"""python-stormondemand 0.2 - a simple client library for accessing the Liquid Web Storm API, written in python

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

import requests
import time
import json
from getpass import getpass

class HTTPException(Exception):
	"""
raised when an HTTP error is encountered; e.g. 401 Permission Denied. If StormOnDemand itself has an issue preventing the request, a StormException may be raised.
	"""
	def __init__(self, code, text):
		self.code = code
		self.text = text
		message = ('Received bad response from the server: %d\n%s' % (code, text))
		super(HTTPException, self).__init__(message)

class StormException(Exception):
	"""
error_class - the type of error encountered, follows the form `LW::Exception::Something::Bad`; you can read more about possible error types here: https://www.stormondemand.com/api/docs/tutorials/exceptions.html
error_message - details of the error recieved

full_message - the full text of the error provided by the server. Will be used as the message of the python base Exception type. 

this exception will be raised when there is an error_class key in the server response. If you would like to handle such errors yourself, this exception may be disabled by setting `raise_exceptions=False` when creating an LWApi object. Regardless, the HTTPException will still be raised if the server responds in a way that can't be handled. e.g. 401 Permission Denied.
	"""
	def __init__(self, error_class, full_message):
		self.error_class = error_class
		self.full_message = full_message
		super(StormException, self).__init__(full_message)

class LWApi(object):
	_version = '0.2'
	_user_agent = 'stormpy-lwapi/0.2'


	def __init__(self, user, password=None, url='api.stormondemand.com', api_version='v1', verify=True, raw_json=False, raise_exceptions=True, use_tokens=True):
		"""
user - the api user (a string)

password - the user's password (a string). If the password is omitted, it will need to be entered via stdin anytime the auth token needs to be updated. This is only recommended for CLI applications. If CLI interactivity is not required, the password should be supplied.

url - the url of the storm on demand api. This is for testing and development purposes, and won't need to be changed for normal usage. 

api_version - the version of the api that will be used (a string). defaults to 'v1'. 'bleed' may also be used at the moment to access the API's neweset methods. 

verify - whether the SSL certificate for the api should be verified (a bool). Defaults to True. This is primarily for testing. The public api should *always* have a valid SSL certificate!

raw_json - by default, LWApi.req() will return a python object generated from the json string sent by the server. By setting this value to True, req() will return the raw json string. This may also be overridden while calling the method if desired.

raise_exceptions - by default, LWApi will raise a StormException if there is an error_class key in the server's response. If you would like to handle these errors yourself. this can be set to False. you can read more about Error Responses here: https://www.stormondemand.com/api/docs/tutorials/exceptions.html ; please note that bad http responses (e.g. 401) will still cause a HTTPException to be raised. Additionally, if automatic token handling is being used, a StormException will be raised if there is an issue with the call to /Account/Auth/token

use_tokens - by default, LWApi is used persistently and will automatically use auth tokens via the /Account/Auth/token method. If this behavior is not desired, this can be set to false.
		"""
		self._url = 'https://%s/%s/' % (url, api_version) 
		self._user = user
		self._password = password

		self._verify = verify
		self._raw_json = raw_json
		self._raise_exceptions = raise_exceptions
		self._use_tokens = use_tokens

		# auth token & expiry time. These will be set via calls to _get_token().
		self._token = None
		self._expires = 0

	def _get_password(self):
		"""
			prompts user for password if it's not stored in memory
		"""
		if self._password:
			return self._password
		else:
			return getpass()

	def _get_token(self):
		"""
			return a stored token, or obtain one via the /Account/Auth/token api method and return that
		"""

		# if we have a valid token, and it's not about to expire, return that
		if self._token and time.time() + 60 < self._expires:
			return self._token

		# otherwise, go on and get a new token.
		# assemble and send the post request to obtain the key
		auth = requests.auth.HTTPBasicAuth(self._user, self._get_password())
		url = self._url + 'Account/Auth/token'
		data = '{"params":{"timeout":"3600"}}'
		req = requests.post(url=url, auth=auth, data=data, verify=self._verify,\
			headers={'User-Agent': self._user_agent})

		# raise an error if we don't get a 200 response
		if req.status_code != 200:
			raise HTTPException(req.status_code, req.text)

		response = json.loads(req.text)

		# ensure request was successful:
		if 'error_class' in response:
			raise StormException(response['error_class'], response['full_message'])

		# store the new token/expiry time and return the token
		self._token = response['token']
		self._expires = int(response['expires'])
		return self._token

	def _get_auth(self):
		"""
			returns a requests.auth.HTTPBasicAuth object
		"""
		if self._use_tokens:
			return requests.auth.HTTPBasicAuth(self._user, self._get_token())
		else:
			return requests.auth.HTTPBasicAuth(self._user, self._get_password())
			
			

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
		# if the path starts with a /, strip it off. if they didn't give a path, the api will error out, but that's cleaner than dealing with the error here.
		if path and path[0] == '/':
			path = path[1:]

		# the docs say to put your data in a hash, the top level of which should be a
		#  key called 'params'... this is sort of redundant, so for simplicity's sake
		# we will support dicts that are formatted per the docs, and format them thus
		# if it's just the bare params. when we finally make the call, we will format
		# the given params into a json string.
		if 'params' not in data.keys():
			data = { 'params': data }

		url = self._url + path
		req = requests.post(url=url, auth=self._get_auth(),\
			data=json.dumps(data), verify=self._verify,\
			headers={'User-Agent': self._user_agent})

		# make sure the request was completed successfully
		if req.status_code != 200:
			raise HTTPException(req.status_code, req.text)

		# turn the response into a json object
		response = json.loads(req.text)

		# handling errors: per the API docs, check the response for an 'error_class'
		#  key (if the user has requested that we raise errors for them, that is):
		if self._raise_exceptions and 'error_class' in response:
			raise StormException(response['error_class'], response['full_message']) 
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
