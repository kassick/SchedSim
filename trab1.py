#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File: "trab1.py"
# Created: "Qui, 24 Set 2015 14:57:44 -0300 (kassick)"
# Updated: "2018-08-09 18:21:18 kassick"
# $Id$
# Copyright (C) 2015, Rodrigo Virote Kassick <rvkassick@inf.ufrgs.br>
#
#

""" Trabalho 1 -- Implementação KASSICK

Usage:
    trab1.py [-n nprocs] [-d testdir]

Options:
    -n nprocs       Number of processes [default: 2]
    -d testdir      Directory where to find the test files [default: ./]
"""

import os
import sys
import os.path
import time
import docopt

class Process:
    STATUS_READY = 0
    STATUS_BLOCKED = 1
    STATUS_FINISHED = 2

    def __init__(self, id):
        '''
        Creates a new process
        '''
        self.id = id
        self.status = Process.STATUS_READY
        self.n_cpu_burst = 0
        self.n_io_burst = 0
        self.cpu_bursts = []
        self.io_bursts = []
        self.cur_cpu_burst = 0
        self.cur_io_burst = 0

        # Blocked time management
        self.time_before_wakeup = 0

        self.sched_info = None

        self.load_bursts()

    def __str__(self):
        r = "Proc " + str(self.id)
        if self.status == Process.STATUS_READY:
            r += " READY for more: %d" % self.cpu_bursts[self.cur_cpu_burst]
        elif self.status == Process.STATUS_BLOCKED:
            r += " BLOCKED for more %d" % self.time_before_wakeup
        else:
            r += " FINISHED"
        return r

    def __repr__(self):
        return self.__str__()

    def load_bursts(self):
        '''
        Loads the bursts from a set of files

        File Format is:
        n_cpu_bursts
        cpu_burst_0
        io_burst_0
        cpu_burst_1
        io_bust_1
        ...
        cpu_burst_<n>
        '''

        fname = "proc_%d.dat" % self.id
        try:
            lines = open(fname).readlines()
        except:
            print("Ooops, file %s missing" % fname)
            sys.exit(1)

        # Wouldn't need to read a n_cpu_bursts in python,
        # but I suggested my students had the number of cpu bursts in the first
        # line in case they didn't use something as handy as readlines()
        n_bursts = int(lines[0])
        remaining = lines[1:]

        if not(2*n_bursts - 1 == len(remaining)):
            print("Odd file %s has not the correct header" % fname)

        cpu_bursts = [int( remaining[i] )
                      for i in range(0, len(remaining))
                      if (i % 2) == 0 ]

        io_bursts = [int( remaining[i] )
                     for i in range(0, len(remaining))
                     if (i % 2) == 1 ]

        if len(io_bursts) != len(cpu_bursts) - 1:

            print("File %s is very wrong, aborting" % fname)
            sys.exit(1)

        self.io_bursts = io_bursts
        self.n_io_burst = len(io_bursts)
        self.cpu_bursts = cpu_bursts
        self.n_cpu_burst = len(cpu_bursts)

    def do_procs(self, quanta):
        '''
        Called by the "fake scheduler" to give the cpu for this process for no more than quanta time units

        @type quanta : int
        @rtype: tuple(int, int)
        '''

        time_in_cpu = min( self.cpu_bursts[self.cur_cpu_burst], quanta )

        print("\tProcess %d in CPU with quanta=%d, will remain %d" % (self.id,
                                                                      quanta,
                                                                      time_in_cpu))

        # time.sleep(time_in_cpu / 100.0) # sleep miliseconds

        self.cpu_bursts[self.cur_cpu_burst] -= time_in_cpu

        if (self.cpu_bursts[self.cur_cpu_burst] <= 0):
            # Block/finish this processes
            self.cur_cpu_burst += 1

            if self.cur_cpu_burst == self.n_cpu_burst:
                # process exit()s
                self.status = Process.STATUS_FINISHED
                return (0, time_in_cpu)
            else:
                # process blocks
                self.status = Process.STATUS_BLOCKED
                self.time_before_wakeup = self.io_bursts[self.cur_io_burst]
                self.cur_io_burst += 1
                return (-1, time_in_cpu)
            pass
        else:
            # process expires
            return (1, time_in_cpu)
        pass
    pass


class SchedInfo:
    '''
    Information used by the scheduler
    '''
    def __init__(self):
        self.n_quanta_finished = 0
        self.n_quanta_unfinished = 0
        self.last_queue = None

        # Accounting
        self.waiting_time = 0
        self.executing_time = 0
        self.blocked_time = 0
        self.last_blocked = 0
        self.last_in_cpu = 0

class NamedList(list):
    '''
    A list with a name

    str from this list returns "Name: [elem1, elem2, ...]"
    '''

    def __init__(self, name, iterable=None):
        '''
        ctor(name, iterable)
        '''

        if iterable:
            list.__init__(self, iterable)
        else:
            list.__init__(self)
        self.name = name

    def __str__(self):
        '''
        Returns "Name: [elem1, elem2, ...]"
        '''
        return "%s: %s" % (self.name,
                           list.__str__(self))


class Scheduler:
    '''
    Class responsible for the scheduling
    '''
    def __init__(self, ready_list):
        '''
        Initializes everything

        @type ready_list: [Process]
        '''

        self.all_processes = ready_list
        self.rr10_queue = NamedList("RR-10", ready_list)
        self.rr20_queue = NamedList("RR-20")
        self.fifo_queue = NamedList("FIFO")
        self.global_clock = 0
        for proc in self.all_processes:
            proc.sched_info = SchedInfo()
            proc.sched_info.last_queue = self.rr10_queue


    def sched(self):
        ''' Scheduler decision: picks on of the processes and gives some time in
        the CPU according to the queue
        '''

        if len(self.rr10_queue) != 0:
            # Round-robin 10 queue has more priority
            proc = self.rr10_queue.pop(0)
            return (proc, self.rr10_queue, 10)
        elif len(self.rr20_queue) != 0:
            # Round-robin 20 queue
            proc = self.rr20_queue.pop(0)
            return (proc, self.rr20_queue, 20)
        elif len(self.fifo_queue) != 0:
            proc = self.fifo_queue.pop(0)
            return (proc, self.fifo_queue,
                          36893488147419103232) # this should make sure we
                                                 # execute ``forever´´
        else:
            return (None, None, -1)

    def wakeup(self, proc):
        """
        Wakes up a process
        """

        blocked_time = self.global_clock - proc.sched_info.last_blocked
        proc.sched_info.blocked_time += blocked_time

        # Zero the criteria for demotion and promotion, as the rule
        # is for time IN QUEUE and number of slices used IN QUEUE
        proc.sched_info.n_quanta_finished = 0
        proc.sched_info.last_in_cpu = self.global_clock
        proc.sched_info.last_queue.append(proc)
        proc.status = Process.STATUS_READY

        print("\tProcess", proc.id, "woke up")

    def block(self, proc):
        '''
        blocks a process
        '''

        proc.sched_info.last_blocked = self.global_clock
        proc.sched_info.n_quanta_unfinished += 1
        print("\tProcess", proc.id, "blocked")

    def wakeup_blocked_processes(self, timestep):
        '''
        Wakes up any process that has already finished
        '''

        to_wakeup = []
        for p in self.all_processes:
            # Process needs to be blocked and not blocked RIGHT NOW
            # If I don't filter out the very last executing process, I'll
            # take out the time from the last cpu burst as if it had really
            # executed
            if (p.status == Process.STATUS_BLOCKED) \
                    and (p.sched_info.last_in_cpu != self.global_clock):
                # Discount the timestep
                p.time_before_wakeup -= timestep

                # We'll have to wake up this one
                if p.time_before_wakeup <= 0:
                    to_wakeup.append(p)

        for p in to_wakeup:
            self.wakeup(p)

    def do_ageing(self):
        '''
        Age processes that remained for more then 100 time-units in a queue
        Move them up one queue
        '''

        queues = [self.rr10_queue, self.rr20_queue, self.fifo_queue ]
        for dest, q in zip(queues, queues[1:]):
            # Migrate any process in q if it spent more than 100 time-units
            # without cpu
            crit = lambda p: (self.global_clock - p.sched_info.last_in_cpu) > 100
            procs = list(filter(crit, q))
            if len(procs) > 0:
                for p in procs:
                    print("\tProcess", p.id, "migrated:",
                          q.name, "----->", dest.name)
                    # Zero the criteria for demotion and promotion, as the rule
                    # is for time IN QUEUE and number of slices used IN QUEUE
                    p.sched_info.n_quanta_finished = 0
                    p.sched_info.last_in_cpu = self.global_clock

                    q.remove(p)
                    dest.append(p)
                    p.sched_info.last_queue = dest

    def do_demotion(self):
        '''
        Demote processes that used all their quanta at least twice.
        Move them one queue down
        '''

        queues = [self.rr10_queue, self.rr20_queue, self.fifo_queue ]
        for q, dest in zip(queues, queues[1:]):
            # Migrate any process in q if it spent more than 100 time-units
            # without cpu
            crit = lambda p: p.sched_info.n_quanta_finished >= 2
            procs = list(filter(crit, q))
            if len(procs) > 0:
                for p in procs:
                    print("\tProcess", p.id, "migrated:",
                          q.name, "----->", dest.name)
                    # Zero the criteria for demotion and promotion, as the rule
                    # is for time IN QUEUE and number of slices used IN QUEUE
                    p.sched_info.n_quanta_finished = 0
                    p.sched_info.last_in_cpu = self.global_clock

                    q.remove(p)
                    dest.append(p)
                    p.sched_info.last_queue = dest

    def run_sim(self):
        '''
        Runs the simulation while the processes have not finished
        '''

        last_sched = self.global_clock
        proc, queue, quanta = self.sched()

        while proc != None:
            print("At", self.global_clock,
                "Scheduler selected proc", proc.id,
                "from queue", queue.name,
                "for", quanta, "time-units")

            #print(self.rr10_queue)
            #print(self.rr20_queue)
            #print(self.fifo_queue)

            # Dispatch to the process
            (ret, used_time) = proc.do_procs(quanta)
            # print("Proc", proc.id, "used ", used_time, "returned", ret)

            # Advance global clock
            self.global_clock += used_time

            # Account for time *executing*
            proc.sched_info.last_in_cpu = self.global_clock
            proc.sched_info.executing_time += used_time

            # Account for time in queue
            # Last selected process does not increase waiting time as it is not
            # back in any queue
            for q in [ self.rr10_queue, self.rr20_queue, self.fifo_queue ]:
                for p in q:
                    p.sched_info.waiting_time += used_time

            self.wakeup_blocked_processes(used_time)

            if (ret == 0):
                #process finished
                print("At %d process %d finished" % (self.global_clock, proc.id))
            elif (ret == -1):
                print("At %d process %d blocked for %d " % (self.global_clock,
                                                            proc.id,
                                                            proc.time_before_wakeup))
                self.block(proc)
            else:
                # REQUEUE
                print("At %d process %d used all it's timeslice" % (self.global_clock, proc.id))
                proc.sched_info.n_quanta_finished += 1
                queue.append(proc)

            # Age process in the queue
            self.do_ageing()

            # Demote over-eager processes
            self.do_demotion()

            # If there are no processes in queue,
            # this either means that all processes are FINISHED
            # or that all non-finished are BLOCKED
            if len(self.rr10_queue) == 0 and \
                    len(self.rr20_queue) == 0 and\
                    len(self.fifo_queue) == 0:
                # Find the first blocked process that will wake up
                blocked = filter(lambda p: p.status == Process.STATUS_BLOCKED,
                                 self.all_processes)
                sorted_blocked = sorted(blocked, key = lambda p: p.time_before_wakeup)
                #print(sorted_blocked)
                if len(sorted_blocked) > 0:
                    print("\tAll processes are blocked, I'll jump in time!")
                    time_to_jump = sorted_blocked[0].time_before_wakeup
                    self.global_clock += time_to_jump
                    self.wakeup_blocked_processes(time_to_jump) # This should wake only one

            last_sched = self.global_clock
            proc, queue, quanta = self.sched()

            #self.print_stats()
            pass

    def print_stats(self):
        print("------------------------------------------------------------------------------")
        for p in self.all_processes:
            print("Process", p.id,
                  p.sched_info.executing_time, "tu in CPU,",
                  p.sched_info.waiting_time, "tu in queues",
                  " Last queue:", p.sched_info.last_queue.name)


def main():
    options = docopt.docopt(__doc__, version="Vers 1.0")
    n_procs = int(options['-n'])
    testdir = options['-d']

    if not(os.path.exists(testdir)):
        print("Error: non-existant test dir", testdir)
        sys.exit(1)

    print("Changing into directory", testdir)

    os.chdir(testdir)

    procs = [ Process(i) for i in range(0, n_procs) ]

    print(procs)

    s = Scheduler(procs)
    print(s.rr10_queue)
    s.run_sim()
    s.print_stats()

if __name__ == "__main__":
    main()
