import subprocess
from pe import and_
from testvectors import complete
from verilator import compile

def test_and():
    a = and_()

    tests = complete(a, 4, 16)
    compile('test_pe_comp_unq1',a.opcode,tests)
    assert not subprocess.call("verilator -I../rtl -Wno-fatal --cc test_pe_comp_unq1 --exe sim_test_pe_comp_unq1.cpp", shell=True, cwd="build")
    assert not subprocess.call("make -C obj_dir -j -f Vtest_pe_comp_unq1.mk Vtest_pe_comp_unq1", shell=True, cwd="build")
    assert not subprocess.call("./obj_dir/Vtest_pe_comp_unq1", shell=True, cwd="build")

