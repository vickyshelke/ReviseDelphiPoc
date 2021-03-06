#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       buffer.py
#
import os
import ConfigParser
logConfig = ConfigParser.ConfigParser()
logConfig.readfp(open(r'logConfig.txt'))
BUFFER_SIZE = logConfig.get('log-config', 'BUFFER_SIZE')
FILENAME="BUFFER"
if BUFFER_SIZE > 10000:
        print "size of buffer excedded setting it to default"
        BUFFER_SIZE = 10000
def string_conditioned(string):
    return string.decode('string_escape').rstrip() + '\n'
def pop():
    if os.stat(FILENAME).st_size > 0:
        with open(FILENAME, 'r+U') as fd:
            rows = fd.readlines()
        with open(FILENAME, 'w') as fd:
            n = int(1)
            fd.writelines(rows[n:])
            return ''.join(rows[:n])
    else:
        return "-1"
def trim_buffer(row):
    size = int(BUFFER_SIZE)
    with open(FILENAME, 'rU') as fd:
        rows = fd.readlines()
    num_rows = len(rows)
    if num_rows >= size:
        n = string_conditioned(row).count('\n')
#        pop(num_rows + n - size)
        pop()
def push(row):
    trim_buffer(row)
    with open(FILENAME, 'a') as fd:
        fd.write(string_conditioned(row))
    return ''
#Use push("shelke") print (pop().rstrip())
