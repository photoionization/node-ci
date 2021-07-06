# Copyright (c) 2013-2019 GitHub Inc.
# Copyright 2019 the V8 project authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json
import os
import subprocess
import sys

basedir = os.path.dirname(__file__)
sys.path.append(os.path.join(basedir, os.pardir, 'node', 'tools'))
import install

def LoadPythonDictionary(path):
  file_string = open(path).read()
  try:
    file_data = eval(file_string, {'__builtins__': None}, None)
  except SyntaxError, e:
    e.filename = path
    raise
  except Exception, e:
    raise Exception('Unexpected error while reading %s: %s' % (path, str(e)))

  assert isinstance(file_data, dict), '%s does not eval to a dictionary' % path

  return file_data


FILENAMES_JSON_HEADER = '''
// This file is automatically generated by generate_gn_filenames_json.py
// DO NOT EDIT
'''.lstrip()

def dedup(a_list):
  return list(set(a_list))

def RedirectV8(list):
  return [f.replace('deps/v8/', '../v8/', 1) for f in list]

def GitLsFiles(path, prefix):
  output = subprocess.check_output(['git', 'ls-files'], cwd=path)
  return [prefix + x for x in output.splitlines()]

def isGypExpansion(entry):
  return entry.startswith('<') or entry.startswith('>')

def GypExpand(node_dir, entry):
  assert entry.startswith('<!'), \
    'Only gyp command expansion is supported at the moment. ' \
    'Invalid expansion: %s' % entry
  is_list = entry.startswith('<!@')
  command = entry[4 if is_list else 3 : -1]
  command = command.split()
  # Dirty hack to run node's python3 scripts under our python2 environment
  if command[0] == 'python':
    command[0] = 'python3'
  output = subprocess.check_output(command, cwd=node_dir)
  if is_list:
    output = output.splitlines()
  else:
    output = [output]
  return output

def GypExpandList(node_dir, list):
  entries = []
  for entry in list:
    if isGypExpansion(entry):
      entries = entries + GypExpand(node_dir, entry)
    else:
      entries.append(entry)
  return entries

if __name__ == '__main__':
  # Set up paths.
  root_dir = os.path.dirname(os.path.dirname(__file__))
  node_dir = os.path.join(root_dir, 'node')
  node_gyp_file = os.path.join(node_dir, 'node.gyp')
  out_file = os.path.join(root_dir, 'node_files.json')
  inspector_gyp_file = os.path.join(node_dir,
      'src', 'inspector', 'node_inspector.gypi')
  openssl_gyp_file = os.path.join(node_dir,
      'deps', 'openssl', 'config', 'archs',
      'linux-x86_64', 'no-asm', 'openssl.gypi')
  out = {}
  # Load file lists from gyp files.
  node_gyp = LoadPythonDictionary(node_gyp_file)
  inspector_gyp = LoadPythonDictionary(inspector_gyp_file)
  openssl_gyp = LoadPythonDictionary(openssl_gyp_file)
  # Find JS lib file and single out files from V8.
  library_files = GypExpandList(node_dir, node_gyp['variables']['library_files'])
  deps_files = node_gyp['variables']['deps_files']
  library_files += deps_files
  out['node_library_files'] = [
      f for f in library_files if not f.startswith('deps/v8')]
  out['all_library_files'] = library_files

  # Find C++ source files.
  node_lib_target = next(
      t for t in node_gyp['targets']
      if t['target_name'] == '<(node_lib_target_name)')
  node_source_blacklist = {
      '<@(library_files)',
      '<@(deps_files)',
      'common.gypi',
      '<(SHARED_INTERMEDIATE_DIR)/node_javascript.cc',
  }
  node_sources = [
      f for f in node_lib_target['sources']
      if f not in node_source_blacklist]
  out['node_sources'] = [
      f.replace('deps/v8/', '../v8/', 1) for f in node_sources]

  # Find C++ sources when building with crypto.
  node_use_openssl = next(
      t for t in node_lib_target['conditions']
      if t[0] == 'node_use_openssl=="true"')
  out['crypto_sources'] = dedup(node_use_openssl[1]['sources'])

  # Find cctest files. Omit included gtest.
  cctest_target = next(
      t for t in node_gyp['targets']
      if t['target_name'] == 'cctest')
  out['cctest_sources'] = [
      f for f in cctest_target['sources'] if not f.startswith('test/cctest/gtest')]

  # Find inspector sources.
  inspector_sources = inspector_gyp['sources']
  out['inspector_sources'] = inspector_sources

  # Find OpenSSL sources.
  openssl_sources = openssl_gyp['variables']['openssl_sources']
  out['openssl_sources'] = openssl_sources
  # Find node/tools/doc content.
  tools_doc_dir = os.path.join(node_dir, 'tools', 'doc')
  out['tools_doc_files'] = GitLsFiles(tools_doc_dir, '//node/tools/doc/')

  # Find node/test/addons content.
  test_addons_dir = os.path.join(node_dir, 'test', 'addons')
  out['test_addons_files'] = GitLsFiles(test_addons_dir, '//node/test/addons/')

  # Find node/test/node-api content.
  test_node_api_dir = os.path.join(node_dir, 'test', 'node-api')
  out['test_node_api_files'] = GitLsFiles(test_node_api_dir,
                                          '//node/test/node-api/')
  # Find node/test/js-native-api content.
  test_js_native_api_dir = os.path.join(node_dir, 'test', 'js-native-api')
  out['test_js_native_api_files'] = GitLsFiles(test_js_native_api_dir,
                                               '//node/test/js-native-api/')

  # Find v8/include content.
  v8_include_dir = os.path.join(root_dir, 'v8', 'include')
  out['v8_headers'] = GitLsFiles(v8_include_dir, '//v8/include/')

  # Write file list as JSON.
  with open(out_file, 'w') as f:
    f.write(FILENAMES_JSON_HEADER)
    f.write(json.dumps(out, sort_keys=True, indent=2, separators=(',', ': ')))
    f.write('\n')
