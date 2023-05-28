#!/usr/bin/python3
import os
import re
import sys

#plus or minus
increment = sys.argv[1]
if increment == "plus":
    print("Plus")
    increment = 1
elif increment == "minus":
    print("Minus")
    increment = -1
else:
    print("Argument not correct.")

file = open("config.ini", 'r')
lines = file.readlines()
file.close()

newLines = []
for line in lines:
    if "CRF = " in line:
        numMatch = re.match(r"CRF = (\d+)", line)
        newNum = int(numMatch.groups()[0]) + increment
        line = re.sub(r"CRF = (\d+)", f"CRF = {newNum}", line)
    newLines.append(line)


os.remove("config.ini")
file = open("config.ini", "w")
file.writelines(newLines)
file.close()