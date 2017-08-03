################################################################################
# Makefile Definitions
################################################################################

# ifndef SMASH
#   $(error ERROR: Chip Gen path is not set. Use "setenv SMASH <path_to_chipgen>")
# else
#   $(warning WARNING: SMASH set to $(SMASH))
# endif

VERILATOR_TOP := ../verilator/generator_z_tb

SILENT := FALSE
ifeq ($(SILENT), TRUE)
       QUIET := -q
else
       QUIET :=
endif
$(warning OUTPUT = "$(OUTPUT)")

TEMPDIR := $(shell mktemp -d)

test_all:
	make hackdiff_test | tee $(TEMPDIR)/hackdiff_test.log

	make test_4x4_gray_small 2>&1 | tee $(TEMPDIR)/test_4x4_gray_small.log
	tail -n 1 $(TEMPDIR)/test_4x4_gray_small.log \
		| grep 'FAIL' && exit 9 || exit 0

	make test_8x8_gray_small 2>&1 | tee $(TEMPDIR)/test_8x8_gray_small.log
	tail -n 1 $(TEMPDIR)/test_8x8_gray_small.log \
		| grep 'FAIL' && exit 9 || exit 0

	make test_4x4_gray       2>&1 | tee $(TEMPDIR)/test_4x4_gray.log
	tail -n 1 $(TEMPDIR)/test_4x4_gray.log \
		| grep 'FAIL' && exit 9 || exit 0

	make test_8x8_gray       2>&1 | tee $(TEMPDIR)/test_8x8_gray.log
	tail -n 1 /$(TEMPDIR)/test_8x8_gray.log \
		| grep 'FAIL' && exit 9 || exit 0

	@echo ""
	@echo SUMMARY OF TEST RESULTS
	@echo ==================================================
	@egrep '^00014'                \
	  $(TEMPDIR)/hackdiff_test.log \
	  $(TEMPDIR)/test_4x4_gray_small.log \
	  $(TEMPDIR)/test_8x8_gray_small.log \
	  $(TEMPDIR)/test_4x4_gray.log       \
	  $(TEMPDIR)/test_8x8_gray.log

hackdiff_test:
	cd ../bitstream; \
	decoder/hackdiff.csh \
	  examples/convbw.{bs,bsa} \
	  -cgra examples/cgra_configs/cgra_info_8x8.txt

# TODO can combine all these down to one
# TODO make it look more like other makefile (cgraflow)
test_4x4_gray_small:
# 	@echo ""
# 	@echo TEST $@
# 	@echo Making $@ because of $?
# 	@echo ==================================================
	bitstream=../../bitstream/examples/cd387-good.bs; \
	image=gray_small;              \
	cd $(VERILATOR_TOP);	        \
	./run.csh $(QUIET) -gen top_tb.cpp -oldmem -4x4       \
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output $(TEMPDIR)/$${image}_out.raw   \
	   -nclocks 5M;                     \
        cmp io/$${image}_out.raw $(TEMPDIR)/$${image}_out.raw || echo FAIL

test_4x4_gray:
	bitstream=../../bitstream/examples/cd387-good.bs; \
	image=gray;                    \
	cd $(VERILATOR_TOP);	        \
	./run.csh $(QUIET) -gen top_tb.cpp -oldmem -4x4        \
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output $(TEMPDIR)/$${image}_out.raw   \
	   -nclocks 5M;                     \
        cmp io/$${image}_out.raw $(TEMPDIR)/$${image}_out.raw || echo FAIL

test_8x8_gray_small:
	bitstream=../../bitstream/examples/cd387-newmem-8x8.bs; \
	image=gray_small;              \
	cd $(VERILATOR_TOP);	        \
	./run.csh $(QUIET) -gen top_tb.cpp -usemem -8x8\
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output $(TEMPDIR)/$${image}_out.raw   \
	   -nclocks 5M;                     \
        cmp io/$${image}_out.raw $(TEMPDIR)/$${image}_out.raw || echo FAIL

test_8x8_gray:
	bitstream=../../bitstream/examples/cd387-newmem-8x8.bs; \
	image=gray;                    \
	cd $(VERILATOR_TOP);	        \
	./run.csh $(QUIET) -gen top_tb.cpp -usemem -8x8\
	   -config $${bitstream}          \
	   -input  io/$${image}.png        \
	   -output $(TEMPDIR)/$${image}_out.raw   \
	   -nclocks 5M;                     \
        cmp io/$${image}_out.raw $(TEMPDIR)/$${image}_out.raw || echo FAIL
