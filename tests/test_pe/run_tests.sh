#!/bin/bash

# Generate the latest pe
pushd ../../hardware/generator_z/pe_new/pe/gen
./run_genesis.sh
popd

pytest
