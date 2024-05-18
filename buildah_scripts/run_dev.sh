#!/usr/bin/bash

cd /usr/local/src
pip3 install -e xraygui/livetable
pip3 install -e xraygui/nbs_core
pip3 install -e nsls-ii-sst/sst_gui/src

tail -f /dev/null
