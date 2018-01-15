// #define INWIRE  top->wire_0_0_BUS16_S1_T0

//// #define OUTWIRE top->wire_1_0_BUS16_S1_T0
// #define OUTWIRE  top->wire_1_2_BUS16_S3_T0

/// module tb();

#include "Vtop.h"
#include "verilated.h"

// If trace requested, verilator will set VM_TRACE to 1, else 0
#if VM_TRACE > 0
#include "verilated_vcd_c.h"
#define CLOSETRACE if (trace_filename != NULL) { tfp->close(); }
#else
#define CLOSETRACE
#endif

// This is not really used anymore, I think...
//int set_rando(
//              unsigned int *in_0_0,
//              unsigned int *in_0_1,
//              unsigned int *in_1_0,
//              unsigned int *in_1_1
//              ) {
//    // add4, no input file, use four rando's
//    in_0_0 = random() & 0xffff;
//    in_0_1 = random() & 0xffff;
//    in_1_0 = random() & 0xffff;
//    in_1_1 = random() & 0xffff;
//    
//    // add4 emulating mul2, no input file, use rando
//    in_0_0 = random() & 0xffff;
//    in_0_1 = in_0_0;
//    in_1_0 = 0;
//    in_1_1 = 0;
//    
//    // add4 w/input file
//    // in_0_0 = (unsigned int)fgetc(input_file);
//    // in_0_1 = (unsigned int)fgetc(input_file);
//    // in_1_0 = (unsigned int)fgetc(input_file);
//    // in_1_1 = (unsigned int)fgetc(input_file);
//    // // printf("Scanned input data %04x %04x %04x %04x\n", in_0_0, in_0_1, in_1_0, in_1_1);
//}

int main(int argc, char **argv, char **env) {
    char *config_filename = NULL;
    char  *input_filename = NULL;
    char *output_filename = NULL;
    char  *trace_filename = NULL;

    char default_trace_filename[128] = "top_tb.vcd";

    FILE *input_file = NULL;
    FILE *output_file = NULL;

    // Run simulation for NCLOCKS clock periods (default = 40)
    int NCLOCKS = 40;

    printf("\n\nHi there!  I am the simulatory thingy.\n");
    fflush(stdout);

    // printf("    arg0 is maybe %s\n", argv[0]);  // "obj_dir/Vtop"
    // printf("    arg1 is maybe %s\n", argv[1]);  // "-config"
    // printf("    arg2 is maybe %s\n", argv[2]);  // "../../hardware/generator_z/top_tb/tile_config.dat"
    // printf("\n");

//    int do_2x = 1
//    else if (! strcmp(argv[i], "-no_2x" ))  { do_2x = 0; }


    int delay_in = 0;  // How long to wait before sending output
    int delay_out = 0; // How long to wait before  ending output

    int initial_delay_so_far = 0;
    int final_delay_so_far = 0;

    for (int i=1; i< argc; i++) {
        // printf("    arg%d is maybe %s\n", i, argv[i]);
        if      (! strcmp(argv[i], "-config"))  { config_filename = argv[++i]; }
        else if (! strcmp(argv[i], "-input" ))  { input_filename  = argv[++i]; }
        else if (! strcmp(argv[i], "-output" )) { output_filename = argv[++i]; }
        else if (! strcmp(argv[i], "-trace" ))  { trace_filename  = argv[++i]; }
        else if (! strcmp(argv[i], "-nclocks")) { 
                sscanf(argv[++i], "%d", &NCLOCKS);
        }
        else if (! strcmp(argv[i], "-delay")) { 
            sscanf(argv[++i], "%d,%d", &delay_in, &delay_out);
        }
        else if (! strcmp(argv[i], "--help" )) {
            fprintf(stderr, "Usage: %s\n%s%s%s%s%s\n",
                    argv[0],
                    "  -config <config_filename>\n",
                    "  -input  <input_filename>\n",
                    "  -output <output_filename>\n",
                    "  [-trace <trace_filename>]\n",
                    "  -nclocks <max_ncycles e.g. '100K' or '5M' or '3576602'>\n"
                    );
        }
    }

    printf("  - Will run for %d cycles or until eof(input)\n", NCLOCKS);
    printf("  - Found config filename '%s'\n", config_filename);

    if (input_filename == NULL) {
        printf("\n");
        printf("WARNING No input file specified. I will generate random numbers instead of input.\n");
    }
    else {
        printf("  - Found input filename '%s'\n", input_filename);

        input_file = fopen(input_filename, "r");
        if (input_file == NULL) {
            fflush(stdout);
            fprintf(stderr,"\n\nERROR: Could not open input file '%s'\n\n", input_filename);
            exit(-1);
        }
    }

    if (output_filename == NULL) {
        printf("\n");
        printf("WARNING No output file specified. I will write debug info only.\n");
    }
    else {
        printf("  - Found output filename '%s'\n", output_filename);

        output_file = fopen(output_filename, "w");
        if (output_file == NULL) {
            fflush(stdout);
            fprintf(stderr,"\n\nERROR: Could not create output file '%s'\n\n", output_filename);
            exit(-1);
        }
    }

#if VM_TRACE > 0
    if (trace_filename == NULL) {
        printf("\n");
        // trace_filename = "top_tb.vcd";
        trace_filename = default_trace_filename;
        printf("WARNING No trace file specified. I am using default '%s'\n", trace_filename);
    }
    else {
        printf("  - Found trace filename '%s' for output waveforms\n", trace_filename);
    }
#else
    printf("NOTE no trace file was requested.\n");
#endif


//    if (delay_in)  { printf("NOTE REQUESTED OUTPUT SEND DELAY OF %d CYCLES\n", delay_in); }
//    if (delay_out) { printf("NOTE REQUESTED OUTPUT  END DELAY OF %d CYCLES\n", delay_out); }
    if (1) { printf("NOTE REQUESTED OUTPUT SEND DELAY OF %d CYCLES\n", delay_in); }
    if (1) { printf("NOTE REQUESTED OUTPUT  END DELAY OF %d CYCLES\n", delay_out); }
    printf("\n");

    /*
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
    */

    // exit(-1);

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

#if VM_TRACE > 0
    // Prepare to build waveform file
    // Verilated::commandArgs(argc, argv); // ?
    Verilated::traceEverOn(true);
    VerilatedVcdC* tfp = new VerilatedVcdC;
    if (trace_filename != NULL) {
        top->trace(tfp, 99); // What is 99?  I don't know!  FIXME
        tfp->open(trace_filename);
    }
#endif

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

    config_data_file = fopen(config_filename, "r");

    if (config_data_file == NULL) {
        fprintf(stderr,"\n\nERROR: Could not open config file '%s'\n\n", config_filename);
        exit(-1);
    }

    // Tile configuration init END
    /////////////////////////////////////////////////////////
    ///    always #0.625 clk <= ~clk;

    int nprints = 0;

//    // First config addr/data should be stable well before reset goes low...
//    fscanf(config_data_file, "%x %x", &config_addr_i, &config_data_i);
//    config_addr = config_addr_i;
//    config_data = config_data_i;

    for (int i=0; i<NCLOCKS; i++) {
        // travis freaks out if no output for 10 minutes...
        // if ( (i%100000) == 0) {
        //     if (i==100000) printf("Executed %dK cycles...", i/1000);
        //     else if (i>0)  printf("%dK...", i/1000);
        //     fflush(stdout);
        // }
        if ( (i%100000) == 0 ) {
            printf("Executed %dK cycles...\n", i/1000); fflush(stdout);
        }

        char what_i_did[256] = "";
        // sprintf(what_i_did, "");

        // @posedge events go here.

        ///    always @(posedge clk) begin
        ///      if (!(&reset_count)) begin 
        ///        reset_count <= reset_count + 1;  // Remember this is four bits!
        ///      end
        ///    end
        ///    assign reset = !reset_count[3];
    
//        if (i>4) { reset = 0; } else { sprintf(what_i_did, "reset=1"); }
//        if (i==4) { sprintf(what_i_did, "reset=0\n"); }

        unsigned int in_0_0;
        unsigned int in_0_1;
        unsigned int in_1_0;
        unsigned int in_1_1;

        for (clk=0; clk<2; clk++) {

#if VM_TRACE > 0
            // dump variables into VCD file
            tfp->dump (2*i+clk);
#endif
            if (clk==0) {
                // Note "clk==0" makes reset go low on negedge of clock
                // Note2 seems to work either way
                if (i>4) { reset = 0; } else { sprintf(what_i_did, "reset=1"); }
                if (i==4) { sprintf(what_i_did, "reset=0\n"); }
            }

            //printf("CyNum-rst-clk %05d %d %d, ", i, reset, clk);
            // char prefix[256];
            // sprintf(prefix, "cy.clk %05d.%d R%d: ", i, clk, reset);
            // printf("cy.clk %05d.%d R%d: ", i, clk, reset);
            // top->clk = !top->clk;
            // printf("Sim-cycle.clock %03d.%d, ", i, clk);

            // FIXME (below) why not "if (!reset && !tile_config_done)" instead?

            /////////////////////////////////////////////////////////
            if (!reset && !clk) { // negedge GOOD
//            if (!reset && clk) { // posedge BAD
                // TILE CONFIGURATION - Change config data "on posedge"
                // E.g. set config when clk==0, after posedge event processed

                fscanf(config_data_file, "%x %x", &config_addr_i, &config_data_i);
                if (!feof(config_data_file)) {
                    // printf("scanned config data %08X %08X\n", config_addr_i, config_data_i);
                    sprintf(what_i_did, "scanned config data %08X %08X", config_addr_i, config_data_i);
                    config_addr = config_addr_i;
                    config_data = config_data_i;
                } else {
                    tile_config_done = 1;
                }
            } // (!reset && !clk)

            if (!reset && tile_config_done && clk) { // posedge
                // READ INPUT DATA - Change input data "on posedge"
                // E.g. set config when clk==1, after posedge event processed
                in_0_0 = (unsigned int)fgetc(input_file);
                // printf("Scanned input data %04x\n", in_0_0);

                if (feof(input_file)) {
                    if (final_delay_so_far == delay_out) {
                        printf("\nINFO Simulation ran for %d cycles (349)\n\n", i);
                        if (input_file)       { fclose(input_file ); }
                        if (output_file)      { fclose(output_file); }
                        if (config_data_file) { fclose(config_data_file); }
                        CLOSETRACE // YES!
                        exit(0);
                    } // (input_filename == NULL) {} else {
                    else {
                        if (final_delay_so_far == 0) { printf("\n"); }
                        printf("One more (349): delay_out=%d, final_delay_so_far=%d",
                               delay_out, final_delay_so_far);
                        in_0_0 = 0;
                        // final_delay_so_far++; // This happnes later, see below.
                    }
                }

            } // (!reset && tile_config_done && !clk)

            // Tile configuration END
            /////////////////////////////////////////////////////////

            /////////////////////////////////////////////////////////
            // DUT instantiation
            /////////////////////////////////////////////////////////

            // These happen on EVERY clock edge, pos and neg
            top->clk = clk;
            top->reset = reset;
            top->config_addr = config_addr;
            top->config_data = config_data;
            INWIRE = in_0_0;

            ///always @(posedge clk) begin
            ///   $display ("%h + %h + %h + %h = %h (%h)", in_0_0, in_0_1, in_1_0,
            ///   in_1_1, dut.wire_0_1_BUS16_S0_T4 ,in_0_0+in_0_1+in_1_0+in_1_1);
            // printf("  top:clk,reset = %d,%d, ", top->clk, top->reset);

            // PROCESS THE NEXT ROUND OF VERILOG EVENTS (posedge, negedge, repeat...)
            top->eval ();

            // if (! printed_something) { printf("\n"); }
        } // for (clk)
        if (!reset && tile_config_done) {
            nprints++;

            // Only print info for first 40 cycles, see how that goes
            if (i < 60) {
                if (delay_in == 0) {
                    // If delay zero, assume we're doing the 2x thing (oh so terrible)
                    // 
                    // Queue up output in "what_i_did" buffer, to display later
                    // INWIRE and OUTWIRE get set by sed script in run.csh maybe
                    sprintf(what_i_did, "Two times %d = %d  *%s*", 
                            INWIRE,
                            OUTWIRE,
                            OUTWIRE == 2*INWIRE ? "PASS" : "FAIL"
                            );
                }
                else {
                    sprintf(what_i_did, "Input %d => result %d", 
                            INWIRE,
                            OUTWIRE
                            );
                }
            }
            else sprintf(what_i_did, "...");

            // Output to output file if specified.
            if (output_file != NULL) {
                if (initial_delay_so_far == delay_in) {
                    // char c = (char)(top->wire_0_1_BUS16_S0_T4 & 0xff);
                    char c = (char)(OUTWIRE & 0xff);
                    // printf("\nemit %d to output file\n", c);
                    fputc(c, output_file);
                    if ((delay_in > 0) && (i < 40)) {
                        sprintf(what_i_did, "Input %d => result %d => OUT", 
                                INWIRE,
                                OUTWIRE
                                );
                    }

                }
                else {
                    initial_delay_so_far++;
                }
            }
        }
        if (nprints==1) {
            printf("\n");
        }


        if (i <= 60) {
            // printf("cy.clk %05d.%d: ", i, top->clk);
            printf("%05d: ", i);
            printf("%s\n", what_i_did);
        }

        // FIXME/TODO maybe build a "close_all_and_exit" subroutine and call it before exit(s)
        if (input_filename != NULL) {
            if (feof(input_file)) {
                if (final_delay_so_far == delay_out) {
                    printf("\n\nINFO Simulation ran for %d cycles (446)\n\n", i);
                    // fclose(input_file);
                    // if (output_file) { fclose(output_file); }
                    if (input_file)       { fclose(input_file ); }
                    if (output_file)      { fclose(output_file); }
                    if (config_data_file) { fclose(config_data_file); }
                    CLOSETRACE
                    exit(0);
                }
                else {
                    //printf("One more (446): delay_out=%d, final_delay_so_far=%d\n",
                    //delay_out, final_delay_so_far);
                        final_delay_so_far++;
                }
            }
        }
    } // for (i)

    if (Verilated::gotFinish()) {
        printf("\n\nINFO Simulation ran for %d cycles (459)\n\n", NCLOCKS);
        if (input_file)       { fclose(input_file ); }
        if (output_file)      { fclose(output_file); }
        if (config_data_file) { fclose(config_data_file); }
        CLOSETRACE
        exit(0);
    }
    CLOSETRACE
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

