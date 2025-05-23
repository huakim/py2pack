#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Sebastian Wagner <sebix@sebix.at>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
import os.path
import sys
from os.path import basename
import pytest

import py2pack

compare_dir = os.path.join(os.path.dirname(__file__), 'examples')
maxDiff = None

import random
import string


def generate_random_string(length):
    letters = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choice(letters) for i in range(length))
    return random_string


username = generate_random_string(22)


@pytest.mark.parametrize('template, fetch_tarball',
                         [('fedora.spec', True),
                          ('mageia.spec', False),
                          ('opensuse-legacy.spec', False),
                          ('opensuse.dsc', False),
                          ('opensuse.spec', False),
                          ('opensuse.spec', True)])
@pytest.mark.parametrize('project, version',
                         [('setuppy', '2021.6.4'),  # legacy setup.py sdist without pyproject.toml
                          ('sampleproject', '3.0.0'),  # PEP517 only sdist without setup.py
                          ('poetry', '1.5.1')])  # poetry build system
def test_template(tmpdir, template, fetch_tarball, project, version):
    """ Test if generated specfile equals to stored one. """

    args = py2pack.Munch({})
    args.template = template
    args.maintainer = username
    base, ext = template.split(".")
    suffix = '-augmented' if fetch_tarball else ''
    filename = f"{base}{suffix}.{ext}"
    args.filename = filename
    args.name = project
    args.version = version
    reference = os.path.join(compare_dir, f'{args.name}-{filename}')
    no_ref = False
    if project == 'poetry' and sys.version_info < (3, 11):
        pytest.xfail("Different requirements for python < 3.11")
    if not os.path.exists(reference):
        no_ref = True
    with tmpdir.as_cwd():
        if fetch_tarball:
            py2pack.fetch(args)
            p1 = project[0]
            source_glob = f'https://files.pythonhosted.org/packages/source/{p1}/{project}/{project}-{version}.tar.gz'
            args.source_url = source_glob
            py2pack.generate(args)
            with open(filename) as filehandle:
                written_spec = filehandle.read()
            args.localfile = basename(source_glob)
            py2pack.generate(args)
            with open(filename) as filehandle:
                assert filehandle.read() == written_spec
        else:
            with pytest.warns(UserWarning, match="No tarball"):
                py2pack.generate(args)
            with open(filename) as filehandle:
                written_spec = filehandle.read()
    if no_ref:
        required = written_spec.replace(username, '__USER__', 1)
        required = required.replace(str(datetime.date.today().year), '__YEAR__', 1)
        with open(reference, 'w') as filehandle:
            filehandle.write(required)
        pytest.xfail("No reference template available")
    else:
        with open(reference) as filehandle:
            required = filehandle.read()
        required = required.replace('__USER__', username, 1)
        required = required.replace('__YEAR__', str(datetime.date.today().year), 1)
        assert written_spec == required
