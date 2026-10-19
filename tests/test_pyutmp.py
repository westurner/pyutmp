import ctypes
import sys
import tempfile
import unittest
from pathlib import Path

import pyutmp


class _ExitStatus(ctypes.Structure):
    _fields_ = [
        ("e_termination", ctypes.c_short),
        ("e_exit", ctypes.c_short),
    ]


class _Timeval(ctypes.Structure):
    _fields_ = [
        ("tv_sec", ctypes.c_int32),
        ("tv_usec", ctypes.c_int32),
    ]


class _LinuxUtmpRecord(ctypes.Structure):
    _fields_ = [
        ("ut_type", ctypes.c_short),
        ("ut_pid", ctypes.c_int),
        ("ut_line", ctypes.c_char * 32),
        ("ut_id", ctypes.c_char * 4),
        ("ut_user", ctypes.c_char * 32),
        ("ut_host", ctypes.c_char * 256),
        ("ut_exit", _ExitStatus),
        ("ut_session", ctypes.c_int32),
        ("ut_tv", _Timeval),
        ("ut_addr_v6", ctypes.c_int32 * 4),
        ("__glibc_reserved", ctypes.c_char * 20),
    ]


def _record(
    record_type=7,
    pid=1234,
    line=b"pts/7",
    user=b"alice",
    host=b"remote.example",
    timestamp=1700000000,
    address=0x01020304,
):
    record = _LinuxUtmpRecord()
    record.ut_type = record_type
    record.ut_pid = pid
    record.ut_line = line
    record.ut_id = b"7"
    record.ut_user = user
    record.ut_host = host
    record.ut_exit.e_exit = 5
    record.ut_session = 42
    record.ut_tv.tv_sec = timestamp
    record.ut_addr_v6[0] = address
    return record


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux utmp layout")
class TestUtmpFile(unittest.TestCase):
    def write_records(self, path, records):
        path.write_bytes(b"".join(bytes(record) for record in records))

    def test_empty_file_has_no_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "utmp"
            path.write_bytes(b"")

            self.assertEqual(list(pyutmp.UtmpFile(str(path))), [])

    def test_reads_user_and_system_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "utmp"
            self.write_records(
                path,
                [
                    _record(),
                    _record(
                        record_type=2,
                        pid=0,
                        line=b"",
                        user=b"",
                        host=b"",
                    ),
                ],
            )

            user, boot = list(pyutmp.UtmpFile(str(path)))

        self.assertEqual(user.ut_type, "USER_PROCESS")
        self.assertTrue(user.ut_user_process)
        self.assertEqual(user.ut_pid, 1234)
        self.assertEqual(user.ut_line, "/dev/pts/7")
        self.assertEqual(user.ut_id, "7")
        self.assertEqual(user.ut_user, "alice")
        self.assertEqual(user.ut_host, "remote.example")
        self.assertEqual(user.ut_exit_code, 5)
        self.assertEqual(user.ut_time, 1700000000.0)
        self.assertEqual(user.ut_addr, 0x01020304)

        self.assertEqual(boot.ut_type, "BOOT_TIME")
        self.assertFalse(boot.ut_user_process)
        self.assertIsNone(boot.ut_line)
        self.assertIsNone(boot.ut_user)
        self.assertIsNone(boot.ut_host)

    def test_rewind_restarts_iteration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "utmp"
            self.write_records(path, [_record()])
            reader = pyutmp.UtmpFile(str(path))

            self.assertEqual([entry.ut_pid for entry in reader], [1234])
            reader.rewind()
            self.assertEqual([entry.ut_pid for entry in reader], [1234])


if __name__ == "__main__":
    unittest.main()