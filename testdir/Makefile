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

TEMPDIR := $(shell mktemp -d /tmp/gentest-XXX)

# gray_small_4x4:
# 	make test TEMPDIR=$(TEMPDIR) IMAGE="gray_small" \
# 	CONFIG="-oldmem -4x4 -config ../../bitstream/examples/cd387-good.bs"
# 
# gray_4x4:
# 	make test TEMPDIR=$(TEMPDIR) IMAGE="gray" \
# 	CONFIG="-oldmem -4x4 -config ../../bitstream/examples/cd387-good.bs"

pw_gray_small_8x8:
	make test TEMPDIR=$(TEMPDIR) IMAGE="gray_small" \
	CONFIG="-config ../../bitstream/examples/pwv2.bs"

pw_gray_8x8:
	make test TEMPDIR=$(TEMPDIR) IMAGE="gray" \
	CONFIG="-config ../../bitstream/examples/pwv2.bs"

test_all:
	make test_standalone
	make test_serpent

        # Read standalone test result(s) from 'log1'
	@echo ""
	@echo SUMMARY OF STANDALONE TEST RESULTS
	@echo ==================================================
	./writelog.csh log1 -print

        # Summary of hackdiff results
	egrep ^hackdiff $(TEMPDIR)/hackdiff_test.log


test_serpent:
	../bitstream/bsbuilder/testdir/make_bitstreams.csh $(TEMPDIR)
	../bitstream/bsbuilder/testdir/test_bitstreams.csh $(TEMPDIR)
#	FIXME Who will delete TEMPDIR?

test_standalone:
	pwd; ls
	./writelog.csh log1 -init TEST SUMMARY BEGIN `date`
	make hackdiff_test | tee $(TEMPDIR)/hackdiff_test.log

        # Note: Results go to 'log1'
	make pw_gray_small_8x8
#	make pw_gray_8x8
# 	# make gray_small_4x4
# 	# make gray_4x4

# Probably want to restore the more-challenging conv_bw test, once smoke has cleared.
# hackdiff_test:
# 	cd ../bitstream; \
# 	decoder/hackdiff.csh \
# 	  examples/conv_bw.bs examples/conv_bw.bsa \
# 	  -cgra examples/cgra_configs/cgra_info_8x8.txt

hackdiff_test:
	cd ../bitstream; \
	decoder/hackdiff.csh \
	  examples/pw351.bs examples/pw351.bsa \
	  -cgra examples/cgra_configs/cgra_info_new.txt



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

	cmp $(VERILATOR_TOP)/io/$(IMAGE)_out.raw $(TEMPDIR)/$(IMAGE)_out.raw      \
		&& ./writelog.csh log1 PASSED `date +%R` test $(IMAGE) \
		|| ./writelog.csh log1 FAILED `date +%R` test $(IMAGE)

	cd $(VERILATOR_TOP);\
	cmp io/$(IMAGE)_out.raw $(TEMPDIR)/$(IMAGE)_out.raw

