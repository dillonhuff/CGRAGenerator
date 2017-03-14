module tb();
/////////////////////////////////////////////////////////
//
// Clock and reset
//
/////////////////////////////////////////////////////////
    reg clk;
    reg [3:0] reset_count;
    
    wire reset;
    
    initial begin
      clk<=1'b1;
      reset_count<=4'd0;
    end
    
    always #0.625 clk <= ~clk;
    
    always @(posedge clk) begin
      if (!(&reset_count)) begin 
        reset_count <= reset_count + 1;
      end
    end
    
    assign reset = !reset_count[3];
    
/////////////////////////////////////////////////////////
//
// Tile configuration
//
/////////////////////////////////////////////////////////

    integer    config_data_file    ; // file handler
    reg [31:0] config_addr_i;
    reg [31:0] config_data_i;
    reg [31:0] config_addr;
    reg [31:0] config_data;
    reg tile_config_done;

    initial begin
      config_addr_i <= 0;
      config_data_i <= 0;
      config_addr <= 0;
      config_data <= 0;
      tile_config_done <= 0;
    end
    `define NULL 0
    
    initial begin
      config_data_file = $fopen("tile_config.dat", "r");
      if (config_data_file == `NULL) begin
        $display("config_data_file handle was NULL");
        $finish;
      end
    end
    always @(posedge clk) begin
      if (!reset) begin
        $fscanf(config_data_file, "%h %h", config_addr_i,config_data_i); 
        if (!$feof(config_data_file)) begin
          config_addr <= config_addr_i;
          config_data <= config_data_i;
        end else begin
          tile_config_done <= 1'b1;
        end
      end
    end

/////////////////////////////////////////////////////////
//
// Data generation 
//
/////////////////////////////////////////////////////////

  reg [15:0] pe_output_0;
  reg [15:0] in_0_0;
  wire [15:0] out_0_0;
  reg [15:0] in_0_1;
  wire [15:0] out_0_1;
  reg [15:0] in_0_2;
  wire [15:0] out_0_2;
  reg [15:0] in_0_3;
  wire [15:0] out_0_3;
  reg [15:0] in_0_4;
  wire [15:0] out_0_4;
  reg [15:0] in_1_0;
  wire [15:0] out_1_0;
  reg [15:0] in_1_1;
  wire [15:0] out_1_1;
  reg [15:0] in_1_2;
  wire [15:0] out_1_2;
  reg [15:0] in_1_3;
  wire [15:0] out_1_3;
  reg [15:0] in_1_4;
  wire [15:0] out_1_4;
  reg [15:0] in_2_0;
  wire [15:0] out_2_0;
  reg [15:0] in_2_1;
  wire [15:0] out_2_1;
  reg [15:0] in_2_2;
  wire [15:0] out_2_2;
  reg [15:0] in_2_3;
  wire [15:0] out_2_3;
  reg [15:0] in_2_4;
  wire [15:0] out_2_4;
  reg [15:0] in_3_0;
  wire [15:0] out_3_0;
  reg [15:0] in_3_1;
  wire [15:0] out_3_1;
  reg [15:0] in_3_2;
  wire [15:0] out_3_2;
  reg [15:0] in_3_3;
  wire [15:0] out_3_3;
  reg [15:0] in_3_4;
  wire [15:0] out_3_4;


always @(posedge clk) begin
  pe_output_0 <= $random;
  in_0_0 <= $random;
  in_0_1 <= $random;
  in_0_2 <= $random;
  in_0_3 <= $random;
  in_0_4 <= $random;
  in_1_0 <= $random;
  in_1_1 <= $random;
  in_1_2 <= $random;
  in_1_3 <= $random;
  in_1_4 <= $random;
  in_2_0 <= $random;
  in_2_1 <= $random;
  in_2_2 <= $random;
  in_2_3 <= $random;
  in_2_4 <= $random;
  in_3_0 <= $random;
  in_3_1 <= $random;
  in_3_2 <= $random;
  in_3_3 <= $random;
  in_3_4 <= $random;
end

/////////////////////////////////////////////////////////
//
// DUT instantiation
//
/////////////////////////////////////////////////////////

top dut (
.clk(clk),
.reset(reset),
.wire_0_m1_BUS16_S0_T0(in_0_0),
.wire_m1_0_BUS16_S1_T0(in_0_1),
.wire_1_m1_BUS16_S0_T2(in_1_0),
.wire_2_0_BUS16_S3_T2(in_1_1),
.config_addr(config_addr),
.config_data(config_data)
);

always @(posedge clk) begin
   $display ("%h + %h + %h + %h = %h (%h)", in_0_0, in_0_1, in_1_0, in_1_1, dut.wire_0_1_BUS16_S0_T4 ,in_0_0+in_0_1+in_1_0+in_1_1);
end
endmodule

