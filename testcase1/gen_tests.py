#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File: "gen_tests.py"
# Created: "Sex, 25 Set 2015 16:38:40 -0300 (kassick)"
# Updated: "Sex, 25 Set 2015 16:56:08 -0300 (kassick)"
# $Id$
# Copyright (C) 2015, Rodrigo Virote Kassick <rvkassick@inf.ufrgs.br>

import random
import sys
import os

def gen_cpu_bound():
    bursts = []
    for x in range(0, 10):
        cpu = random.randint(1, 10)
        io = random.randint(500, 5000)
        bursts.append(cpu)
        bursts.append(io)
    return bursts[:-1]

def gen_io_bound():
    bursts = []
    for x in range(0, 100):
        cpu = random.randint(50, 500)
        io = random.randint(500, 5000)
        bursts.append(cpu)
        bursts.append(io)
    return bursts[:-1]

for pid in range(0, 5):
    bursts = gen_cpu_bound()
    with open("proc_%d.dat" % pid, 'w+') as fh:
        fh.writelines([str(int(len(bursts)/2)) + '\n'])
        fh.writelines(map(lambda b: "%d\n" % b, bursts))

for pid in range(5, 10):
    bursts = gen_io_bound()
    with open("proc_%d.dat" % pid, 'w+') as fh:
        fh.writelines([str(int(len(bursts)/2)) + '\n'])
        fh.writelines(map(lambda b: "%d\n" % b, bursts))

