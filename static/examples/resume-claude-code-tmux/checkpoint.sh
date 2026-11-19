#!/usr/bin/env bash
set -eu
printf 'start\n' > progress.log
sleep 8
printf '42\n' > result.txt
printf 'ready\n' >> progress.log
