from __future__ import print_function
import pprint
import subprocess
import time
import tty
import unittest

import pyutmp


def tty():
    p = subprocess.Popen("tty", stdout=subprocess.PIPE)
    p.wait()
    if p.returncode != 0:
        raise Exception("tty(1) failed")
    return p.stdout.readlines()[0].strip()


class TestPyutmp(unittest.TestCase):
    def test_ut_user_process(self):
        f = pyutmp.UtmpFile()
        for u in f:
            if u.ut_user_process:
                print(
                    "%s %s (%s) from %s"
                    % (time.ctime(u.ut_time), u.ut_user, u.ut_line, u.ut_host)
                )

    def test_print_all(self):
        for f in pyutmp.UtmpFile():
            assert f.__dict__
            pprint.pprint(f.__dict__)
