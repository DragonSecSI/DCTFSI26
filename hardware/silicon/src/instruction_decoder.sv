typedef enum logic [3:0] {
    OP_NOP    = 4'b0000,
    OP_ADD    = 4'b0001,
    OP_SUB    = 4'b0010,
    OP_AND    = 4'b0011,
    OP_OR     = 4'b0100,
    OP_XOR    = 4'b0101,
    OP_NOT    = 4'b0110,
    OP_SHIFTL = 4'b0111,
    OP_SHIFTR = 4'b1000,
    OP_JMP    = 4'b1001,
    OP_JMPEQ  = 4'b1010,
    OP_JMPL   = 4'b1011,
    OP_CMP    = 4'b1100,
    OP_MOVM   = 4'b1101,
    OP_LOADM  = 4'b1110,
    OP_LOADL  = 4'b1111
} opcode_t;

module decoder (
    input  logic [31:0] instruction,
    output opcode_t opcode,
    output logic [7:0] addr1,
    output logic [7:0] addr2,
    output logic [7:0] addr3,
    output logic       illegal
);
    assign opcode  = opcode_t'(instruction[31:28]);
    assign addr1   = instruction[27:20];
    assign addr2   = instruction[19:12];
    assign addr3   = instruction[11:4];
    assign illegal = 1'b0;
endmodule