#!/usr/bin/env python3
import time
import sys

for x in range(10):
    print(x)
    time.sleep(0.5)
    sys.stdout.flush()