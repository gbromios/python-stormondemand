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
from stormpy.lwapi import LWApi

class StormpyTests(unittest.TestCase):
  username = os.getenv('UNAME')
  password = os.getenv('PASSWD')

  def test_placeholder(self):
    # tests aren't much at the moment, but I'll add more later
    a = LWApi(self.username, self.password)
    a.req('Utilities/Info/ping')

    

if __name__ == '__main__':
  unittest.main()
