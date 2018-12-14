//Feichen Shen
//Float/half conversion
//avx/f16c CPU support


#include "malloc.h"
#include "stdint.h"
#include "stdio.h"
#include "string.h"
#include "x86intrin.h"


#define buffer_size 1024*1024

typedef FILE* file_handle;

file_handle binary_input_handles[256];
FILE * output_file;
int input_count = 0;

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
typedef float v4sf __attribute__ ((vector_size (16)));
typedef float v8sf __attribute__ ((vector_size (32)));
typedef unsigned short v8hf __attribute__ ((vector_size (16)));

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



void Combine_depth_half()
{
	//Alignment for 256bit AVX register
	v8hf * Sum = (v8hf*) memalign(32, buffer_size * sizeof(v8hf));
	v8sf * intermediate = (v8sf*) memalign(32, buffer_size * sizeof(v8sf));
	v8hf * buffer = (v8hf*) memalign(32, buffer_size * sizeof(v8hf));
	float * intermediate_hf = (float *) intermediate;
	//char cpu_support = f16c_support(); //F16C comes later than AVX
	char read_fail = 1;
	while (read_fail)
	{
		int actual_size = 0;
		memset(intermediate, 0, buffer_size << 5); //8x float
		for (int f_idx = 0; f_idx < input_count; f_idx++)
		{
			//Read as half float x8 ( << 3)
			actual_size = fread(buffer, sizeof(unsigned short), buffer_size << 3, binary_input_handles[f_idx]);
			//if (cpu_support) {
			//	for (int k = 0; k < (actual_size + 7) >> 3; k++) {
			//		intermediate[k] += _mm256_cvtph_ps(buffer[k]);
			//	}
			// }
			//else {
				unsigned short * buffer_hf = (unsigned short *) buffer;
				for (int k = 0; k < actual_size; k++){
					intermediate_hf[k] += HtoF(buffer_hf[k]);
				}
			// }
		}
		//Result to half float
		//if (cpu_support) {
		//	for (int k = 0; k < (actual_size + 7) >> 3; k++) Sum[k] = _mm256_cvtps_ph(intermediate[k], 0);
		// }
		//else {
			unsigned short * Sum_hf = (unsigned short *) Sum;
			for (int k = 0; k < actual_size; k++) Sum_hf[k] = FtoH(intermediate_hf[k]);
		// }
		//Dump to output
		if (actual_size) fwrite(Sum, sizeof(unsigned short), actual_size, output_file);
		else read_fail = 0;
	}
	free(Sum);
	free(intermediate);
	free(buffer);
}

void Combine_depth_float()
{
	v4sf * Sum = (v4sf*) memalign(32, buffer_size * sizeof(v4sf));
	v4sf * buffer = (v4sf*) memalign(32, buffer_size * sizeof(v4sf));
	char read_fail = 1;
	while (read_fail)
	{
		int actual_size = 0;
		memset(Sum, 0, buffer_size << 4);
		for (int f_idx = 0; f_idx < input_count; f_idx++)
		{
			actual_size = fread(buffer, sizeof(float), buffer_size << 2, binary_input_handles[f_idx]);
			//Add to sum
			for (int k = 0; k < (actual_size + 3) >> 2; k++) //4 float at a time
			{
				Sum[k] += buffer[k];
			}
		}
		//Dump to output
		if (actual_size) fwrite(Sum, sizeof(float), actual_size, output_file);
		else read_fail = 0;
	}
	free(Sum);
	free(buffer);
}

int main(int argc, char** argv)
{
	char files = 0;
	char input_argv = 0;
	char output_argv = 0;
	char skip_argument = 0;
	char half_float = 0;
	for (char k = 1; k < argc; k++)
	{
		if (skip_argument)
		{
			skip_argument = 0;
			continue;
		}
		if (argv[k][0] == '-'){
			switch (argv[k][1])
			{
				case 'L':
					input_argv = k + 1;
					skip_argument = 1;
					break;
				case 'o':
					output_argv = k + 1;
					skip_argument = 1;
					break;
				case 'H':
					half_float = 1;
					break;
			}
		}
		else input_count++;
	}
	if (!input_argv && input_count < 2)
	{
		printf("Less than 2 file specified\n");
		return 1;
	}
	//File list
	if (input_argv)
	{
		FILE * input_file;
		input_file = fopen(argv[input_argv],"rb");
		char buffer_str[65535];
		while (fgets(buffer_str, 65535, input_file)) {
			binary_input_handles[input_count] = fopen(buffer_str, "rb");
			input_count++;
		}
		fclose(input_file);
	}
	else {
		//No listing
		char handle_idx = 0;
		for (int k = argc - 1; k >= argc - input_count; k--)
		{
			binary_input_handles[handle_idx] = fopen(argv[k],"rb");
			handle_idx++;
		}
	}
	//Output file
	if (output_argv) output_file = fopen(argv[output_argv],"wb");
	else output_file = fopen("/dev/fd/1","wb");
	if (half_float) Combine_depth_half();
	else Combine_depth_float();
	fclose(output_file);
	return 0;
}
