`timescale 1ns / 1ps

module mult #(
	parameter N_MUL_LEN = 4
	)(
	input clk, rstn,
	input [N_MUL_LEN - 1:0] X, Y,
	output logic [N_MUL_LEN - 1:0] Z
	);

	logic [N_MUL_LEN - 1:0] ZZ;
	always_ff @(posedge clk) begin
		if (!rstn) 
			Z <= 0;
		else begin
			ZZ <= X*Y;
			Z <= ZZ;
		end
	end

endmodule // mult
