#!/bin/bash
export PSPKG_ROOT=/reg/common/package
export PSPKG_RELEASE=controls-0.0.8
source $PSPKG_ROOT/etc/set_env.sh

python autoEncoder.py $@
