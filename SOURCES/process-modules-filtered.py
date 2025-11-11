#!/usr/bin/python3
"""read modules-filtered.lst and update modules.conf

Usage:
  # enable only modules listed in the modules-filtered.lst file
  ./process-modules-filtered.py ../../modules-filtered.lst dist/targeted/modules.conf enabled > policy/modules.conf

  # disable modules listed in the modules-filtered.lst file
  ./process-modules-filtered.py ../../modules-filtered.lst dist/targeted/modules.conf disabled > policy/modules.conf

"""

import sys

modules = []
for line in open(sys.argv[1]):
    if line[0] != "#":
        modules.append(line.strip())


for line in open(sys.argv[2]):
    if len(line) == 1 or line[0] == "#":
        print(line, end='')
        continue

    (name, sep, state) = line.partition(" = ")

    if state.rstrip() == "base":
        print(line, end='')
        continue

    if not name in modules and sys.argv[3] == "enabled":
        print(name, " = off", sep='')
        continue

    if name in modules and sys.argv[3] == "disabled":
        print(name, " = off", sep='')
        continue

    print(line, end='')
