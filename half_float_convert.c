//Feichen Shen
//Float/half conversion
//avx/f16c CPU support

#include <cstdio>
#include <x86intrin.h>
#include <malloc.h>
#include <stdint.h>

unsigned int buffer_size = 1024*1024;
char mode = 0;

void cpuid(unsigned info, unsigned *eax, unsigned *ebx, unsigned *ecx, unsigned *edx)
{
	*eax = info;
	__asm volatile
	("mov %%ebx, %%edi;" /* 32bit PIC: don't clobber ebx */
	"cpuid;"
	"mov %%ebx, %%esi;"
	"mov %%edi, %%ebx;"
	:"+a" (*eax), "=S" (*ebx), "=c" (*ecx), "=d" (*edx)
	: :"edi");
}

char f16c_support()
{
	unsigned int eax, ebx, ecx, edx;
	cpuid(1, &eax, &ebx, &ecx, &edx);
	return ((ecx & 0x20000000) != 0);
}

typedef uint16_t npy_uint16;
typedef uint32_t npy_uint32;
typedef float v8sf __attribute__ ((vector_size (32)));
typedef long long int v8hf __attribute__ ((vector_size (16)));

npy_uint16 floatbits_to_halfbits(npy_uint32 f);
npy_uint32 halfbits_to_floatbits(npy_uint16 h);

unsigned short FtoH(float value)
{
	return floatbits_to_halfbits(*(npy_uint32 *)(&value));
}

float HtoF(unsigned short value)
{
	npy_uint32 res = halfbits_to_floatbits(*(npy_uint16 *)(&value));
	return *((float *) &res);
}

npy_uint32 halfbits_to_floatbits(npy_uint16 h)
{
    npy_uint16 h_exp, h_man;
    npy_uint32 f_sgn, f_exp, f_man;

    h_exp = (h&0x7c00u);
    f_sgn = ((npy_uint32)h&0x8000u) << 16;
    switch (h_exp) {
        case 0x0000u: /* 0 or denormalized */
            h_man = (h&0x03ffu);
            /* Signed zero */
            if (h_man == 0) {
                return f_sgn;
            }
            /* Denormalized */
            h_man <<= 1;
            while ((h_man&0x0400u) == 0) {
                h_man <<= 1;
                h_exp++;
            }
            f_exp = ((npy_uint32)(127 - 15 - h_exp)) << 23;
            f_man = ((npy_uint32)(h_man&0x03ffu)) << 13;
            return f_sgn + f_exp + f_man;
        case 0x7c00u: /* inf or NaN */
            /* All-ones exponent and a copy of the mantissa */
            return f_sgn + 0x7f800000u + (((npy_uint32)(h&0x03ffu)) << 13);
        default: /* normalized */
            /* Just need to adjust the exponent and shift */
            return f_sgn + (((npy_uint32)(h&0x7fffu) + 0x1c000u) << 13);
    }
}

npy_uint16 floatbits_to_halfbits(npy_uint32 f)
{
    npy_uint32 f_exp, f_man;
    npy_uint16 h_sgn, h_exp, h_man;

    h_sgn = (npy_uint16) ((f&0x80000000u) >> 16);
    f_exp = (f&0x7f800000u);
    
    /* Exponent overflow/NaN converts to signed inf/NaN */
    if (f_exp >= 0x47800000u) {
        if (f_exp == 0x7f800000u) {
            /*
             * No need to generate FP_INVALID or FP_OVERFLOW here, as
             * the float/double routine should have done that.
             */
            f_man = (f&0x007fffffu);
            if (f_man != 0) {
                /* NaN - propagate the flag in the mantissa... */
                npy_uint16 ret = (npy_uint16) (0x7c00u + (f_man >> 13));
                /* ...but make sure it stays a NaN */
                if (ret == 0x7c00u) {
                    ret++;
                }
                return h_sgn + ret;
            } else {
                /* signed inf */
                return (npy_uint16) (h_sgn + 0x7c00u);
            }
        } else {
            /* overflow to signed inf */
#if HALF_GENERATE_OVERFLOW
            generate_overflow_error();
#endif
            return (npy_uint16) (h_sgn + 0x7c00u);
        }
    }
    
    /* Exponent underflow converts to denormalized half or signed zero */
    if (f_exp <= 0x38000000u) {
        /* 
         * Signed zeros, denormalized floats, and floats with small
         * exponents all convert to signed zero halfs.
         */
        if (f_exp < 0x33000000u) {
#if HALF_GENERATE_UNDERFLOW 
            /* If f != 0, we underflowed to 0 */
            if ((f&0x7fffffff) != 0) {
                generate_underflow_error();
            }
#endif
            return h_sgn;
        }
        /* It underflowed to a denormalized value */
#if HALF_GENERATE_UNDERFLOW 
        generate_underflow_error();
#endif
        /* Make the denormalized mantissa */
        f_exp >>= 23;
        f_man = (0x00800000u + (f&0x007fffffu)) >> (113 - f_exp);
        /* Handle rounding by adding 1 to the bit beyond half precision */
#if HALF_ROUND_TIES_TO_EVEN 
        /*
         * If the last bit in the half mantissa is 0 (already even), and
         * the remaining bit pattern is 1000...0, then we do not add one
         * to the bit after the half mantissa.  In all other cases, we do.
         */
        if ((f_man&0x00003fffu) != 0x00001000u) {
            f_man += 0x00001000u;
        }
#else
        f_man += 0x00001000u;
#endif
        h_man = (npy_uint16) (f_man >> 13);
        /*
         * If the rounding causes a bit to spill into h_exp, it will
         * increment h_exp from zero to one and h_man will be zero.
         * This is the correct result.
         */
        return (npy_uint16) (h_sgn + h_man);
    }

    /* Regular case with no overflow or underflow */
    h_exp = (npy_uint16) ((f_exp - 0x38000000u) >> 13);
    /* Handle rounding by adding 1 to the bit beyond half precision */
    f_man = (f&0x007fffffu);
#if HALF_ROUND_TIES_TO_EVEN 
    /*
     * If the last bit in the half mantissa is 0 (already even), and
     * the remaining bit pattern is 1000...0, then we do not add one
     * to the bit after the half mantissa.  In all other cases, we do.
     */
    if ((f_man&0x00003fffu) != 0x00001000u) {
        f_man += 0x00001000u;
    }
#else
    f_man += 0x00001000u;
#endif
    h_man = (npy_uint16) (f_man >> 13);
    /*
     * If the rounding causes a bit to spill into h_exp, it will
     * increment h_exp by one and h_man will be zero.  This is the
     * correct result.  h_exp may increment to 15, at greatest, in
     * which case the result overflows to a signed inf.
     */
#if HALF_GENERATE_OVERFLOW
    h_man += h_exp;
    if (h_man == 0x7c00u) {
        generate_overflow_error();
    }
    return h_sgn + h_man;
#else
    return h_sgn + h_exp + h_man;
#endif
}

void floattohalf(FILE * input, FILE * output, char CPU_support)
{
	float *Buffer = (float*) memalign(32, buffer_size * sizeof(float));
	unsigned short *Out_buffer = (unsigned short*) memalign(32, buffer_size * sizeof(unsigned short));
	unsigned int read_actual = fread(Buffer, sizeof(float), buffer_size, input);
	while (read_actual)
	{
		if (CPU_support)
			for (unsigned int i = 0; i < read_actual; i+=8)
			{
				v8sf v8_in = *((v8sf*) (Buffer + i));
				*((v8hf*) (Out_buffer + i)) = _mm256_cvtps_ph(v8_in, 0);
				//printf("%x\n%x\n%x\n%x\n",Out_buffer[i],Out_buffer[i+1],Out_buffer[i+2],Out_buffer[i+3]);
				//Out_buffer[i] = _cvtss_sh(Buffer[i], 0);
			}
		else
			for (unsigned int i = 0; i < read_actual; i++)
			{
				Out_buffer[i] = FtoH(Buffer[i]);
			}
		fwrite(Out_buffer, 2, read_actual, output);
		read_actual = fread(Buffer, sizeof(float), buffer_size, input);
	}
	free(Out_buffer);
	free(Buffer);
}

void halftofloat(FILE * input, FILE * output, char CPU_support)
{
    unsigned short *Buffer = (unsigned short*) memalign(32, buffer_size * sizeof(unsigned short));
	float *Out_buffer = (float*) memalign(32, buffer_size * sizeof(float));
	unsigned int read_actual = fread(Buffer, sizeof(unsigned short), buffer_size, input);
	
	while (read_actual)
	{
		if (CPU_support)
			for (unsigned int i = 0; i < read_actual; i+=8)
			{
				v8hf v8_in = *((v8hf*) (Buffer + i));
				*((v8sf*) (Out_buffer + i)) = _mm256_cvtph_ps(v8_in);
			}
		else
			for (unsigned int i = 0; i < read_actual; i++)
			{
				Out_buffer[i] = HtoF(Buffer[i]);
			}
		fwrite(Out_buffer, 4, read_actual, output);
		read_actual = fread(Buffer, sizeof(unsigned short), buffer_size, input);
	}
	free(Out_buffer);
	free(Buffer);
}

int main(int argc, char** argv)
{
	char files = 0;
	char input_idx = 0;
	char output_idx = 0;
	for (char k = 0; k < argc; k++)
	{
		if (argv[k][0] == '-'){
			switch (argv[k][1])
			{
				case 'F':
					mode = 'F';
					break;
				case 'H':
					mode = 'H';
					break;
			}
		}
		else {
			if (files == 1) input_idx = k;
			if (files == 2) output_idx = k;
			files++;
		}
	}
	if (!mode) {
		printf("Half float conversion utility\nFeichen Shen\n\nRequire mode option:\n-H (Half to float)\n-F (Float to half)\n");
		printf("\nhalf_float_convert -F float.bin half.bin\n");
		return 1;
	}
	FILE * input_file;
	FILE * output_file;
	if (input_idx) input_file = fopen(argv[input_idx],"rb");
	else input_file = fopen("/dev/fd/0","rb");
	if (output_idx) output_file = fopen(argv[output_idx],"wb");
	else output_file = fopen("/dev/fd/1","wb");

	//Check F16C support
	char F16C = f16c_support();
	//if (F16C) printf("F16C half float supported!\n");
	//Conversion
	if (mode == 'F') floattohalf(input_file, output_file, F16C);
	if (mode == 'H') halftofloat(input_file, output_file, F16C);
	fclose(input_file);
	fclose(output_file);
	return 0;
}
