#!/usr/bin/env python3

#
# Copyright 2016 riteme
#

import os
import sys
import time

import threading


def info(message):
    print("\033[32m(info)\033[0m {}".format(message))

def warning(message):
    print("\033[33m(warn)\033[0m {}".format(message))

def error(message):
    print("\033[31m(error)\033[0m {}".format(message))

try:
    import psutil
except:
    warning("psutil not installed. Memory states will not be watched.")


class Compiler(object):
    """Represent a compiler"""
    def __init__(self, name, args, output_opt="-o"):
        super(Compiler, self).__init__()

        assert type(args) is list, "args must be a list"

        self.name = name
        self.args = args
        self.output_option = output_opt
    
    def compile(self, file, output="a.out"):
        status = os.system(
            "{compiler} {args} {input} {output_opt} {output}".format(
                compiler=self.name,
                args=" ".join(self.args),
                input=file,
                output_opt=self.output_option,
                output=output
            )
        )

        if status != 0:
            raise RuntimeError("Can't compile file: {}".format(file))


class Timer(object):
    """A simple timer"""
    def __init__(self):
        super(Timer, self).__init__()
        self.current = time.time()

    def restart(self):
        self.current = time.time()

    def tick(self):
        now = time.time()
        span = now - self.current

        return span


class MemoryWatcher(object):
    """Watch for memory usage"""
    def __init__(self, timespan=0.016):
        super(MemoryWatcher, self).__init__()
        self.pid = 0
        self.max = 0.0
        self.timespan = timespan

    def _main(self):
        try:
            proc = psutil.Process(self.pid)
        except:
            warning("Memory watcher will not work.")
            return

        while self._flag:
            try:
                meminfo = proc.memory_info()
                self.max = max(self.max, meminfo.vms)

                time.sleep(self.timespan)

            except:
                return

    def start(self, pid):
        self.pid = pid
        self._flag = True
        self._thread = threading.Thread(
            target = MemoryWatcher._main,
            name = "Memory Watcher",
            args = (self, )
        )
        self._thread.start()

    def stop(self, wait=True):
        self._flag = False

        if wait:
            self._thread.join()

    def get_history_max(self):
        return self.max

    def reset(self):
        self.max = 0.0

if __name__ == "__main__":
    t = Timer()
    t.restart()

    time.sleep(0.5222)
    print(t.tick())
