#!/usr/bin/python3
import os
import sys


file = sys.argv[1]

base = os.path.basename(file)
dirname = os.path.dirname(file)

newBase = base.replace('-mk4', '')
newFile = os.path.join(dirname, newBase)

os.rename(file, newFile)