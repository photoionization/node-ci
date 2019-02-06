# Copyright 2019 the V8 project authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

vars = {
  'build_url': 'https://chromium.googlesource.com/chromium/src/build.git',
  'build_revision': '85b07e998a9cf85b07c1afc1046270aab63d5020',

  'buildtools_url': 'https://chromium.googlesource.com/chromium/buildtools.git',
  'buildtools_revision': '2f02e1f363b1af2715536f38e239853f04ec1497',

  'clang_url': 'https://chromium.googlesource.com/chromium/src/tools/clang.git',
  'clang_revision': '3a16568a56486d7d032b8ec7b8dae892413a9a7a',

  'googletest_url': 'https://chromium.googlesource.com/external/github.com/google/googletest.git',
  'googletest_revision': '5ec7f0c4a113e2f18ac2c6cc7df51ad6afc24081',

  'icu_url': 'https://chromium.googlesource.com/chromium/deps/icu.git',
  'icu_revision': '07e7295d964399ee7bee16a3ac7ca5a053b2cf0a',

  'jinja2_url': 'https://chromium.googlesource.com/chromium/src/third_party/jinja2.git',
  'jinja2_revision': 'b41863e42637544c2941b574c7877d3e1f663e25',

  'markupsafe_url': 'https://chromium.googlesource.com/chromium/src/third_party/markupsafe.git',
  'markupsafe_revision': '8f45f5cfa0009d2a70589bcda0349b8cb2b72783',

  'node_url': 'https://chromium.googlesource.com/external/github.com/v8/node.git',
  'node_revision': 'af7b741e38da0700283386261d2a5fe1a666c636',

  'trace_common_url': 'https://chromium.googlesource.com/chromium/src/base/trace_event/common.git',
  'trace_common_revision' : 'e31a1706337ccb9a658b37d29a018c81695c6518',

  'v8_url': 'https://chromium.googlesource.com/v8/v8.git',
  'v8_revision': '66ddc07b45f4124bdcde8cb2210cf5291539a21a',
}

deps = {
  'node-ci/base/trace_event/common': Var('trace_common_url') + '@' + Var('trace_common_revision'),
  'node-ci/build': Var('build_url') + '@' + Var('build_revision'),
  'node-ci/buildtools': Var('buildtools_url') + '@' + Var('buildtools_revision'),
  'node-ci/tools/clang': Var('clang_url') + '@' + Var('clang_revision'),
  'node-ci/third_party/googletest/src': Var('googletest_url') + '@' + Var('googletest_revision'),
  'node-ci/third_party/icu': Var('icu_url') + '@' + Var('icu_revision'),
  'node-ci/third_party/jinja2': Var('jinja2_url') + '@' + Var('jinja2_revision'),
  'node-ci/third_party/markupsafe': Var('markupsafe_url') + '@' + Var('markupsafe_revision'),
  'node-ci/v8': Var('v8_url') + '@' +  Var('v8_revision'),
  'node-ci/node': Var('node_url') + '@' + Var('node_revision'),
}

recursedeps = [
  'node-ci/buildtools',
]

hooks = [
  {
    'name': 'clang',
    'pattern': '.',
    'action': ['python', 'node-ci/tools/clang/scripts/update.py'],
  },
  {
    'name': 'generate_node_filelist',
    'pattern': 'node-ci/node',
    'action': ['python', 'node-ci/tools/generate_node_files_json.py'],
  },
  # Pull GN using checked-in hashes.
  {
    'name': 'gn_win',
    'pattern': '.',
    'condition': 'host_os == "win"',
    'action': [ 'download_from_google_storage',
                '--no_resume',
                '--platform=win32',
                '--no_auth',
                '--bucket', 'chromium-gn',
                '-s', 'node-ci/buildtools/win/gn.exe.sha1',
    ],
  },
  {
    'name': 'gn_mac',
    'pattern': '.',
    'condition': 'host_os == "mac"',
    'action': [ 'download_from_google_storage',
                '--no_resume',
                '--platform=darwin',
                '--no_auth',
                '--bucket', 'chromium-gn',
                '-s', 'node-ci/buildtools/mac/gn.sha1',
    ],
  },
  {
    'name': 'gn_linux',
    'pattern': '.',
    'condition': 'host_os == "linux"',
    'action': [ 'download_from_google_storage',
                '--no_resume',
                '--platform=linux*',
                '--no_auth',
                '--bucket', 'chromium-gn',
                '-s', 'node-ci/buildtools/linux64/gn.sha1',
    ],
  },
]
