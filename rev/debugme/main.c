#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "generated_data.h"

static uint64_t rotl64(uint64_t x, unsigned int r) {
	return (x << r) | (x >> (64U - r));
}

static uint64_t derive_seed(void) {
	size_t i;
	uint64_t acc = 0x6A09E667F3BCC909ULL;

	for (i = 0; i < sizeof(k_parts) / sizeof(k_parts[0]); ++i) {
		acc ^= rotl64(k_parts[i] + (uint64_t)i * 0x9E3779B97F4A7C15ULL,
					  (unsigned int)((i * 11U + 7U) & 63U));
		acc *= 0xD6E8FEB86659FD93ULL;
		acc ^= acc >> 27U;
		acc = rotl64(acc, 17U);
	}

	return acc;
}

static unsigned char keystream_byte(uint64_t seed, uint64_t nonce, size_t i) {
	size_t r;
	size_t block = i / 8U;
	size_t lane = i % 8U;
	unsigned int shift = (unsigned int)((lane * 13U) & 63U);
	uint64_t x = seed ^ (nonce + (uint64_t)block * 0x9E3779B97F4A7C15ULL);

	for (r = 0; r < 10U; ++r) {
		x ^= rotl64(x, 7U);
		x *= 0xD6E8FEB86659FD93ULL;
		x ^= x >> 17U;
		x += 0xA5A5A5A5A5A5A5A5ULL ^ ((uint64_t)r * 0x123456789ULL);
	}

	return (unsigned char)(((x >> shift) & 0xFFU) ^ ((0x5AU + (lane * 17U)) & 0xFFU));
}

static void crypt_buf(unsigned char *buf, size_t len, uint64_t seed, uint64_t nonce) {
	size_t i;

	for (i = 0; i < len; ++i) {
		buf[i] ^= keystream_byte(seed, nonce, i);
	}
}

int main(void) {
	char input[128];
	uint64_t seed = derive_seed();
	unsigned char pass_buf[sizeof(enc_pass)];
	unsigned char flag_buf[sizeof(enc_flag)];

	memcpy(pass_buf, enc_pass, sizeof(enc_pass));
	memcpy(flag_buf, enc_flag, sizeof(enc_flag));

	crypt_buf(pass_buf, sizeof(pass_buf), seed, pass_nonce);
	crypt_buf(flag_buf, sizeof(flag_buf), seed, flag_nonce);

	puts("Input access token:");

	if (fgets(input, sizeof(input), stdin) == NULL) {
		return 1;
	}

	uint64_t nl = strcspn(input, "\n");
	if (nl < sizeof(input)) {
		input[nl] = '\0';
	}

	if (strcmp(input, (const char *)pass_buf) != 0) {
		puts("nope");
		return 1;
	}

	puts((const char *)flag_buf);
	return 0;
}
