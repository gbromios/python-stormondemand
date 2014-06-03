# python-stormondemand #

##### version 0.2 #####

a lightweight [StormOnDemand API](https://www.stormondemand.com/api/) python wrapper based on the [requests library](http://docs.python-requests.org/en/latest/), released as open source under the Apache 2.0 License.

presently, the entire functionality of the library is available in the lwapi.py module.

### Basic Example ###


```python
$ python -i

>>> # create an LWApi object:

>>> from stormpy import lwapi
>>> storm = lwapi.LWApi("username", "password")


>>> # use the LWApi.req() method to call methods on the Storm API. If the
>>> # request completes successfully, a json-format native python object
>>> # will be returned, as parsed by the standard python JSON library:
>>> type(storm.req('/Storm/Server/list'))
<type 'dict'>
>>> storm.req('/Storm/Server/list')['items'][0]['create_date']
u'2013-01-08 14:34:50'


>>> # if desired, the return type may be overridden so that the LWApi.req()
>>> # method returns a raw string containing Storm's response, by specifying
>>> # raw_json=True, either when calling req(), or when creating an LWAapi
>>> # instance, if you prefer to skip the JSON-to-python parsing:

>>> type(storm.req('/Storm/Server/list', raw_json=True))
<type 'unicode'>
>>> storm.req('/Storm/Server/list', raw_json=True)[443:473].upper()
u'CENTOS 6.5 64-BIT SELF-MANAGED'


>>> # parameters are passed to the API as a dict; per the documentation, this
>>> # this dict must be passed within an outer dict, as the value of a key
>>> # called "params". For the sake of convenience you may pass your params
>>> # as a dict, and LWApi will automatically format them correctly to conform
>>> # to the {'params':{ ... }} convention used by Storm:

>>> storm.req('/Storm/Server/reboot', data={ 'params' : { 'uniq_id': 'TP8J8V' } })
{
	"rebooted": "TP8J8V"
}

>>> storm.req('/Storm/Server/reboot', data={ 'uniq_id': '2DKA1R' })
{   
    "rebooted": "2DKA1R"
}


>>> # if the storm interface returns an error, LWApi will raise an exception
>>> try:
...     storm.req('/Some/Invented/method')
... except lwapi.StormException as e:
...     print e.error_class
...     print e.full_message
...
LW::Exception::API::InvalidMethod
Invalid API method: some/invented/method


>>> # however, this behavior can be disabled if desired, allowing you to check
>>> # and handle exceptions manually:

>>> storm_2 = lwapi.LWApi("username", "password", raise_exceptions=False)
>>> storm_2.req('/Storm/Server/details', data={'uniq_id': '000000'})
{
    "field": "subaccnt", 
    "full_message": "Record 'subaccnt: 000000' not found: ", 
    "error_class": "LW::Exception::RecordNotFound", 
    "input": "000000", 
    "error": ""
}

>>> # Basic HTTP Authentication is handled by passing the username and password
>>> # during LWApi instantiation. The password may be given as None, in which
>>> # case, the user will be prompted for a password upon making a request.
>>> # naturally, doing so should be limited strictly to CLI applications:

>>> storm_cli = lwapi.LWApi("username", None)
>>> storm_cli.req('/Utilities/Info/ping')
Password: 
{u'ping': u'success'}

>>> # LWApi automatically uses the '/Account/Auth/token' method of Storm to
>>> # grab an auth token, and will take care of renewing expired tokens, 
>>> # allowing a user to enter their password once and use a token for the 
>>> # next hour:

>>> storm_cli.req('/Utilities/Info/ping')
{u'ping': u'success'}


>>> # Token functionality may be disabled, in which case, the password will
>>> # be sent on every request. Note that this will prompt the user for their
>>> # password on every single request:

>>> storm_no_pass = lwapi.LWApi("username", None, use_tokens=False)
>>> storm_no_pass.req('/Utilities/Info/ping')
Password:
{u'ping': u'success'}
>>> storm_no_pass.req('/Utilities/Info/ping')
Password:
{u'ping': u'success'}

```

That's a basic overview of the functionality currently present in stormpy.lwapi, and should allow you to perform any action in the [StormOnDemand API](https://www.stormondemand.com/api/) by reading the documentation.


### Future ###

When I have a chance, here are some features I'd like to add:

- native python function calls would be a nice addition, though this is low priority given the current ease of use.

- just for sanity, unit tests are in the works

- package the module as a .egg and possibly even upload it to pypi; if the project grows at all, this will be nice to have!








