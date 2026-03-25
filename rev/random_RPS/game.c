#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

#define TOTAL_ROUNDS 96
#define REQUIRED_WINS 86


void decodeSecretMessage(int wins);

static unsigned int scramble_seed(unsigned int x) {
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return x;
}

static unsigned int get_time_seed(void) {
    struct timespec ts;
    timespec_get(&ts, TIME_UTC);
    unsigned int s = (unsigned int)(ts.tv_sec ^ (ts.tv_nsec / 1000));
    return scramble_seed(s) * 2654435761u;
}

static int elf_choose(void) {
    return (rand() % 3) + 1;
}

static int rps_result(int p, int e) {
    if (p == e) return 0;
    if ((p - e + 3) % 3 == 1) return 1;
    return -1;
}

static const char *move_name(int m) {
    static const char *names[] = {"???", "Rock", "Paper", "Scissors"};
    if (m < 1 || m > 3) return names[0];
    return names[m];
}

static int read_choice(void) {
    for (;;) {
        printf("[R]ock / [P]aper / [S]cissors > ");
        char buf[64];
        if (!fgets(buf, sizeof(buf), stdin)) exit(1);
        if (buf[0] == '1' || buf[0] == 'r' || buf[0] == 'R') return 1;
        if (buf[0] == '2' || buf[0] == 'p' || buf[0] == 'P') return 2;
        if (buf[0] == '3' || buf[0] == 's' || buf[0] == 'S') return 3;
        printf("Invalid. Try again.\n");
    }
}

typedef struct {
    long long val;
    long long base;
    long long mod;
} Accum;

static Accum accum_init(long long mod) {
    Accum a;
    a.mod = mod;
    a.base = rand() % (mod - 2) + 2;
    a.val = 1;
    return a;
}

static void accum_step(Accum *a) {
    a->val = a->val * a->base % a->mod;
}

static long long accum_expect(Accum *a, int steps) {
    long long r = 1;
    for (int i = 0; i < steps; i++) r = r * a->base % a->mod;
    return r;
}

int main(void) {
    unsigned int seed = get_time_seed();

    for (int i = 0; i < 500; i++) {
        printf("\r\033[K%d", i);
        fflush(stdout);
    }
    printf("\033[2J\033[H");

    srand(seed);

    for (int i = 0; i < (seed & 0xFF); i++) rand();

    long long prime = 114743;
    Accum win_acc  = accum_init(prime);
    Accum game_acc = accum_init(prime);

    int wins = 0, losses = 0, draws = 0, round = 0;

    printf("========================================\n");
    printf("   The Elf's Rock-Paper-Scissors Arena  \n");
    printf("========================================\n");
    printf(" Win %d of %d rounds to claim the prize.\n", REQUIRED_WINS, TOTAL_ROUNDS);
    printf("========================================\n\n");

    while (round < TOTAL_ROUNDS && wins < REQUIRED_WINS) {
        if (game_acc.val != accum_expect(&game_acc, round)) {
            printf("Something feels off... the Elf leaves.\n");
            return 1;
        }

        printf("--- Round %d/%d ---\n", round + 1, TOTAL_ROUNDS);
        int player = read_choice();
        int elf = elf_choose();
        int res = rps_result(player, elf);

        printf("  You threw %s, Elf threw %s. ", move_name(player), move_name(elf));

        if (res == 1) {
            printf("You win!\n");
            wins++;
            accum_step(&win_acc);
        } else if (res == -1) {
            printf("Elf wins!\n");
            losses++;
        } else {
            printf("Draw!\n");
            draws++;
        }

        round++;
        accum_step(&game_acc);

        printf("  Score: %dW / %dL / %dD  |  Need %d more wins in %d rounds\n\n",
               wins, losses, draws, REQUIRED_WINS - wins, TOTAL_ROUNDS - round);
    }

    int legit = (wins >= REQUIRED_WINS) && (win_acc.val == accum_expect(&win_acc, wins));

    if (legit) {
        printf("\n*** Congratulations! The Elf bows to your might! ***\n\n");
        decodeSecretMessage(wins);
    } else {
        printf("\nThe Elf grins. Better luck next time.\n");
    }

    return 0;
}

void decodeSecretMessage(int wins) {
    unsigned char encryptedMessage[] = { 100, 63, 193, 96, 50, 6, 237, 182, 28, 206, 198, 241, 19, 226, 157, 239, 211, 40, 225, 32, 193, 157, 117, 32, 25, 58, 214, 168, 239, 254, 207, 180, 131, 106, 223, 189, 102, 178, 155, 24, 201, 213 };
    unsigned char temp_pt[sizeof(encryptedMessage)+1];
    unsigned char pt[sizeof(encryptedMessage)+1];
    unsigned char lookupTable[32] = { 88, 236, 81, 51, 219, 134, 126, 46, 174, 88, 15, 152, 224, 151, 29, 27, 81, 210, 11, 245, 243, 237, 100, 229, 66, 6, 132, 208, 154, 248, 1, 196 };

    for (int i = 1; i < sizeof(encryptedMessage); i++) {
        int prev_value = encryptedMessage[i - 1];
        int current_value = encryptedMessage[i];
        int c = (current_value - lookupTable[prev_value & 0x1f]) & 0xff;
        temp_pt[i - 1] = c;
    }

    for (int i = 0; i < sizeof(encryptedMessage) - 1; i++) {
        int power = 1;
        for (int j = 0; j < i; j++) {
            power = (power * (137 + wins)) % 256;
        }
        pt[i] = (char)((temp_pt[i] * power) % 256);
    }
    
    pt[sizeof(encryptedMessage) - 1] = '\0';
    printf("%s\n", pt);
}
