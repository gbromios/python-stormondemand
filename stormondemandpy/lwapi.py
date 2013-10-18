"""python-stormondemand - a simple client library for accessing the Liquid Web Storm API, written in python

  see the official documentation for more information about the api itself:
    http://www.liquidweb.com/StormServers/api/docs/v1

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

import os
import requests
import urllib
import time
import json
from getpass import getpass
from lwexceptions import *



class LWApi(object):
  def __init__(self, user, password=None, url='api.stormondemand.com', api_version='v1', verify=True, docfile=None, authfile=None, raw_json=False):
    """
user - the api user (a string)

password - the user's password (a string). If the password is omitted, it will need to be entered via stdin anytime the auth token needs to be updated. This is only recommended for CLI applications. If CLI interactivity is not required, the password should be supplied.

url - the url of the storm on demand api. This is for testing and development purposes, and won't need to be changed for normal usage. 

api_version - the version of the api that will be used (a string). defaults to 'v1'. 'bleed' may also be used at the moment to access the API's neweset methods. 

verify - whether the SSL certificate for the api should be verified (a bool). Defaults to True. This is primarily for testing. The public api should *always* have a valid SSL certificate!

docfile - name of the file that contains the api documentation in json format. This file may be downloaded here:
- http://www.liquidweb.com/StormServers/api/docs/v1/docs.json
If no filename is given, the docs will be saved in the stormy directory

authfile - by default, auth tokens are not stored persistently, and will only exist until the LWApi object is garbage collected. if a filename is supplied, LWApi will attempt to store the auth token (along with its expiry time) there so that it may be used by multiple LWApi objects. This behavior may be desriable for certain CLI applications where a new LWApi object is created for each request.

raw_json - by default, LWApi.req() will return a python object generated from the json string sent by the server. By setting this value to True, req() will return the raw json string. This may also be overridden while calling the method if desired.
    """
    self._url = 'https://%s/%s/' % (url, api_version) 
    self._user = user
    self._password = password

    self._verify = verify
    self._raw_json = raw_json

    self._authfile = authfile

    # auth token & expiry time. These will be set via calls to _get_token().
    self._token = ''
    self._expires = 0

    # generate the dict of methods, based on json documentation.
    # if we're given a local file for the docs

    # if no docfile is given, use docs.json in the library's directory
    if docfile is None:
      docfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'docs.json')
    try: 
      docs = open(docfile,'r')
    except IOError:
      #if we're given a file that does not exist, create it and write the docs to it.
      new_docs_file = open(docfile,'w')
      downloaded_docs = urllib.urlopen(('http://www.liquidweb.com/StormServers/api/docs/%s/docs.json' % api_version))
  
      new_docs_file.write( downloaded_docs.read() )

      downloaded_docs.close()
      new_docs_file.close()

      # then open the new file
      docs = open(docfile,'r')

    # we process the raw docs to make them a little easier to work with,
    # so that each method is at the top level in the generated dict 
    self._docs = {} 
    j_docs = json.load(docs)

    for path in j_docs.keys():
      methods = j_docs[path]
      for m in methods['__methods']:
        method = path + '/' + m
        self._docs[method] = methods['__methods'][m]

    docs.close()

  def _get_token(self):
    """
      obtain an auth token, either via the /Account/Auth/token api method, or by reading a locally stored token.
    """
    # if no password is given
    if self._password == None:
    
      # check to see if we're using an auth file.
      if self._authfile:
        # if we are, try to use it.
        try:
          # read the values in
          af = open(self._authfile, 'r')
          self._token = af.readline()
          self._expires = int(af.readline())
          af.close()

          # make sure the token we read is still good
          now = int(time.time())
          if self._expires == 0 or now > self._expires + 5:
            # it's sort of shady to raise IOError when there's no IOError
            # but it's an easy way to get us somewhere that will skip over
            # the early return AND get us the password 
            raise IOError

          # if the file was readable and had a valid token
          # then exit from the function early
          return
          
        
        # if it's not there, grab the password as normal, we'll write the authfile later
        except IOError:
          print "need to retrieve auth token. please enter password for user `%s`" % self._user
          passwd = getpass('pass > ')

      # if no auth file was given, grab the password as normal.
      else:
        print "need to retrieve auth token. please enter password for user `%s`" % self._user
        passwd = getpass('pass > ')
    else:
      passwd = self._password

    # assemble and send the post request to obtain the key
    auth = requests.auth.HTTPBasicAuth(self._user, passwd)
    url = self._url + 'Account/Auth/token'
    data = '{"params":{"timeout":"3600"}}'
    r = requests.post(url=url, auth=auth, data=data, verify=self._verify)

    # raise an error if we don't get a 200 response
    if r.status_code != 200:
      raise BadResponseException(r.status_code, r.text)

    else:
      self._token = json.loads(r.text)['token']
      self._expires = int(json.loads(r.text)['expires'])

      # if the user would like to save the token, write it into the file with
      # the expiry time.
      if self._authfile:
        af = open(authfile, 'w')
        af.write('%s\n%d' % (self._token, self._expires))
        af.close

  def _get_auth(self):
    """
      returns a requests.auth.HTTPBasicAuth object
    """
    now = int(time.time())
    # if the auth token is not set, or if it has expired/is about to expire
    if self._expires == 0 or now > self._expires + 5:
      self._get_token()

    return requests.auth.HTTPBasicAuth(self._user, self._token)
      

  def req(self, path, data={}, raw_json=None):
    """make a POST request to the storm api
      path -- a string contaning the method you'd like to call. Methods are Case sensitive. Leading slash may be included or omitted
        ex. 'Utilities/Info/ping'
      
      data -- POST data to be used by the request, formatted as a dict. parameters be added directly:
        data = {'page_size':'20'}
      or as the value to a 'params' key:
        data = {"params":{"page_size":"20"}}

      The latter is how the API expects the data to be formatted, but if a dict of parameters is passed directly, LWApi will add the params key automatically. This should be a little easier to work with.

      raw_json -- may be used to override the default return value. True to return a json string, False to return an object, None to use the instance default. 

      RETURNS: either a json formatted string, or the python object composed from said string, dependign on user's preference. 
    """
    # if the path starts with a /, strip it off.
    if path[0] == '/':
      path = path[1:]

    # if the postdata is enclosed in a 'params' hash, just use the value.
    # support the {"params":{"key":"value"}} because it complies with the
    # docs, but the data is easier to use without it, so we'll put it in
    # when we make the request.
    if data.keys() == ['params']:
      data = data['params']


    # this is where input validation should take place
    # presently, we just make sure that the required parameters are given
    # but eventually we will add type checking

    if path not in self._docs:
      # invalid method!
      raise NoMethodException(path) 

    method = self._docs[path]

    # check given parameters 
    for param in data:
      # make sure there aren't any we're not expecting 
      if param not in method['__input']:
        raise InvalidParamException(param, path)

      # make sure the type is correct... but do that later
      # ( type validation goes here )

    # check expected parameters to make sure required/non-optional params are
    # present... I guess there's a difference according to the docs? hoefully
    # this will be addressed at some point, some input parameters are marked
    # as optional: 1|0, others are marked as required as required: 1|0, but
    # there seems to be no rhyme or reason to this.
    for param in method['__input']:
      param_dict = method['__input'][param]
      if param not in data:
        # if a parameter wasn't supplied and there's a default, use the default
        if 'default' in param_dict:
          default = param_dict['default']
          data[param] = default
          
        # if the parameter is required/non-optional/whatever, and it's not
        # present, throw an error
        elif ('optional' in param_dict and param_dict['optional'] == '0')\
        or ('required' in param_dict and param_dict['required'] == '1')\
        or ('optional' not in param_dict and 'required' not in param_dict):
          raise RequiredParamMissingException(param, path)

    url = self._url + path
    req = requests.post(url=url, auth=self._get_auth(),\
                        data=json.dumps({'params':data}), verify=self._verify)

    # make sure the request was completed successfully
    if req.status_code != 200:
      raise BadResponseException(req.status_code, req.text)

    # turn the response into a json object
    response = json.loads(req.text)

    # handling errors: per the API docs, check the response for an 'error_class' key:
    if 'error_class' in response:
      raise StormException(response['error_class'],response['full_message']) 

    # no error:
    # if the user has not overriden the return setting for this call, return the default type
    if raw_json is None:
      if self._raw_json:
        return req.text
      else:
        return response

    elif raw_json:
      return req.text
    else:
      return response
