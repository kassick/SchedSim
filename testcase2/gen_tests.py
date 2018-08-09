#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File: "gen_tests.py"
# Created: "Sex, 25 Set 2015 16:38:40 -0300 (kassick)"
# Updated: "Sex, 25 Set 2015 17:26:08 -0300 (kassick)"
# $Id$
# Copyright (C) 2015, Rodrigo Virote Kassick <rvkassick@inf.ufrgs.br>

import random
import sys
import os

def gen_bursts(n_bursts, min_cpu, max_cpu, min_io, max_io):
    bursts = []
    for x in range(0, n_bursts):
        cpu = random.randint(min_cpu, max_cpu)
        io = random.randint(min_io, max_io)
        bursts.append(cpu)
        bursts.append(io)
    return bursts[:-1]

def write_bursts(procs):
    for (id, bursts) in procs:
        with open("proc_%d.dat" % id, 'w+') as fh:
            fh.writelines([str(int(len(bursts)/2)) + '\n'])
            fh.writelines(map(lambda b: "%d\n" % b, bursts))

write_bursts((((i, gen_bursts(10, 9, 39, 500, 5000))
               for i in range(0, 4))) )

write_bursts((((i, gen_bursts(10, 100, 1000, 50, 150))
               for i in range(4, 7))) )

write_bursts((((i, gen_bursts(10, 5, 19, 500, 5000))
               for i in range(7, 10))) )

