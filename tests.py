"""tests.py - tests for the python storm on demand client library

   Copyright 2013 Liquid Web, Inc. 

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import unittest
import os
from sys import argv
from stormondemandpy.lwapi import LWApi

if len(argv) != 3:
  raise Exception("usage: tests.py USERNAME PASSWORD\ntests require valid api credentials")

class StormTests():
  username = argv[1]
  password = argv[2]

  def test_placeholder(self):
    # tests aren't much at the moment, but I'll add more later
    a = LWApi(self.username, self.password)
    r = a.req('Utilities/Info/ping')
    print r, ' this is what the storm api has to say about your creds.\n Coming soon: real tests :P'

s = StormTests()
s.test_placeholder()
