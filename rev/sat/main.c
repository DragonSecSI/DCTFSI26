#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "sat_data.h"

static uint8_t rol8(uint8_t v, unsigned int r) {
  r &= 7U;
  return (uint8_t)((v << r) | (v >> (8U - r)));
}

static int is_sat_flag(const char *buf) {
  uint8_t x[FLAG_LEN] = {0};
  memcpy(x, buf, FLAG_LEN);

  for (int i = 0; i < PREFIX_LEN; ++i) {
    if (x[i] != KNOWN_PREFIX[i]) {
      return 0;
    }
  }

  if (x[FLAG_LEN - 1] != LAST_BYTE) {
    return 0;
  }

  for (size_t i = 0; i < sizeof(C1); ++i) {
    uint8_t expr = (uint8_t)(7U * x[i] + 11U * x[i + 1] + 13U * x[i + 2] +
                             17U * x[i + 3] + 19U * (uint8_t)i);
    if (expr != C1[i]) {
      return 0;
    }
  }

  uint8_t exprs[5] = {0};

  for (size_t i = 0; i < sizeof(C2); ++i) {
    uint8_t expr =
        (uint8_t)(rol8(x[i], 1) ^ rol8(x[i + 1], 2) ^ rol8(x[i + 2], 3) ^
                  x[i + 3] ^ (uint8_t)(x[i + 4] + (uint8_t)(7U * (uint8_t)i)));
    if (expr != C2[i]) {
      return 0;
    }
  }

  for (size_t i = 0; i < sizeof(C3); ++i) {
    int j = (i * 7 + 3) % FLAG_LEN;
    int k = (i * 11 + 5) % FLAG_LEN;
    uint8_t expr =
        (uint8_t)((uint8_t)(x[i] + x[j]) ^ (uint8_t)(3U * x[k] + (uint8_t)i));
    if (expr != C3[i]) {
      return 0;
    }
  }

  for (size_t i = 0; i < sizeof(C4); ++i) {
    uint8_t rot = (uint8_t)((i % 7) + 1);
    uint8_t expr = (uint8_t)(rol8(x[i], rot) + (uint8_t)(x[i + 1] ^ x[i + 3]) +
                             3U * x[i + 2] + 5U * x[i + 4] + 7U * x[i + 5] +
                             13U * (uint8_t)i);
    if (expr != C4[i]) {
      return 0;
    }
  }

  for (size_t i = 0; i < sizeof(C5); ++i) {
    int j = (i * 5 + 1) % FLAG_LEN;
    int k = (i * 9 + 2) % FLAG_LEN;
    int t = (i + 3) % FLAG_LEN;
    int p = (i + 4) % FLAG_LEN;
    uint8_t expr = (uint8_t)((x[i] & x[j]) ^ (x[k] | x[t]) ^ (uint8_t)(~x[p]));
    if (expr != C5[i]) {
      return 0;
    }
  }

  uint8_t acc1 = 0;
  for (int i = 0; i < FLAG_LEN; ++i) {
    acc1 = (uint8_t)(acc1 + (uint8_t)((17U * (uint8_t)i + 3U) * x[i]));
  }
  if (acc1 != G1) {
    return 0;
  }

  uint8_t acc2 = 0;
  for (int i = 0; i < FLAG_LEN; ++i) {
    acc2 = (uint8_t)(acc2 ^ rol8(x[i], (unsigned int)((i % 5) + 1)));
  }
  if (acc2 != G2) {
    return 0;
  }

  return 1;
}

int main(void) {
  char buf[256];

  printf("Enter flag: ");

  if (!fgets(buf, sizeof(buf), stdin)) {
    return 1;
  }

  size_t n = strcspn(buf, "\n");
  if (n > 0) {
    buf[n] = '\0';
  }

  if (strlen(buf) != FLAG_LEN || !is_sat_flag(buf)) {
    puts("Try again");
    return 1;
  }

  printf("Correct! Flag: %s\n", buf);
  return 0;
}
