`include "alu/adder.sv"
`timescale 1ns / 1ns

typedef enum logic [3:0] {
    ALU_ADD  = 4'b0000,
    ALU_SUB  = 4'b0001,
    ALU_AND  = 4'b0010,
    ALU_OR   = 4'b0011,
    ALU_XOR  = 4'b0100,
    ALU_NOT  = 4'b0101
} alu_ctrl_t;

typedef enum logic [3:0] {
    FLAG_ZERO     = 4'b0001,
    FLAG_OVERFLOW = 4'b0010,
    FLAG_EQUAL    = 4'b0100,
    FLAG_LESS     = 4'b1000
} alu_flags_t;


module alu(A, B, Control, Result, Flags);
    input [31:0] A, B;
    input alu_ctrl_t Control;

    output [31:0] Result;
    output [3:0] Flags;

    wire [31:0] adder_result;
    wire adder_carry_out;

    adder adder_inst(A, B, adder_result, Control[2:0], adder_carry_out);

    assign Flags[0] = (adder_result == 32'b0) ? 1'b1 : 1'b0; // ZERO flag
    assign Flags[1] = adder_carry_out; // OVERFLOW flag
    assign Flags[2] = (!adder_carry_out && (adder_result == 32'b0)) ? 1'b1 : 1'b0; // EQUAL flag
    assign Flags[3] = (adder_carry_out && (adder_result != 32'b0)) ? 1'b1 : 1'b0; // LESS flag
    assign Result = adder_result;

endmodule