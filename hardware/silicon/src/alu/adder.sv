`timescale 1ns / 1ns

typedef enum logic [2:0] {
    ADDER_ADD  = 3'b000,
    ADDER_SUB  = 3'b001,
    ADDER_AND  = 3'b010,
    ADDER_OR   = 3'b011,
    ADDER_XOR  = 3'b100,
    ADDER_NOT  = 3'b101
} adder_ctrl_t;

/*
    Used for flags by cpu: 
    A sub B = C, Cout
    If Cout = 1, then A < B
    If Cout = 0, then A >= B
*/

module adder (A, B, Result, Control, Cout);
    input [31:0] A, B;
    output [31:0] Result;
    input adder_ctrl_t Control;
    output Cout;

    reg Cin;
    reg [32:0] A_Full;
    reg [32:0] B_Full;
    reg [32:0] Res_Full;

    wire add_c = (Control == ADDER_ADD);
    wire sub_c = (Control == ADDER_SUB);
    wire and_c = (Control == ADDER_AND);
    wire or_c  = (Control == ADDER_OR);
    wire xor_c = (Control == ADDER_XOR);
    wire not_c = (Control == ADDER_NOT);


    always @(*) begin
        assign A_Full = {1'b0, A};
        assign B_Full = {1'b0, B};

        if (sub_c) begin
            B_Full = ~B_Full;
            Cin = 1'b1;
            assign Res_Full = A_Full + B_Full + {31'b0, Cin};
        end 
        else if (add_c) begin
            Cin = 1'b0;
            assign Res_Full = A_Full + B_Full + {31'b0, Cin};
        end
        else if (and_c) begin
            Cin = 1'b0;
            assign Res_Full = A_Full & B_Full;
        end
        else if (or_c) begin
            assign Res_Full = A_Full | B_Full;
            Cin = 1'b0;
        end
        else if (xor_c) begin
            assign Res_Full = A_Full ^ B_Full;
            Cin = 1'b0;
        end
        else if (not_c) begin
            assign Res_Full = ~A_Full;
            Cin = 1'b0;
        end
        else begin
            B_Full = B_Full;
            Cin = 1'b0;
            assign Res_Full = 1337;
        end
    end

    assign Cout = Res_Full[32];
    assign Result = Res_Full[31:0];
endmodule