#!/usr/bin/env python3

#
# Copyright 2016 riteme
#

import os
import sys
import time

import imp
import shutil
import threading
import subprocess


def info(message):
    print("\033[32m(info)\033[0m {}".format(message))

def warning(message):
    print("\033[33m(warn)\033[0m {}".format(message))

def error(message):
    print("\033[31m(error)\033[0m {}".format(message))

try:
    import psutil
except:
    warning("psutil is not installed. Memory states will not be watched.")


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
        except Exception as e:
            warning("Memory watcher will not work. Maybe the program has already exited.")
            warning(str(e))
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
        return self.max / (1024 ** 2)

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
UNKNOWN = -2


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
        self.returncode = 0
        self.source = ""
        self.compiled = ""
        self.source_extension = ""
        self.input_filename = ""
        self.output_filename = ""
        self.standard_input = ""
        self.standard_output = ""
        self.user_output = ""
        self.score = 10
        self.status = UNKNOWN
        self.message = ""


class Judger(object):
    """The core part of a single judgement"""
    def __init__(self, testcase,
                       timer,
                       memory_watcher,
                       checker
                ):
        super(Judger, self).__init__()
        self.testcase = testcase
        self.timer = timer
        self.memory_watcher = memory_watcher
        self.checker = checker

    def judge(self):
        try:
            # Copy input data
            shutil.copy2(
                self.testcase.standard_input,
                self.testcase.input_filename
            )

            # Update output file
            self.testcase.user_output = self.testcase.output_filename

            # Preparations
            self.memory_watcher.reset()

            # Run it
            proc = subprocess.Popen(
                ["./{}".format(self.testcase.compiled)]
            )

            # Start memory watcher
            self.memory_watcher.start(proc.pid)

            # Start timer
            self.timer.restart()

            try:
                # Wait for exit
                proc.wait(timeout = self.testcase.time_limit)
            except subprocess.TimeoutExpired:
                pass

            # Get running time
            self.testcase.time = self.timer.tick()

            # Get memory usage
            self.memory_watcher.stop()
            self.testcase.memory = self.memory_watcher.get_history_max()

            # Get returncode
            self.testcase.returncode = proc.returncode

            # Check if the program exit with no error
            if self.testcase.time > self.testcase.time_limit:
                self.testcase.status = TIME_LIMIT_EXCEEDED
            elif self.testcase.memory > self.testcase.memory_limit:
                self.testcase.status = MEMORY_LIMIT_EXCEEDED
            elif self.testcase.returncode != 0:
                self.testcase.status = RUNTIME_ERROR

            # Check the answer
            if self.testcase.status == UNKNOWN:
                self.testcase.status = self.checker.check(
                    self.testcase
                )

        except Exception as e:
            self.testcase.status = INTERNAL_ERROR
            raise e


if __name__ == "__main__":
    t = Testcase()
    t.time_limit = 1.0
    t.memory_limit = 64.0
    t.source = "a/a.cpp"
    t.compiled = "exec"
    t.input_filename = "a.in"
    t.output_filename = "a.out"
    t.standard_input = "a/a.in"
    t.standard_output = "a/a.out"
    t.score = 100

    compiler = Compiler("g++", args = ["-static"])
    compiler.compile("a/a.cpp", output = "exec")

    timer = Timer()
    memory_watchdog = MemoryWatcher()
    checker = Checker("a")
    judger = Judger(t, timer, memory_watchdog, checker)
    judger.judge()

    print(t.time, t.memory, t.returncode, t.status, t.message)
