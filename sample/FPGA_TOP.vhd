library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

entity FPGA_TOP is
	port(
	i_ENC1_A	:in  std_logic;--1系のA相
	i_ENC1_B	:in  std_logic;--1系のB相
	i_ENC2_A	:in  std_logic;--2系のA相
	i_ENC2_B	:in  std_logic;--2系のB相
	i_ENC3_A	:in  std_logic;--3系のA相
	i_ENC3_B	:in  std_logic;--3系のB相
	i_ENC4_A	:in  std_logic;--4系のA相
	i_ENC4_B	:in  std_logic;--4系のB相
	
	o_MOT1_STP	:out  std_logic; --1系のパルス
	o_MOT1_DIR	:out  std_logic; --1系の方向
	o_MOT2_STP	:out  std_logic; --2系のパルス
	o_MOT2_DIR	:out  std_logic; --2系の方向
	o_MOT3_STP	:out  std_logic; --3系のパルス
	o_MOT3_DIR	:out  std_logic; --3系の方向
	o_MOT4_STP	:out  std_logic; --4系のパルス
	o_MOT4_DIR	:out  std_logic); --4系の方向
end entity;

architecture RTL of FPGA_TOP is
begin
	MC_inst1:entity MotorController1
		port map
		(i_ENC_A	=>i_ENC1_A
		,i_ENC_B	=>i_ENC1_B
		,o_MOT_STP	=>o_MOT1_STP
		,o_MOT_DIR	=>o_MOT1_DIR
		);
	
	MC_inst2:entity MotorController1
		port map
		(i_ENC_A	=>i_ENC1_A
		,i_ENC_B	=>i_ENC2_B
		,o_MOT_STP	=>o_MOT2_STP
		,o_MOT_DIR	=>o_MOT2_DIRx
		);
	
	MC_inst3:entity MotorController2
		port map
		(i_ENC_C	=>i_ENC3_A
		,i_ENC_D	=>i_ENC3
		,o_MOT_STP	=>o_MOT3_STPi
		,o_MOT_DIR	=>o_MOT3_DIR
		);
	
	MC_inst4:entity MotorController2
		port map
		(i_ENC_C	=>o_MOT3_STPi
		,i_ENC_D	=>o_MOT3_STPi
		,o_MOT_STP	=>o_MOT4_STP
		,o_MOT_DIR	=>o_MOT4_DIR
		);
end architecture;
