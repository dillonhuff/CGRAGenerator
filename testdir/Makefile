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
# $(warning OUTPUT = "$(OUTPUT)")

TEMPDIR := $(shell mktemp -d)

# gray_small_4x4:
# 	make test TEMPDIR=$(TEMPDIR) IMAGE="gray_small" \
# 	CONFIG="-oldmem -4x4 -config ../../bitstream/examples/cd387-good.bs"
# 
# gray_4x4:
# 	make test TEMPDIR=$(TEMPDIR) IMAGE="gray" \
# 	CONFIG="-oldmem -4x4 -config ../../bitstream/examples/cd387-good.bs"

gray_small_8x8:
	make test TEMPDIR=$(TEMPDIR) IMAGE="gray_small" \
	CONFIG="-usemem -config ../../bitstream/examples/pointwise_handcrafted.bs"
# 	CONFIG="-usemem -8x8 -config ../../bitstream/examples/cd387-newmem-8x8.bs"

gray_8x8:
	make test TEMPDIR=$(TEMPDIR) IMAGE="gray" \
	CONFIG="-usemem -config ../../bitstream/examples/pointwise_handcrafted.bs"
# 	CONFIG="-usemem -8x8 -config ../../bitstream/examples/cd387-newmem-8x8.bs"

test_all:
#	echo TEST SUMMARY > $(TEMPDIR)/test_summary.txt
#	echo BEGIN `date` >> $(TEMPDIR)/test_summary.txt
	pwd; ls
	./writelog.csh log1 -init TEST SUMMARY
	./writelog.csh log1 BEGIN `date`
	make hackdiff_test | tee $(TEMPDIR)/hackdiff_test.log

#         # Note the '| tee' masks any errors that might have occurred :(
# 	make TEMPDIR=$(TEMPDIR) test_4x4_gray_small
# 	make TEMPDIR=$(TEMPDIR) test_8x8_gray_small
# 	make TEMPDIR=$(TEMPDIR) test_4x4_gray
# 	make TEMPDIR=$(TEMPDIR) test_8x8_gray

	make gray_small_8x8
	make gray_8x8
	# make gray_small_4x4
	# make gray_4x4

	@echo ""
	@echo SUMMARY OF TEST RESULTS
	@echo ==================================================
#	cat $(TEMPDIR)/test_summary.txt
	./writelog.csh log1 -print

# 	@egrep '^00014'                \
# 	  $(TEMPDIR)/hackdiff_test.log \
# 	  $(TEMPDIR)/test_4x4_gray_small.log \
# 	  $(TEMPDIR)/test_8x8_gray_small.log \
# 	  $(TEMPDIR)/test_4x4_gray.log       \
# 	  $(TEMPDIR)/test_8x8_gray.log

hackdiff_test:
	cd ../bitstream; \
	decoder/hackdiff.csh \
	  examples/conv_bw.bs examples/conv_bw.bsa \
	  -cgra examples/cgra_configs/cgra_info_8x8.txt

# TODO can combine all these down to one
# TODO make it look more like other makefile (cgraflow)


test:
	@echo ""
	@echo "------------------------------------------------------------------------"
	@echo "BEGIN TEST"
	@echo "------------------------------------------------------------------------"

	cd $(VERILATOR_TOP);\
	./run.csh $(QUIET) -gen top_tb.cpp  \
	   $(CONFIG)                         \
	   -input  io/$(IMAGE).png            \
	   -output $(TEMPDIR)/$(IMAGE)_out.raw \
	   -delay 0,0 \
	   -nclocks 5M || echo FAIL

# 	cd $(VERILATOR_TOP);\
# 	cmp io/$(IMAGE)_out.raw $(TEMPDIR)/$(IMAGE)_out.raw      \
# 		&& echo $@ PASSED  >> $(TEMPDIR)/test_summary.txt \
# 		|| echo $@ FAILED  >> $(TEMPDIR)/test_summary.txt;

	cmp $(VERILATOR_TOP)/io/$(IMAGE)_out.raw $(TEMPDIR)/$(IMAGE)_out.raw      \
		&& ./writelog.csh log1 $@ PASSED
		|| ./writelog.csh log1 $@ FAILED



	cd $(VERILATOR_TOP);\
	cmp io/$(IMAGE)_out.raw $(TEMPDIR)/$(IMAGE)_out.raw

