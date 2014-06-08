# download API documentation from Storm api website and use them to generate
# a native python Storm On Demand client!

import requests, json, os
from lwapi import LWApi

# figure out a more elegant way to do this later; certain parameter names in 
# storm clash with python reserved keywords; append the paramater with an
# underscore in these cases. there are also a few parameter names that, just
# to be safe, will be similarly escaped.
global reserved
reserved = ['and', 'as', 'assert', 'break', 'class', 'continue', 'data', 'def', 'del', 'elif', 'else', 'except', 'exec', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'path', 'print', 'raise', 'return', 'try', 'while', 'with', 'yield']

## utility function so I can readily dump readable json during development
## (to be removed for release)
def pp(j):
	print json.dumps(j, indent=2, sort_keys=True)



# the next two methods turn each method category key into a list, so that all 
# posible method paths are a part of one unified data structure.
def _list_of_method_paths(m_in):
	l = []
	for k in m_in:
		l.append(k.split('/'))
	return l


def _build_method_tree(m_list):
	m_tree = {}
	for method_paths in m_list:
		if not method_paths:
			m_tree['__methods'] = None
		else:
			if method_paths[0] not in m_tree:
				m_tree[method_paths[0]] = []
			m_tree[method_paths[0]].append(method_paths[1:])

	for k, v in m_tree.items():
		if k is not '__methods':
			m_tree[k] = _build_method_tree(v)
	return m_tree


# go through the method tree and fill out the actual method calls
def _add_method_calls(jdoc, m_tree, path=''):
	# presnce of methods key indicates that there are actual callable methods
	# in this "dir", rather than just more specific "dirs"
	#print path
	for k,v in m_tree.items():
		if k == '__methods':
			if path not in jdoc.keys():
				'ERROR: THERES NO METHODS HERE IN THE DOCS D:<'
			m_tree['__methods'] = _parse_method_dict(jdoc[path[1:]]['__methods'])
			m_tree['__full_path'] = path[1:]+'/'
		else:
			_add_method_calls(jdoc, m_tree[k], path+'/'+k)

	return m_tree


# takes the method declaration from the docs.json from storm, and uses them to
# build the dict that we'll use to finally generate the native method calls.
def _parse_method_dict(m_doc):
	methods = {}
	for k,v in m_doc.items():
		methods[k] = v['__input'].keys()
	return methods


# using the method tree we've parsed out of the storm docs, turn that into
# a python module
def _generate_native_storm_client(m_tree, version):
	all = [] # top level classes ("method dirs?") can be imported with *
	all.append('open_api') # utility function to load persistent api object

	indent = 0 # start at 0 indent and work our way to the right
	code = "" # the string that will hold our generated code

	for k,v in m_tree.items():
		all.append(k)
		code += _gen_path_class(k, v, indent)

	all_line = '__all__ = ' + repr(all) + '\n'
	base_class = '''from stormpy.lwapi import LWApi

class NativeStorm(object):
	# can set this to a persistent LWApi via open(), to allow for
	# automatic auth token handling.
	storm = None
	version = '%s'
	@classmethod
	def call(cls, auth_user, auth_password, path, data, **kwargs):
		# unescape args with reserved names
		for k,v in kwargs.items():
			if k[-1] == '_':
				kwargs[k[:-1]] = v
				del kwargs [k]
		if not data:
			data = kwargs

		if cls.storm:
			return cls.storm.req(path, data)
		else:
			return LWApi(auth_user, auth_password, api_version = cls.version).req(path, data)

	@classmethod
	def open(cls, auth_user, auth_pass=None):
		cls.storm = LWApi(auth_user, auth_pass, api_version=cls.version)
''' % version

	# a global function allowing the creation of a single LWApi instance
	open_line = 'def open_api(auth_user, auth_password):\n\tNativeStorm.open(auth_user, auth_password)\n\n'


	return all_line + base_class + open_line + code


def _gen_path_class(storm_path_dir, m_tree, indent):
	code = ('\t'*indent) + 'class %s(NativeStorm):\n' % storm_path_dir
	
	# just to make the end library prettier, do the class methods before
	# the sub-classes. Doesn't really matter, but they should go before
	# or after, and not be mixed in between subclasses.
	if "__methods" in m_tree:
		code += _gen_path_methods(m_tree['__methods'], m_tree['__full_path'], indent + 1)

	for k,v in m_tree.items():
		if k in ('__methods','__full_path'):
			continue
		code += _gen_path_class(k, v, indent + 1)

	# put an extra newline at the end of a class for intense readibility
	code += '\n'
	return code


def _gen_path_methods(methods, path, indent):
	code = ''
	
	for k,v in methods.items():
		def_line = ('\t'*indent) + 'def ' + k + '(cls, auth_user=None, auth_password=None, data=None'

		# all args are optional and default to None at the moment. May make
		# this more detailed in the future.

		for arg in v:
			# can't use python keywords as parameters!
			if arg in reserved:
				arg += '_'
			def_line += ', ' + arg + '=None'
		def_line += '):\n'

		method_path = ('\t'*(indent+1)) + 'path = "%s%s"\n' % (path, k)
		method_call = ('\t'*(indent+1)) + 'return cls.call(auth_user=auth_user, auth_password=auth_password, path=path, data=data'
		for arg in v:
			# can't use python keywords as parameters!
			if arg in reserved:
				arg += '_'
			method_call += ', ' + arg + '=' + arg
		method_call += ')\n'

		code += ('\t'*indent) + '@classmethod\n'
		code += def_line
		code += method_path
		code += method_call
		# put an extra newline at the end of a method for overwhelming readibility
		code += '\n'
	return code
	

def _write_client_files(contents, target_dir, version):
	# finally, write the file.
	try:
		# if target directory doesn't exist, create it (not recursively, though)
		if not os.path.isdir(target_dir):
			os.mkdir(target_dir, 0o755)
		# if/when it does exist, make sure there's a __init__.py inside
		open(os.path.join(target_dir, "__init__.py"), 'w').close()
		# write the code we generated
		with open(os.path.join(target_dir, "%s.py" % version), 'w') as f:
			f.write(contents)

	except OSError as e:
		print " !! Error while creating files:", repr(e)
		raise

def build(version='v1',target_dir=None):
	docs = json.loads(requests.get('https://www.stormondemand.com/api/docs/%s/docs.json' % version).text)
	if not target_dir:
		target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'native')
	_write_client_files(_generate_native_storm_client(_add_method_calls(docs, _build_method_tree(_list_of_method_paths(docs))), version=version), target_dir, version)

if __name__ == '__main__':
	build()






























