/// module tb();

#include "Vtop.h"
#include "verilated.h"
// #include "verilated_vcd_c.h"

int main(int argc, char **argv, char **env) {
    char *config_filename;
    char *input_filename;

    FILE *input_file;


    printf("\n\nHi there!  I am the simulatory thingy.\n");
    // printf("    arg0 is maybe %s\n", argv[0]);  // "obj_dir/Vtop"
    // printf("    arg1 is maybe %s\n", argv[1]);  // "-config"
    // printf("    arg2 is maybe %s\n", argv[2]);  // "../../hardware/generator_z/top_tb/tile_config.dat"
    // printf("\n");

    for (int i=1; i< argc; i++) {
        // printf("    arg%d is maybe %s\n\n", argv[i]);
        if      (! strcmp(argv[i], "-config")) { config_filename = argv[++i]; }
        else if (! strcmp(argv[i], "-input" )) { input_filename  = argv[++i]; }
    }

    printf("Found config filename '%s'\n", config_filename);

    if (input_filename == NULL) {
        printf("WARNING No input file specified.\n");
        printf("WARNING I will generate random numbers instead of input.\n");
    }
    else {
        printf("Found input filename '%s'\n", input_filename);

        // FIXME fopen has no corresponding fclose()!
        input_file = fopen(input_filename, "r");
        if (input_file == NULL) {
            fflush(stdout);
            fprintf(stderr,"\n\nERROR: Could not open input file '%s'\n\n", input_filename);
            exit(-1);
        }


    }

    // Let's try reading from the input file

    unsigned int in_0_0 = (unsigned int)fgetc(input_file);
    unsigned int in_0_1 = (unsigned int)fgetc(input_file);
    unsigned int in_1_0 = (unsigned int)fgetc(input_file);
    unsigned int in_1_1 = (unsigned int)fgetc(input_file);

    printf("Found four 8-bit input pixels 0x%04x 0x%04x 0x%04x 0x%04x\n",
           in_0_0,
           in_0_1,
           in_1_0,
           in_1_1);


    exit(-1);

    // return(-1);

    /////////////////////////////////////////////////////////
    // Clock and reset
    /////////////////////////////////////////////////////////
    ///
    ///    reg clk;
    ///    reg [3:0] reset_count;
    ///    wire reset;
    
    int clk;
    int reset_count;
    int reset;

    Verilated::commandArgs(argc, argv);
    Vtop* top = new Vtop;

    ///    initial begin
    ///      clk<=1'b1;
    ///      reset_count<=4'd0;
    ///    end

    clk = 1;
    reset = 1;
    reset_count = 0;

    /////////////////////////////////////////////////////////
    // Tile configuration init BEGIN
    ///
    ///    integer    config_data_file    ; // file handler
    ///    reg [31:0] config_addr_i;
    ///    reg [31:0] config_data_i;
    ///    reg [31:0] config_addr;
    ///    reg [31:0] config_data;
    ///    reg tile_config_done;

    FILE *config_data_file; // file handler

    unsigned int config_addr_i;
    unsigned int config_data_i;

    unsigned int config_addr;
    unsigned int config_data;

    int tile_config_done;

    ///    initial begin
    ///      config_addr_i <= 0;
    ///      config_data_i <= 0;
    ///      config_addr <= 0;
    ///      config_data <= 0;
    ///      tile_config_done <= 0;
    ///    end

    config_addr_i = 0;
    config_data_i = 0;

    config_addr = 0;
    config_data = 0;

    tile_config_done = 0;

    ///    `define NULL 0
    ///    initial begin
    ///      config_data_file = $fopen("tile_config.dat", "r");
    ///      if (config_data_file == `NULL) begin
    ///        $display("config_data_file handle was NULL");
    ///        $finish;
    ///      end
    ///    end

    // FIXME fopen has no corresponding fclose()!
    // config_data_file = fopen("tile_config.dat", "r");
    config_data_file = fopen(config_filename, "r");

    if (config_data_file == NULL) {
        fflush(stdout);
        fprintf(stderr,"\n\nERROR: Could not open config file '%s'\n\n", config_filename);
        exit(-1);
    }

// Tile configuration init END
/////////////////////////////////////////////////////////

  ///    always #0.625 clk <= ~clk;

    int nprints = 0;

  // Run simulation for NCLOCKS clock periods
  int NCLOCKS = 40;
  for (int i=0; i<NCLOCKS; i++) {
      char what_i_did[256] = "";
      // sprintf(what_i_did, "");

      // @posedge events go here.

      ///    always @(posedge clk) begin
      ///      if (!(&reset_count)) begin 
      ///        reset_count <= reset_count + 1;  // Remember this is four bits!
      ///      end
      ///    end
      ///    assign reset = !reset_count[3];
    
      if (i>4) { reset = 0; } else { sprintf(what_i_did, "reset=1"); }
      if (i==4) { sprintf(what_i_did, "reset=0\n"); }

      if (input_filename == NULL) {
          unsigned int in_0_0 = random() & 0xff;
          unsigned int in_0_1 = random() & 0xff;
          unsigned int in_1_0 = random() & 0xff;
          unsigned int in_1_1 = random() & 0xff;
      }
      else {
          unsigned int in_0_0 = (unsigned int)fgetc(input_file);
          unsigned int in_0_1 = (unsigned int)fgetc(input_file);
          unsigned int in_1_0 = (unsigned int)fgetc(input_file);
          unsigned int in_1_1 = (unsigned int)fgetc(input_file);
      }

      for (clk=0; clk<2; clk++) {

          //printf("CyNum-rst-clk %05d %d %d, ", i, reset, clk);
          // char prefix[256];
          // sprintf(prefix, "cy.clk %05d.%d R%d: ", i, clk, reset);
          // printf("cy.clk %05d.%d R%d: ", i, clk, reset);

          // top->clk = !top->clk;

          // printf("Sim-cycle.clock %03d.%d, ", i, clk);

          /////////////////////////////////////////////////////////
          // Tile configuration run BEGIN

          ///    always @(posedge clk) begin
          ///      if (!reset) begin
          ///        $fscanf(config_data_file, "%h %h", config_addr_i,config_data_i); 
          ///        if (!$feof(config_data_file)) begin
          ///          config_addr <= config_addr_i;
          ///          config_data <= config_data_i;
          ///        end else begin
          ///          tile_config_done <= 1'b1;
          ///        end
          ///      end
          ///    end

          if (clk == 0) { // So it will be stable for posedge events, I guess
              // FIXME (below) why not "if (!reset && !tile_config_done)" instead?
              if (!reset) {
                  fscanf(config_data_file, "%x %x", &config_addr_i, &config_data_i);
                  if (!feof(config_data_file)) {
                      // printf("scanned config data %08X %08X\n", config_addr_i, config_data_i);
                      sprintf(what_i_did, "scanned config data %08X %08X", config_addr_i, config_data_i);
                      config_addr = config_addr_i;
                      config_data = config_data_i;
                  } else {
                      tile_config_done = 1;
                  }
              }
          }

          // Tile configuration run END
          /////////////////////////////////////////////////////////

          /////////////////////////////////////////////////////////
          // DUT instantiation
          /////////////////////////////////////////////////////////

          ///top dut (
          ///.clk(clk),
          ///.reset(reset),
          ///.wire_0_m1_BUS16_S0_T0(in_0_0),
          ///.wire_m1_0_BUS16_S1_T0(in_0_1),
          ///.wire_1_m1_BUS16_S0_T2(in_1_0),
          ///.wire_2_0_BUS16_S3_T2(in_1_1),
          ///.config_addr(config_addr),
          ///.config_data(config_data)
          ///);

          top->clk = clk;
          top->reset = reset;

          top->wire_0_m1_BUS16_S0_T0 = in_0_0;
          top->wire_m1_0_BUS16_S1_T0 = in_0_1;
          top->wire_1_m1_BUS16_S0_T2 = in_1_0;
       // top->wire_2_0_BUS16_S3_T2  = in_1_1;
          top->wire_4_0_BUS16_S3_T2  = in_1_1;

          top->config_addr = config_addr;
          top->config_data = config_data;

          ///
          ///always @(posedge clk) begin
          ///
          ///   $display ("%h + %h + %h + %h = %h (%h)", in_0_0, in_0_1, in_1_0,
          ///   in_1_1, dut.wire_0_1_BUS16_S0_T4 ,in_0_0+in_0_1+in_1_0+in_1_1);

          // printf("  top:clk,reset = %d,%d, ", top->clk, top->reset);


          top->eval ();

          // if (! printed_something) { printf("\n"); }
      } // for (clk)
      if (!reset && tile_config_done) {
          nprints++;
          sprintf(what_i_did, "%04x + %04x + %04x + %04x = %04x (%04x)",
                  in_0_0, in_0_1, in_1_0, in_1_1,
                  top->wire_0_1_BUS16_S0_T4,
                  (in_0_0 + in_0_1 + in_1_0 + in_1_1)
                  );
      }
      if (nprints==1) {
          printf("\n");
      }
      // printf("cy.clk %05d.%d: ", i, top->clk);
      printf("%05d: ", i);
      printf("%s\n", what_i_did);

  } // for (i)
  if (Verilated::gotFinish()) exit(0);
} // main()

/////////////////////////////////////////////////////////
// Data generation 
/////////////////////////////////////////////////////////

///  reg [15:0] pe_output_0;
///  reg [15:0] in_0_0;
///  wire [15:0] out_0_0;
///  reg [15:0] in_0_1;
///  wire [15:0] out_0_1;
///  reg [15:0] in_0_2;
///  wire [15:0] out_0_2;
///  reg [15:0] in_0_3;
///  wire [15:0] out_0_3;
///  reg [15:0] in_0_4;
///  wire [15:0] out_0_4;
///  reg [15:0] in_1_0;
///  wire [15:0] out_1_0;
///  reg [15:0] in_1_1;
///  wire [15:0] out_1_1;
///  reg [15:0] in_1_2;
///  wire [15:0] out_1_2;
///  reg [15:0] in_1_3;
///  wire [15:0] out_1_3;
///  reg [15:0] in_1_4;
///  wire [15:0] out_1_4;
///  reg [15:0] in_2_0;
///  wire [15:0] out_2_0;
///  reg [15:0] in_2_1;
///  wire [15:0] out_2_1;
///  reg [15:0] in_2_2;
///  wire [15:0] out_2_2;
///  reg [15:0] in_2_3;
///  wire [15:0] out_2_3;
///  reg [15:0] in_2_4;
///  wire [15:0] out_2_4;
///  reg [15:0] in_3_0;
///  wire [15:0] out_3_0;
///  reg [15:0] in_3_1;
///  wire [15:0] out_3_1;
///  reg [15:0] in_3_2;
///  wire [15:0] out_3_2;
///  reg [15:0] in_3_3;
///  wire [15:0] out_3_3;
///  reg [15:0] in_3_4;
///  wire [15:0] out_3_4;
///
///
///always @(posedge clk) begin
///  pe_output_0 <= $random;
///  in_0_0 <= $random;
///  in_0_1 <= $random;
///  in_0_2 <= $random;
///  in_0_3 <= $random;
///  in_0_4 <= $random;
///  in_1_0 <= $random;
///  in_1_1 <= $random;
///  in_1_2 <= $random;
///  in_1_3 <= $random;
///  in_1_4 <= $random;
///  in_2_0 <= $random;
///  in_2_1 <= $random;
///  in_2_2 <= $random;
///  in_2_3 <= $random;
///  in_2_4 <= $random;
///  in_3_0 <= $random;
///  in_3_1 <= $random;
///  in_3_2 <= $random;
///  in_3_3 <= $random;
///  in_3_4 <= $random;
///end

