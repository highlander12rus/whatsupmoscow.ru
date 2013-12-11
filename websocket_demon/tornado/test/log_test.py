#!/usr/bin/env python
#
# Copyright 2012 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from __future__ import absolute_import, division, print_function, with_statement

import contextlib
import glob
import logging
import os
import re
import tempfile
import warnings

from tornado.escape import utf8
from tornado.log import LogFormatter, define_logging_options, enable_pretty_logging
from tornado.options import OptionParser
from tornado.test.util import unittest
from tornado.util import u, bytes_type, basestring_type


@contextlib.contextmanager
def ignore_bytes_warning():
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=BytesWarning)
        yield


class LogFormatterTest(unittest.TestCase):
    # Matches the output of a single logging call (which may be multiple lines
    # if a traceback was included, so we use the DOTALL option)
    LINE_RE = re.compile(b"(?s)\x01\\[E [0-9]{6} [0-9]{2}:[0-9]{2}:[0-9]{2} log_test:[0-9]+\\]\x02 (.*)")

    def setUp(self):
        self.formatter = LogFormatter(color=False)
        # Fake color support.  We can't guarantee anything about the $TERM
        # variable when the tests are run, so just patch in some values
        # for testing.  (testing with color off fails to expose some potential
        # encoding issues from the control characters)
        self.formatter._colors = {
            logging.ERROR: u("\u0001"),
        }
        self.formatter._normal = u("\u0002")
        self.formatter._color = True
        # construct a Logger directly to bypass getLogger's caching
        self.logger = logging.Logger('LogFormatterTest')
        self.logger.propagate = False
        self.tempdir = tempfile.mkdtemp()
        self.filename = os.path.join(self.tempdir, 'log.out')
        self.handler = self.make_handler(self.filename)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.handler.close()
        os.unlink(self.filename)
        os.rmdir(self.tempdir)

    def make_handler(self, filename):
        # Base case: default setup without explicit encoding.
        # In python 2, supports arbitrary byte strings and unicode objects
        # that contain only ascii.  In python 3, supports ascii-only unicode
        # strings (but byte strings will be repr'd automatically).
        return logging.FileHandler(filename)

    def get_output(self):
        with open(self.filename, "rb") as f:
            line = f.read().strip()
            m = LogFormatterTest.LINE_RE.match(line)
            if m:
                return m.group(1)
            else:
                raise Exception("output didn't match regex: %r" % line)

    def test_basic_logging(self):
        self.logger.error("foo")
        self.assertEqual(self.get_output(), b"foo")

    def test_bytes_logging(self):
        with ignore_bytes_warning():
            # This will be "\xe9" on python 2 or "b'\xe9'" on python 3
            self.logger.error(b"\xe9")
            self.assertEqual(self.get_output(), utf8(repr(b"\xe9")))

    def test_utf8_logging(self):
        self.logger.error(u("\u00e9").encode("utf8"))
        if issubclass(bytes_type, basestring_type):
            # on python 2, utf8 byte strings (and by extension ascii byte
            # strings) are passed through as-is.
            self.assertEqual(self.get_output(), utf8(u("\u00e9")))
        else:
            # on python 3, byte strings always get repr'd even if
            # they're ascii-only, so this degenerates into another
            # copy of test_bytes_logging.
            self.assertEqual(self.get_output(), utf8(repr(utf8(u("\u00e9")))))

    def test_bytes_exception_logging(self):
        try:
            raise Exception(b'\xe9')
        except Exception:
            self.logger.exception('caught exception')
        # This will be "Exception: \xe9" on python 2 or
        # "Exception: b'\xe9'" on python 3.
        output = self.get_output()
        self.assertRegexpMatches(output, br'Exception.*\\xe9')
        # The traceback contains newlines, which should not have been escaped.
        self.assertNotIn(br'\n', output)


class UnicodeLogFormatterTest(LogFormatterTest):
    def make_handler(self, filename):
        # Adding an explicit encoding configuration allows non-ascii unicode
        # strings in both python 2 and 3, without changing the behavior
        # for byte strings.
        return logging.FileHandler(filename, encoding="utf8")

    def test_unicode_logging(self):
        self.logger.error(u("\u00e9"))
        self.assertEqual(self.get_output(), utf8(u("\u00e9")))


class EnablePrettyLoggingTest(unittest.TestCase):
    def setUp(self):
        super(EnablePrettyLoggingTest, self).setUp()
        self.options = OptionParser()
        define_logging_options(self.options)
        self.logger = logging.Logger('tornado.test.log_test.EnablePrettyLoggingTest')
        self.logger.propagate = False

    def test_log_file(self):
        tmpdir = tempfile.mkdtemp()
        try:
            self.options.log_file_prefix = tmpdir + '/test_log'
            enable_pretty_logging(options=self.options, logger=self.logger)
            self.assertEqual(1, len(self.logger.handlers))
            self.logger.error('hello')
            self.logger.handlers[0].flush()
            filenames = glob.glob(tmpdir + '/test_log*')
            self.assertEqual(1, len(filenames))
            with open(filenames[0]) as f:
                self.assertRegexpMatches(f.read(), r'^\[E [^]]*\] hello$')
        finally:
            for handler in self.logger.handlers:
                handler.flush()
                handler.close()
            for filename in glob.glob(tmpdir + '/test_log*'):
                os.unlink(filename)
            os.rmdir(tmpdir)
