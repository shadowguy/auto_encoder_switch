#!/bin/bash
export PSPKG_ROOT=/reg/g/pcds/pkg_mgr
export PSPKG_RELEASE="controls-0.1.9"
source $PSPKG_ROOT/etc/set_env.sh

python autoEncoder.py $@
