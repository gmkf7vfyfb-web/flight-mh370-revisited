#!/bin/bash
# usage: launch.sh <logname> <args...>
cd ~/imos-noise
if ps -eo args | grep -v grep | grep -q "python imos_deploy_noise.py"; then echo RUNNING; exit 0; fi
name=$1; shift
setsid nohup venv/bin/python imos_deploy_noise.py --cfg cfg.json "$@" > $name.out 2>&1 < /dev/null &
echo launched $!
