`timescale 1ns / 1ns
`include "cpu.sv"

// server_tb.sv — CTF Challenge Server
//
// Runs the custom RISC CPU and relays MMIO I/O between the CPU and stdin/stdout.

module server_tb;
    logic        clk, reset;
    logic        io_in_valid;
    logic [31:0] io_in;
    logic [31:0] result_out;
    logic [3:0]  flags_out;
    logic [31:0] pc_out;
    logic        io_valid;
    logic [31:0] io_out;

    cpu dut (
        .clk           (clk),
        .reset         (reset),
        .program_mode  (1'b1),
        .instruction_in(32'b0),
        .io_in_valid   (io_in_valid),
        .io_in         (io_in),
        .result_out    (result_out),
        .flags_out     (flags_out),
        .pc_out        (pc_out),
        .io_valid      (io_valid),
        .io_out        (io_out)
    );

    // Manually driven clock.  No free-running always generator — simulation time
    // is frozen whenever the initial block is blocked inside $fgetc.
    task automatic tick();
        #5 clk = 1;
        #5 clk = 0;
    endtask

    integer stdin_fd;
    integer byte_val;
    integer cycle;
    int     got_output;

    initial begin
        clk         = 0;
        reset       = 1;
        io_in_valid = 0;
        io_in       = 32'h0;

        $readmemh("server_fake.hex", dut.instr_mem);

        // Hold reset for 2 cycles then release
        tick(); tick();
        reset = 0;

        stdin_fd = 32'h8000_0000; // STDIN

        $display("=== Custom Silicon CPU Challenge ===");
        $display("Send exploit bytes via stdin (one raw byte per attempt).");
        $display("");

        forever begin
            byte_val = $fgetc(stdin_fd);       // blocks; simulation frozen here
            if (byte_val < 0) $finish(0);      // EOF / pipe closed

            io_in       = 32'(byte_val);
            io_in_valid = 1;

            got_output = 0;
            for (cycle = 0; cycle < 200 && !got_output; cycle++) begin
                tick();
                if (io_valid) begin
                    got_output = 1;
                    if (io_out[7:0] == 8'h00) begin
                        $display("DENIED");
                    end else begin
                        $write("%c", io_out[7:0]);          
                        for (int k = 0; k < 256; k++) begin
                            tick(); tick();                 
                            if (io_valid)
                                $write("%c", io_out[7:0]);
                            else
                                break;
                        end
                        $display("");                       
                        $finish(0);
                    end
                end
            end
        end
    end
endmodule

