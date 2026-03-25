#include <stdio.h>
#include <string.h>

#define FLAG_LENGTH "flag_length"

const char FLAG[] = "flag";
const char KEY[] = "key";
unsigned int MAGIC_A = 0xDEADC0DE;
unsigned int MAGIC_B = 0x42;
unsigned int STEP = 3;

/*
 * Encrypts a plaintext string in-place.
 * string length must be equal to the flag length
 * if it's not there WILL be an oopsie
 * Args
 *  char*:  plaintext string
 */
void encrypt(char* pt) {
    for(int i = 0; i < FLAG_LENGTH; i++) {
        pt[i] = (((pt[i] ^ KEY[i]) + MAGIC_A - (i * STEP)) ^ MAGIC_B);
    }
}

int check_flag(char* inp) {
    encrypt(inp);
    return memcmp(inp, FLAG, FLAG_LENGTH) == 0;
}

int main(int argc, char* argv) {
    puts("What is the flag?");
    char inp[64];
    fgets(inp, sizeof inp, stdin);
    inp[strcspn(inp, "\n")] = 0;
    if(strlen(inp) == FLAG_LENGTH && check_flag(inp)) {
        puts("Correct! You got the flag!");
    }
    else {
        puts("Try again...");
    }
}
