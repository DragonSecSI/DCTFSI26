`timescale 1ns / 1ns
`include "cpu.sv"

module cpu_tb;
    localparam logic [3:0] OP_NOP    = 4'b0000;
    localparam logic [3:0] OP_ADD    = 4'b0001;
    localparam logic [3:0] OP_SUB    = 4'b0010;
    localparam logic [3:0] OP_AND    = 4'b0011;
    localparam logic [3:0] OP_OR     = 4'b0100;
    localparam logic [3:0] OP_XOR    = 4'b0101;
    localparam logic [3:0] OP_NOT    = 4'b0110;
    localparam logic [3:0] OP_CMP    = 4'b1100;
    localparam logic [3:0] OP_MOVM   = 4'b1101;
    localparam logic [3:0] OP_LOADM  = 4'b1110;
    localparam logic [3:0] OP_LOADL  = 4'b1111;

    logic clk;
    logic reset;
    logic [31:0] instruction;
    logic [31:0] result_out;
    logic [3:0] flags_out;
    logic [31:0] pc_out;
    logic io_in_valid;
    logic [31:0] io_in;
    logic io_valid;
    logic [31:0] io_out;

    integer test_count;
    integer pass_count;
    integer fail_count;

    cpu dut (
        .clk(clk),
        .reset(reset),
        .program_mode(1'b0),
        .instruction_in(instruction),
        .io_in_valid(io_in_valid),
        .io_in(io_in),
        .result_out(result_out),
        .flags_out(flags_out),
        .pc_out(pc_out),
        .io_valid(io_valid),
        .io_out(io_out)
    );

    function automatic [31:0] enc_instr(
        input logic [3:0] op,
        input logic [7:0] a1,
        input logic [7:0] a2,
        input logic [7:0] a3
    );
        enc_instr = {op, a1, a2, a3, 4'b0000};
    endfunction

    task automatic issue(input logic [31:0] instr);
        begin
            instruction = instr;
            @(posedge clk);
            #1;
        end
    endtask

    task automatic check_result(
        input logic [31:0] expected,
        input [80*8-1:0] name
    );
        begin
            test_count = test_count + 1;
            if (result_out === expected) begin
                pass_count = pass_count + 1;
                $display("PASS: %s -> result=%h", name, result_out);
            end else begin
                fail_count = fail_count + 1;
                $display("FAIL: %s", name);
                $display("      expected=%h got=%h", expected, result_out);
            end
        end
    endtask

    task automatic check_flags(
        input logic [3:0] expected,
        input [80*8-1:0] name
    );
        begin
            test_count = test_count + 1;
            if (flags_out === expected) begin
                pass_count = pass_count + 1;
                $display("PASS: %s -> flags=%b", name, flags_out);
            end else begin
                fail_count = fail_count + 1;
                $display("FAIL: %s", name);
                $display("      expected=%b got=%b", expected, flags_out);
            end
        end
    endtask

    task automatic check_io(
        input logic expected_valid,
        input logic [31:0] expected_out,
        input [80*8-1:0] name
    );
        begin
            test_count = test_count + 1;
            if (io_valid === expected_valid && io_out === expected_out) begin
                pass_count = pass_count + 1;
                $display("PASS: %s -> io_valid=%b io_out=%h", name, io_valid, io_out);
            end else begin
                fail_count = fail_count + 1;
                $display("FAIL: %s", name);
                $display("      expected io_valid=%b io_out=%h", expected_valid, expected_out);
                $display("      got      io_valid=%b io_out=%h", io_valid, io_out);
            end
        end
    endtask

    always #5 clk = ~clk;

    initial begin
        clk = 1'b0;
        reset = 1'b1;
        instruction = 32'b0;
        io_in_valid = 1'b0;
        io_in = 32'b0;

        test_count = 0;
        pass_count = 0;
        fail_count = 0;

        repeat (2) @(posedge clk);
        reset = 1'b0;

        issue(enc_instr(OP_LOADL, 8'd1, 8'd5, 8'd0));
        check_result(32'd5, "LOADL gp1, 5");

        issue(enc_instr(OP_LOADL, 8'd2, 8'd3, 8'd0));
        check_result(32'd3, "LOADL gp2, 3");

        issue(enc_instr(OP_ADD, 8'd1, 8'd2, 8'd3));
        check_result(32'd8, "ADD gp1 + gp2 -> gp3");

        issue(enc_instr(OP_SUB, 8'd1, 8'd2, 8'd4));
        check_result(32'd2, "SUB gp1 - gp2 -> gp4");

        issue(enc_instr(OP_NOT, 8'd1, 8'd0, 8'd5));
        check_result(32'hFFFF_FFFA, "NOT gp1 -> gp5");

        issue(enc_instr(OP_CMP, 8'd1, 8'd1, 8'd0));
        check_result(32'd0, "CMP gp1, gp1 result");
        check_flags(4'b0101, "CMP gp1, gp1 zero+equal flags");

        issue(enc_instr(OP_MOVM, 8'd3, 8'hFF, 8'd0));
        check_result(32'd8, "MOVM gp3 -> OUT(0xFF) result");
        check_io(1'b1, 32'd8, "MOVM to MMIO asserts output pulse");

        io_in_valid = 1'b1;
        io_in = 32'd11;
        issue(enc_instr(OP_LOADM, 8'd6, 8'hFE, 8'd0));
        check_result(32'd11, "LOADM gp6 <- IN(0xFE) result");

        issue(enc_instr(OP_NOP, 8'd0, 8'd0, 8'd0));
        check_result(32'd11, "NOP keeps prior result");

        $display("\n=== CPU TB SUMMARY ===");
        $display("Total:  %0d", test_count);
        $display("Passed: %0d", pass_count);
        $display("Failed: %0d", fail_count);

        if (fail_count == 0) begin
            $display("*** ALL TESTS PASSED ***");
        end else begin
            $display("*** TEST FAILURES DETECTED ***");
        end

        $finish;
    end
endmodule
