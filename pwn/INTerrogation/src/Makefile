# c99 needed to use gets
../app: main.c
	gcc $^ -std=c99 -no-pie -fno-stack-protector -Wl,-z,relro,-z,lazy -o $@
