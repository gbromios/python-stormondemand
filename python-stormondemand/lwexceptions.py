"""lwexceptions.py - exceptions that may be thrown by the api client

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

class NoMethodException(Exception):
  def __init__(self, method):
    message = ('Method `%s` was not found' % (method))
    super(NoMethodException, self).__init__(message)

class RequiredParamMissingException(Exception):
  def __init__(self, param, method):
    message = ('Required Parameter `%s` was not given for method `%s`' % (param, method))
    super(RequiredParamMissingException, self).__init__(message)

class BadResponseException(Exception):
  def __init__(self, code, text):
    message = ('Received bad response from the server: %d\n%s' % (code, text))
    super(BadResponseException, self).__init__(message)
