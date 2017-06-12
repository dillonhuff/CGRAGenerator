# Consider:
# 
# script:
#   - cd testdir; make testall

################################################################################
# Makefile Definitions
################################################################################

# # Check environment variables
# 
# # - export CGRA_GEN_USE_MEM=1
# # - export CGRA_GEN_ALL_REG=1
# 
# ifndef CGRA_GEN_USE_MEM
#   CGRA_GEN_USE_MEM := 0
# endif
# 
# ifndef CGRA_GEN_ALL_REG
#   CGRA_GEN_ALL_REG := 0
# endif
# 
# $(warning WARNING: CGRA_GEN_USE_MEM = $(CGRA_GEN_USE_MEM))
# $(warning WARNING: CGRA_GEN_ALL_REG = $(CGRA_GEN_ALL_REG))

# ifndef SMASH
#   $(error ERROR: Chip Gen path is not set. Use "setenv SMASH <path_to_chipgen>")
# else
#   $(warning WARNING: SMASH set to $(SMASH))
# endif

VERILATOR_TOP := ../verilator/generator_z_tb

test_all:
	make test_4x4_gray_small 2>&1 | tee /tmp/test_4x4_gray_small.log
	make test_8x8_gray_small 2>&1 | tee /tmp/test_8x8_gray_small.log
	make test_4x4_gray       2>&1 | tee /tmp/test_4x4_gray.log
	make test_8x8_gray       2>&1 | tee /tmp/test_8x8_gray.log
	@echo ""
	@echo SUMMARY OF TEST RESULTS
	@echo ==================================================
	@egrep '^00014' /tmp/test_{4x4,8x8}_gray_small.log
	@egrep '^00014' /tmp/test_{4x4,8x8}_gray.log

test_4x4_gray_small:
# 	@echo ""
# 	@echo TEST $@
# 	@echo Making $@ because of $?
# 	@echo ==================================================
	bitstream=../../bitstream/examples/cd387-good.bs; \
	image=gray_small;              \
	cd $(VERILATOR_TOP);	        \
	./run.csh -gen top_tb.cpp        \
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output /tmp/$${image}_out.raw   \
	   -nclocks 3M

test_4x4_gray:
	bitstream=../../bitstream/examples/cd387-good.bs; \
	image=gray;                    \
	cd $(VERILATOR_TOP);	        \
	./run.csh -gen top_tb.cpp        \
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output /tmp/$${image}_out.raw   \
	   -nclocks 3M

test_8x8_gray_small:
	bitstream=../../bitstream/examples/cd387-newmem-8x8.bs; \
	image=gray_small;              \
	cd $(VERILATOR_TOP);	        \
	./run.csh -gen top_tb.cpp -usemem\
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output /tmp/$${image}_out.raw   \
	   -nclocks 3M

test_8x8_gray:
	bitstream=../../bitstream/examples/cd387-newmem-8x8.bs; \
	image=gray;                    \
	cd $(VERILATOR_TOP);	        \
	./run.csh -gen top_tb.cpp -usemem\
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output /tmp/$${image}_out.raw   \
	   -nclocks 3M
