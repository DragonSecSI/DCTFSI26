#include <stdio.h>

int main()
{
	char buf[0x40];
	puts("Huh?! I would never tell \"you\" where my libc is!! You better just kill -11 me now...");
	gets(buf);
}
