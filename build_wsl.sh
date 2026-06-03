#!/bin/bash
export PATH=$HOME/.local/bin:/usr/bin:/usr/local/bin:/usr/sbin
cd $HOME/find_my_car
python3 -m buildozer android debug 2>&1
