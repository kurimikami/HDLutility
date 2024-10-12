`timescale 1ns / 1ps


module tb_mult;
    localparam 
        CYCLE = 10,
        DELAY = 2,
        N_LOOP = 10000,
		N_MUL_LEN = 256,
		N_PIPELINE_STAGES = 2;
               
    reg clk, rstn;
    logic [N_MUL_LEN - 1:0] X, Y, Z, ans;
	logic [N_PIPELINE_STAGES - 1:0][N_MUL_LEN - 1:0] reg_ans;

	int unsigned _urandom;
	assign ans = X*Y;

    mult #(N_MUL_LEN) DUT(.clk, .rstn, .X, .Y, .Z);
    
    always begin
        #(CYCLE/2) clk <= ~clk;
    end

	always @(posedge clk) begin
		reg_ans <= {reg_ans[N_PIPELINE_STAGES - 2:0], ans};
	end
    
    /*-------------------------------------------
    Test
    -------------------------------------------*/
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars();
    end
    
    initial begin
		_urandom = $urandom(1);
        rstn = 1'b1;
        clk = 1'b1;
    #(CYCLE*10)
        rstn = 1'b0;
    #(CYCLE*10)
        rstn = 1'b1;
    #DELAY;
        $display("Test start\n");

        for(integer i = 0; i < N_LOOP; i = i + 1) begin
            X = urand_n();
            Y = urand_n();
            
            #DELAY
            $display("%d: x = %h, y = %h, z = %h, ans = %h", i, X, Y, Z, ans);
            if(Z !== reg_ans[N_PIPELINE_STAGES - 1]) begin
                $display("Failed: ans = %h", ans);
                $stop();
            end
            #(CYCLE-DELAY);
        end
        $display("#%d Test end\n", N_LOOP);
        $finish;
    end

	function static [N_MUL_LEN - 1:0] urand_n;
		logic [(N_MUL_LEN/32 + 1)*32 - 1: 0] temp_var = '0;
		repeat(N_MUL_LEN/32 + 1)
			temp_var = {temp_var[$bits(temp_var)-32-1:0], $urandom};
		urand_n = (N_MUL_LEN)'(temp_var);
	endfunction

endmodule

// verilator  tb_mult.sv  --timing --trace  --trace-structs  --binary
// ./obj_dir/Vtb_mult