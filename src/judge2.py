#!/usr/bin/env python3

#
# Copyright 2016 riteme
#

import os
import sys
import time

import imp
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


class Checker(object):
    """Respresent a checker"""
    def __init__(self, path, checker_name="checker"):
        super(Checker, self).__init__()
        self.path = path
        file, pathname, description = imp.find_module(
            checker_name,
            path = [os.path.abspath(path)]
        )

        if file is None:
            raise ImportError("No checker found")

        try:
            self._checker = imp.load_module(
                checker_name,
                file, pathname, description
            )
        except Exception as e:
            raise e

    def check(self, testcase):
        checker = self._checker.Checker(testcase)

        return min(checker.check())


class Sandbox(object):
    """Sandbox is designed for safety"""

    SANDBOX_SOURCE = """
    import os

    os.chroot("{location}")
    os.system("{target}")
    """

    def __init__(self, location="/tmp/judge", entrance="exec.py"):
        super(Sandbox, self).__init__()
        self.location = os.path.abspath(location)
        
        if not os.path.exist(self.location):
            os.mkdir(self.location)

        self.entrance = os.path.join(self.location, entrance)
        with open(self.entrance) as f:
            f.write(
                Sandbox.SANDBOX_SOURCE.format(
                    location = self.location,
                    target = "./{}".format(entrance)
                )
            )


class Testcase(object):
    """Store states of a testcase's judgement"""
    def __init__(self):
        super(Testcase, self).__init__()
        
        self.id = 0
        self.name = ""
        self.compiler = None
        self.time = 0.0
        self.time_limit = 0.0
        self.memory = 0.0
        self.memory_limit = 0.0
        self.return_code = 0
        self.source = ""
        self.compiled = ""
        self.source_extension = ""
        self.standard_input = ""
        self.standard_output = ""
        self.user_output = ""
        self.score = 10


# Final status of judgement
ACCEPTED = 0
TIME_LIMIT_EXCEEDED = 1
MEMORY_LIMIT_EXCEEDED = 2
RUNTIME_ERROR = 3
OUTPUT_LIMIT_EXCEEDED = 4
ACCEPTABLE = 5
WRONG_ANSWER = 6
JUDGEMENT_ERROR = 7
INTERNAL_ERROR = -1

if __name__ == "__main__":
    c = Checker("test")
    print(c.check(Testcase))
