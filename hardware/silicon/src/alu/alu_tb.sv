`timescale 1ns / 1ns
`include "alu/alu.sv"

module alu_tb;

    // Test signals
    reg [31:0] A, B;
    reg [3:0] Control;
    wire [31:0] Result;
    wire [3:0] Flags;
    
    // Expected results for verification
    reg [31:0] expected_result;
    reg [3:0] expected_flags;
    integer test_count, pass_count, fail_count;

    // DUT instantiation
    alu alu_inst(
        .A(A),
        .B(B), 
        .Control(Control),
        .Result(Result),
        .Flags(Flags)
    );

    // Test task
    task test_alu;
        input [31:0] test_a, test_b;
        input [3:0] test_ctrl;
        input [31:0] exp_result;
        input [3:0] exp_flags;
        input [80*8-1:0] test_name;
        
        begin
            A = test_a;
            B = test_b;
            Control = test_ctrl;
            expected_result = exp_result;
            expected_flags = exp_flags;
            
            #10; // Wait for combinational logic to settle
            
            test_count = test_count + 1;
            
            if (Result === expected_result && Flags === expected_flags) begin
                $display("PASS: %s", test_name);
                $display("      A=%h, B=%h, Ctrl=%b -> Result=%h, Flags=%b", 
                        A, B, Control, Result, Flags);
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL: %s", test_name);
                $display("      A=%h, B=%h, Ctrl=%b", A, B, Control);
                $display("      Expected: Result=%h, Flags=%b", expected_result, expected_flags);
                $display("      Got:      Result=%h, Flags=%b", Result, Flags);
                fail_count = fail_count + 1;
            end
            $display("");
        end
    endtask

    initial begin
        $display("=== ALU Testbench Starting ===");
        $display("Testing ALU with operations: ADD, SUB, AND, OR, XOR, NOT");
        $display("");
        
        // Initialize counters
        test_count = 0;
        pass_count = 0;
        fail_count = 0;
        
        // Test ADD operation (Control = 4'b0000)
        test_alu(32'h00000001, 32'h00000002, 4'b0000, 32'h00000003, 4'b0000, "ADD: 1 + 2 = 3");
        test_alu(32'h00000000, 32'h00000000, 4'b0000, 32'h00000000, 4'b0101, "ADD: 0 + 0 = 0 (Zero flag)");
        test_alu(32'hFFFFFFFF, 32'h00000001, 4'b0000, 32'h00000000, 4'b0011, "ADD: -1 + 1 = 0 (Carry + Zero)");
        test_alu(32'h80000000, 32'h80000000, 4'b0000, 32'h00000000, 4'b0011, "ADD: Overflow test");
        
        // Test SUB operation (Control = 4'b0001)  
        test_alu(32'h00000005, 32'h00000003, 4'b0001, 32'h00000002, 4'b0000, "SUB: 5 - 3 = 2");
        test_alu(32'h00000003, 32'h00000003, 4'b0001, 32'h00000000, 4'b0001, "SUB: 3 - 3 = 0 (Zero flag)");
        test_alu(32'h00000001, 32'h00000002, 4'b0001, 32'hFFFFFFFF, 4'b0000, "SUB: 1 - 2 = -1");
        
        // Test AND operation (Control = 4'b0010)
        test_alu(32'hAAAAAAAA, 32'h55555555, 4'b0010, 32'h00000000, 4'b0001, "AND: 0xAAAAAAAA & 0x55555555 = 0");
        test_alu(32'hFFFFFFFF, 32'h12345678, 4'b0010, 32'h12345678, 4'b0000, "AND: 0xFFFFFFFF & 0x12345678");
        test_alu(32'hF0F0F0F0, 32'h0F0F0F0F, 4'b0010, 32'h00000000, 4'b0001, "AND: Alternating bits");
        
        // Test OR operation (Control = 4'b0011)
        test_alu(32'hAAAAAAAA, 32'h55555555, 4'b0011, 32'hFFFFFFFF, 4'b0000, "OR: 0xAAAAAAAA | 0x55555555");
        test_alu(32'h00000000, 32'h00000000, 4'b0011, 32'h00000000, 4'b0001, "OR: 0 | 0 = 0");
        test_alu(32'h12345678, 32'h87654321, 4'b0011, 32'h97755779, 4'b0000, "OR: Mixed pattern");
        
        // Test XOR operation (Control = 4'b0100)
        test_alu(32'hAAAAAAAA, 32'h55555555, 4'b0100, 32'hFFFFFFFF, 4'b0000, "XOR: 0xAAAAAAAA ^ 0x55555555");
        test_alu(32'h12345678, 32'h12345678, 4'b0100, 32'h00000000, 4'b0001, "XOR: Same values = 0");
        test_alu(32'hFFFFFFFF, 32'hFFFFFFFF, 4'b0100, 32'h00000000, 4'b0001, "XOR: All 1s ^ All 1s = 0");
        
        // Test NOT operation (Control = 4'b0101)
        test_alu(32'h00000000, 32'h00000000, 4'b0101, 32'hFFFFFFFF, 4'b0000, "NOT: ~0x00000000");
        test_alu(32'hFFFFFFFF, 32'h00000000, 4'b0101, 32'h00000000, 4'b0001, "NOT: ~0xFFFFFFFF");
        test_alu(32'hAAAAAAAA, 32'h00000000, 4'b0101, 32'h55555555, 4'b0000, "NOT: ~0xAAAAAAAA");
        
        // Edge cases and corner cases
        test_alu(32'h7FFFFFFF, 32'h00000001, 4'b0000, 32'h80000000, 4'b0000, "ADD: Max positive + 1");
        test_alu(32'h80000000, 32'hFFFFFFFF, 4'b0000, 32'h7FFFFFFF, 4'b0010, "ADD: Min negative + (-1)");
        
        // Summary
        $display("=== Test Summary ===");
        $display("Total Tests: %0d", test_count);
        $display("Passed:      %0d", pass_count);
        $display("Failed:      %0d", fail_count);
        
        if (fail_count == 0) begin
            $display("*** ALL TESTS PASSED! ***");
        end else begin
            $display("*** %0d TESTS FAILED ***", fail_count);
        end
        
        $display("=== ALU Testbench Complete ===");
        $finish;
    end

endmodule