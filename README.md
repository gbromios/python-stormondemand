stormpy
=======

stormpy - a simple client library for accessing the Liquid Web Storm API, written in python

once I've written it, this file will explain how to use the library. Until then, take a look at the docstrings in lwapi.py

TODO:
 - expand exception checking/add more exceptions.
 - stronger type validation? not sure of a good way to do that without downloading more docs, if said docs even exist somewhere they're publicly available
 - handle 'required_if' parameters, either dynamically or checking case-by-case
 - should users be able to save auth tokens for multiple users in the same authfile?
 - file interactions (saving docs / auth tokens) could stand to be more robust. Right now it just opens files based on a string, doesn't use os.path or anything. Related: probably want the docs to get downloaded somewhere out-of-the way, probably with the other lib files. At the moment, they go into $PWD or an absolute path. Not very convenient. 
 - add tests ヽ(*・ω・)ﾉ
 - turn the files into some sort of distributable package... like a .egg or something. Still need to figure out how those things work eggsactly 
 - write better docs with usage examples
