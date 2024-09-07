entity FPGA_TOP is
	port(
	i_ENC_C	:in  std_logic;--1系のA相
	i_ENC_D	:in  std_logic;--1系のB相
	
	o_MOT_STP	:out  std_logic; --1系のパルス
	o_MOT_DIR	:out  std_logic; --1系の方向
    );
end entity;