# Operation process

- Fetch
- Decode
- Execute
- Memory

# Registers

## GPRs (General pourpose registers)

### General pourpose dual read registers

| Name | Width |
|------|-------|
| gp0  | 32    |
| gp1  | 32    |
| gp2  | 32    |
| gp3  | 32    |
| gp4  | 32    |
| gp5  | 32    |
| gp6  | 32    |
| gp7  | 32    |

### Special registers

| Name | Width |
|------|-------|
| sp   | 16    |
| bp   | 16    |
| ip   | 16    |


### Hidden registers (Inaccassible to ops)

| Name | Width |
| ---- | ----- |
| flags| 4     |


# Instruction set

| Opcode | Mnemonic | Bit representation | Description |
| ------ | -------- | ------------------ | ----------- |
| NOP    | No op    |  0000              | No operation |
| ADD    | Addition |  0001              | Add R1 to R2 save to R3 |
| SUB    | Subtract |  0010              | Sub R1 from R2 save to R3 |
| AND    | And      |  0011              | Bitwise AND R1 and R2, save to R3 |
| OR     | Or       |  0100              | Bitwise OR R1 and R2, save to R3 |
| XOR    | Xor      |  0101              | Bitwise XOR R1 and R2, save to R3 |
| NOT    | Not      |  0110              | Bitwise NOT R1, save to R3        |
| SHIFTL | Shift left | 0111             | Bitwise left shift in R2 into R1 |
| SHIFTR | Shift Right | 1000            | Bitwise right shift R2 into R1 |
| JMP    | Jump |      | 1001            | Unconditional jump |
| JMPEQ  | Jump equal  | 1010            | Jump if R1 and R2 were equal |
| JMPL   | Jump Less   | 1011            | Jump if R1 is less than R2 |
| CMP    | Compare     | 1100            | Compare R1 and R2 | 
| MOVM   | Move to Mem | 1101            | Move R1 to Mem R2-R3 | 
| LOADM  | Load to reg  | 1110           | Move Mem R2-R3 to R1 |
| LOADL  | Load literal | 1111          | Load literal to R1   |


## Instruction format

| 4 bit opcode | 8 bit addr1 | 8 bit addr2 | 8 bit addr3 |

## Memory mapped output

- Data memory is byte addressed (`0x00`-`0xFF`) for `MOVM`/`LOADM`.
- Address `0xFE` is reserved as MMIO input.
- Address `0xFF` is reserved as MMIO output.
- Executing `LOADM` with `addr2 = 0xFE` reads the external input value (`io_in`) when `io_in_valid` is high.
- Executing `MOVM` with `addr2 = 0xFF` emits the value of `addr1` register on the CPU output port (`io_out`) with a one-cycle pulse on `io_valid`.


# Compile

```
verilator --binary --timing --sv -Wall --Wno-WIDTHEXPAND --Wno-WIDTHTRUNC --Wno-INITIALDLY --Wno-CASEINCOMPLETE --Wno-EOFNEWLINE --Wno-DECLFILENAME --Wno-UNUSEDSIGNAL -o Vserver_tb server_tb.sv 2>&1 | tail -8
```
