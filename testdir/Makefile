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

# foo: ../bitstream/examples/cd387-good.bs $(VERILATOR_TOP)/top_tb.cpp $(VERILATOR_TOP)/io/gray_small.png
# 	@echo $?
# 	@echo $(?:.bs=.foo)
# 	echo $(filter %.cpp,$?)
# 	bitstream=$(filter %.bs,$?); echo $$bitstream
# 	input=$(filter %.png,$?); echo $$input
# 
# %.baz : ; echo foo
# 	echo bar
# 	echo $?
# 	$(A=b)
# 	echo $(A)
# 
# bar.baz: ../bitstream/examples/cd387-good.bs


test_all:
	make test_4x4_gray_small 2>&1 | tee /tmp/test_4x4_gray_small.log
#	grep '\*PASS\*' /tmp/test_4x4_gray_small.log | head -1
	grep 'FAIL' /tmp/test_4x4_gray_small.log && exit -1

	make test_8x8_gray_small 2>&1 | tee /tmp/test_8x8_gray_small.log
	grep '\*PASS\*' /tmp/test_8x8_gray_small.log | head -1

	make test_4x4_gray       2>&1 | tee /tmp/test_4x4_gray.log
	grep '\*PASS\*' /tmp/test_4x4_gray.log | head -1

	make test_8x8_gray       2>&1 | tee /tmp/test_8x8_gray.log
	grep '\*PASS\*' /tmp/test_8x8_gray.log | head -1

	@echo ""
	@echo SUMMARY OF TEST RESULTS
	@echo ==================================================
	@egrep '^00014'                \
	  /tmp/test_4x4_gray_small.log \
	  /tmp/test_8x8_gray_small.log \
	  /tmp/test_4x4_gray.log       \
	  /tmp/test_8x8_gray.log

test_4x4_gray_small:
# 	@echo ""
# 	@echo TEST $@
# 	@echo Making $@ because of $?
# 	@echo ==================================================
	bitstream=../../bitstream/examples/cd387-good.bs; \
	image=gray_small;              \
	cd $(VERILATOR_TOP);	        \
	./run.csh -gen top_tb.cpp -oldmem -4x4       \
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output /tmp/$${image}_out.raw   \
	   -nclocks 5M;                     \
        cmp io/$${image}.png io/$${image}_out.raw || echo FAIL

test_4x4_gray:
	bitstream=../../bitstream/examples/cd387-good.bs; \
	image=gray;                    \
	cd $(VERILATOR_TOP);	        \
	./run.csh -gen top_tb.cpp -oldmem -4x4        \
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output /tmp/$${image}_out.raw   \
	   -nclocks 5M

test_8x8_gray_small:
	bitstream=../../bitstream/examples/cd387-newmem-8x8.bs; \
	image=gray_small;              \
	cd $(VERILATOR_TOP);	        \
	./run.csh -gen top_tb.cpp -usemem -8x8\
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output /tmp/$${image}_out.raw   \
	   -nclocks 5M

test_8x8_gray:
	bitstream=../../bitstream/examples/cd387-newmem-8x8.bs; \
	image=gray;                    \
	cd $(VERILATOR_TOP);	        \
	./run.csh -gen top_tb.cpp -usemem -8x8\
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output /tmp/$${image}_out.raw   \
	   -nclocks 5M
