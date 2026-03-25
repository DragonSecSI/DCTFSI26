#include <iostream>
#include <cstdint>

int debug = 0;

#define REGSIZE 4
#define REGCHECK(reg) if (reg < 0 || reg >= REGSIZE) { \
	std::cout << "Invalid register: " << (int)reg << std::endl; \
	exit(1); \
} 

long syscall_read(size_t* rsp)
{
  char c;
	if (std::cin.get(c)) {
		return ((long)c) & 0xFF;
	} else {
		return -1; // EOF
	}
}

long syscall_write(size_t* rsp)
{
	char c = (char)(*rsp & 0xFF);
	std::cout << c;
	return 0;
}

long syscall_exit(size_t* rsp)
{
	exit(0);
}

class VM
{
	private:
		uint8_t* program;
		size_t program_size;

		size_t regs[REGSIZE];
		uint8_t *rip;
		size_t *rsp;

		long (*syscalls[3])(size_t* rsp) = {syscall_read, syscall_write, syscall_exit};

		size_t stack[1024];

	public:
		void setup(uint8_t* program, size_t program_size)
		{
			this->program = program;
			this->program_size = program_size;

			for (int i = 0; i < REGSIZE; i++) {
				regs[i] = 0;
			}

			this->rip = (uint8_t*)program;
			this->rsp = this->stack + 1000;
		}
		void run()
		{
			while (true)
			{
				if (rip < program || rip >= program + program_size) {
					std::cout << "Invalid instruction pointer" << std::endl;
					exit(1);
				}
				if (rsp < stack || rsp >= stack + 1024) {
					std::cout << "Invalid stack pointer" << std::endl;
					exit(1);
				}

				uint8_t opcode = *rip++;
				if (debug)
					printf("[DEBUG] Opcode: 0x%02X, RIP: %p, RSP: %p\n", opcode, rip, rsp);
				switch (opcode) {
					case 0x00: // NOP
						break;
					case 0x01: // ADD reg, reg
						{
							uint8_t reg1 = *rip++;
							uint8_t reg2 = *rip++;
							REGCHECK(reg1);
							REGCHECK(reg2);
							regs[reg1] += regs[reg2];
						}
						break;
					case 0x02: // SUB reg, reg
						{
							uint8_t reg1 = *rip++;
							uint8_t reg2 = *rip++;
							REGCHECK(reg1);
							REGCHECK(reg2);
							regs[reg1] -= regs[reg2];
						}
						break;
				  case 0x03: // MUL reg, reg
						{
							uint8_t reg1 = *rip++;
							uint8_t reg2 = *rip++;
							REGCHECK(reg1);
							REGCHECK(reg2);
							regs[reg1] *= regs[reg2];
						}
						break;
					case 0x04: // DIV reg, reg
						{
							uint8_t reg1 = *rip++;
							uint8_t reg2 = *rip++;
							REGCHECK(reg1);
							REGCHECK(reg2);
							regs[reg1] /= regs[reg2];
						}
						break;
					case 0x05: // MOD reg, reg
						{
							uint8_t reg1 = *rip++;
							uint8_t reg2 = *rip++;
							REGCHECK(reg1);
							REGCHECK(reg2);
							regs[reg1] %= regs[reg2];
						}
						break;
					case 0x06: // PUSH reg
						{
							uint8_t reg = *rip++;
							REGCHECK(reg);
							*--rsp = regs[reg] & 0xFF;
						}
						break;
					case 0x07: // POP reg
						{
							uint8_t reg = *rip++;
							REGCHECK(reg);
							regs[reg] = *rsp++;
						}
						break;
					case 0x08: // PUSH imm
						{
							size_t imm = *((size_t*)rip);
							rip += sizeof(size_t);
							*--rsp = imm;
						}
						break;
					case 0x09: // MOV reg, reg
						{
							uint8_t reg1 = *rip++;
							uint8_t reg2 = *rip++;
							REGCHECK(reg1);
							REGCHECK(reg2);
							regs[reg1] = regs[reg2];
						}
						break;
					case 0x0A: // MOV reg, imm
						{
							uint8_t reg = *rip++;
							REGCHECK(reg);
							size_t imm = *((size_t*)rip);
							rip += sizeof(size_t);
							regs[reg] = imm;
						}
						break;
					case 0x0B: // SHL reg, imm
						{
							uint8_t reg = *rip++;
							REGCHECK(reg);
							uint8_t imm = *rip++;
							regs[reg] <<= imm;
						}
						break;
					case 0x0C: // SHR reg, imm
						{
							uint8_t reg = *rip++;
							REGCHECK(reg);
							uint8_t imm = *rip++;
							regs[reg] >>= imm;
						}
						break;
					case 0x0D: // AND reg, reg
						{
							uint8_t reg1 = *rip++;
							uint8_t reg2 = *rip++;
							REGCHECK(reg1);
							REGCHECK(reg2);
							regs[reg1] &= regs[reg2];
						}
						break;
					case 0x0E: // OR reg, reg
						{
							uint8_t reg1 = *rip++;
							uint8_t reg2 = *rip++;
							REGCHECK(reg1);
							REGCHECK(reg2);
							regs[reg1] |= regs[reg2];
						}
						break;
					case 0x0F: // SYSCALL imm
						{
							int8_t imm = *rip++;
							regs[0] = syscalls[imm](rsp);
						}
						break;
					default:
						std::cout << "Invalid opcode: " << std::hex << (int)opcode << std::dec << std::endl;
						exit(1);
				}
			}
		}
} vm;

int main()
{
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);

	int n = 0;
	std::cin >> n;
	std::cin.ignore(); // ignore the newline after the number

	if (n <= 0 || n > 10240) {
		std::cout << "Invalid program size" << std::endl;
		return 1;
	}

	uint8_t* program = new uint8_t[n];
	std::cin.read((char*)program, n);
	std::cin.ignore(); // ignore the newline after the program

	vm.setup(program, n);
	vm.run();

	return 0;
}
