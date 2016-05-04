#!/usr/bin/env python3

#
# Copyright 2016 riteme
#

import os
import sys
import time


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
        span = int((now - self.current) * 1000)

        return span

if __name__ == "__main__":
    t = Timer()
    t.restart()

    time.sleep(0.5222)
    print(t.tick())
