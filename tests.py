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
