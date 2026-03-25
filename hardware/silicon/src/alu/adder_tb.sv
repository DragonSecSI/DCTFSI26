`timescale 1ns / 1ns
`include "alu/adder.sv"

module alu_tb;


reg [31:0] A;
reg [31:0] B;

reg [31:0] Result;
reg Cin;
wire Cout;

alu_ctrl_t Control;

adder adder_inst(A, B, Result, Control, Cout);

initial begin
    A = 32'h0000_0001;
    B = 32'h0000_0002;
    Cin = 1'b0;

    Control = ALU_ADD;    

    #10;

    $display("ADD ->A: %h, B: %h, Result: %h, Cin: %b, Cout: %b", A, B, Result, Control, Cout);

    A = 32'hFFFF_FFFF;
    B = 32'h0000_0001;

    #10;

    $display("ADD -> A: %h, B: %h, Result: %h, Cin: %b, Cout: %b", A, B, Result, Control, Cout);

    Control = ALU_SUB;
    A = 32'h0000_0003;
    B = 32'h0000_0002;

    #10;
    $display("SUB  -> A: %h, B: %h, Result: %h, Cin: %b, Cout: %b", A, B, Result, Control, Cout);

    Control = ALU_SUB;
    A = 32'h0000_0001;
    B = 32'h0000_0002;

    #10;
    $display("SUB  -> A: %h, B: %h, Result: %h, Cin: %b, Cout: %b", A, B, Result, Control, Cout);

    // try other ALU controls
    A = 32'hF0F0_F0F0;
    B = 32'h0F0F_0F0F;
    Control = ALU_AND;
    #10;
    $display("AND  -> A:%h B:%h Result:%h Control:%0d Cout:%b", A, B, Result, Control, Cout);

    Control = ALU_OR;
    #10;
    $display("OR   -> A:%h B:%h Result:%h Control:%0d Cout:%b", A, B, Result, Control, Cout);

    Control = ALU_XOR;
    #10;
    $display("XOR  -> A:%h B:%h Result:%h Control:%0d Cout:%b", A, B, Result, Control, Cout);

    Control = ALU_NOT;
    #10;
    $display("NOT  -> A:%h B:%h Result:%h Control:%0d Cout:%b", A, B, Result, Control, Cout);

    $finish;
end

endmodule