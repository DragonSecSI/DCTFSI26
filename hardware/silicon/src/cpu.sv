`timescale 1ns / 1ns
`include "alu/alu.sv"
`include "instruction_decoder.sv"

module cpu (
    input logic clk,
    input logic reset,
    input logic program_mode,
    input logic [31:0] instruction_in,
    input logic io_in_valid,
    input logic [31:0] io_in,
    output logic [31:0] result_out,
    output logic [3:0] flags_out,
    output logic [31:0] pc_out,
    output logic io_valid,
    output logic [31:0] io_out
);

logic [31:0] gpr [7:0];
logic [3:0] flags;
logic [31:0] pc;
logic [31:0] pc_next;
logic [31:0] current_instruction;

logic [31:0] instr_mem [0:255];
logic [31:0] data_mem [0:255];

opcode_t opcode;
logic [7:0] addr1;
logic [7:0] addr2;
logic [7:0] addr3;
logic illegal;

logic [31:0] alu_a;
logic [31:0] alu_b;
logic [31:0] alu_result;
logic [3:0] alu_flags;
logic [7:0] mem_addr;

alu_ctrl_t alu_control;
localparam logic [7:0] MMIO_OUT_ADDR = 8'hFF;
localparam logic [7:0] MMIO_IN_ADDR = 8'hFE;

decoder decoder_inst (
    .instruction(current_instruction),
    .opcode(opcode),
    .addr1(addr1),
    .addr2(addr2),
    .addr3(addr3),
    .illegal(illegal)
);

always_comb begin
    current_instruction = program_mode ? instr_mem[pc[7:0]] : instruction_in;
    mem_addr = addr2;
    pc_next = pc;

    if (program_mode) begin
        pc_next = pc + 32'd1;
    end

    unique case (opcode)
        OP_JMP: begin
            pc_next = {24'b0, addr1};
        end
        OP_JMPEQ: begin
            if (flags[2]) begin  // FLAG_EQUAL bit - only set by arithmetic ops, NOT by CMP
                pc_next = {24'b0, addr3};
            end
        end
        OP_JMPL: begin
            if (flags[3]) begin  // FLAG_LESS bit - only set by arithmetic ops, NOT by CMP
                pc_next = {24'b0, addr3};
            end
        end
        default: begin
            pc_next = pc_next;
        end
    endcase

    alu_a = gpr[addr1[2:0]];
    alu_b = gpr[addr2[2:0]];

    unique case (opcode)
        OP_ADD: alu_control = ALU_ADD;
        OP_SUB: alu_control = ALU_SUB;
        OP_AND: alu_control = ALU_AND;
        OP_OR:  alu_control = ALU_OR;
        OP_XOR: alu_control = ALU_XOR;
        OP_NOT: alu_control = ALU_NOT;
        OP_CMP: alu_control = ALU_SUB;
        default: alu_control = ALU_ADD;
    endcase
end

alu alu_inst (
    .A(alu_a),
    .B(alu_b),
    .Control(alu_control),
    .Result(alu_result),
    .Flags(alu_flags)
);

always_ff @(posedge clk or posedge reset) begin
    if (reset) begin
        integer i;
        for (i = 0; i < 8; i = i + 1) begin
            gpr[i] <= 32'b0;
        end
        flags <= 4'b0;
        result_out <= 32'b0;
        pc <= 32'b0;
        io_valid <= 1'b0;
        io_out <= 32'b0;
    end else if (!illegal) begin
        io_valid <= 1'b0;
        pc <= pc_next;

        unique case (opcode)
            OP_ADD, OP_SUB, OP_AND, OP_OR, OP_XOR, OP_NOT: begin
                gpr[addr3[2:0]] <= alu_result;
                flags <= alu_flags;
                result_out <= alu_result;
            end
            OP_CMP: begin
                flags[1:0] <= alu_flags[1:0];  // only updates ZERO and OVERFLOW
                result_out <= alu_result;
            end
            OP_LOADL: begin
                gpr[addr1[2:0]] <= {24'b0, addr2};
                result_out <= {24'b0, addr2};
            end
            OP_MOVM: begin
                data_mem[mem_addr] <= gpr[addr1[2:0]];
                result_out <= gpr[addr1[2:0]];

                if (mem_addr == MMIO_OUT_ADDR) begin
                    io_valid <= 1'b1;
                    io_out <= gpr[addr1[2:0]];
                end
            end
            OP_LOADM: begin
                if (mem_addr == MMIO_IN_ADDR) begin
                    if (io_in_valid) begin
                        gpr[addr1[2:0]] <= io_in;
                        result_out <= io_in;
                    end else begin
                        gpr[addr1[2:0]] <= 32'b0;
                        result_out <= 32'b0;
                    end
                end else begin
                    gpr[addr1[2:0]] <= data_mem[mem_addr];
                    result_out <= data_mem[mem_addr];
                end
            end
            default: begin
                result_out <= result_out;
            end
        endcase
    end
end

assign flags_out = flags;
assign pc_out = pc;

endmodule