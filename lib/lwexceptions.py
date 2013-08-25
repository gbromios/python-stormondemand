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
