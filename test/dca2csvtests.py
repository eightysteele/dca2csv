#!/usr/bin/env python

# Copyright 2011 Jante LLC and University of Kansas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "Aaron Steele, Dave Vieglais, and John Wieczorek"

"""This module provides unit testing for the dca2csv.py module."""

from dca2csv import *
import logging
import unittest

class FieldTypeTests(unittest.TestCase):
    """Provides unit testing for FieldType class."""

    def test_constructor(self):
        """Tests the FieldType constructor with various inputs."""
        try:
            FieldType()
            self.fail()
        except:
            pass

        try:
            FieldType(None)
            self.fail()
        except:
            pass
        
        x = FieldType('foo')
        self.assertTrue(x.term == 'foo')

        x = FieldType('http://bar.com/foo')
        self.assertTrue(x.term == 'foo')

        x = FieldType('foo', index=0)
        self.assertTrue(x.index == 0)
        
        try:
            FieldType('foo', index='')
        except TypeError:
            pass

        x = FieldType('foo', default='bar')
        self.assertTrue(x.default == 'bar')

        x = FieldType('foo', index=0, default='bar')
        self.assertTrue(x.term == 'foo')
        self.assertTrue(x.index == 0)
        self.assertTrue(x.default == 'bar')

class CoreFileTypeTests(unittest.TestCase):
    """Provides unit testing for CoreFileType class."""
    # TODO
    pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
