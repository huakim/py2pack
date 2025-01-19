# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Thomas Bechtold <tbechtold@suse.com>
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

"""Module containing utility functions that fit nowhere else."""

import os
import tempfile
import shutil
from contextlib import contextmanager
from build.util import project_wheel_metadata
import pwd
from email import parser
import json
from io import StringIO
from typing import List  # noqa: F401, pylint: disable=unused-import
try:
    import tomllib as toml
except ModuleNotFoundError:
    import tomli as toml

import tarfile
import zipfile
from importlib import metadata
from backports.entry_points_selectable import EntryPoint, EntryPoints


def _get_archive_filelist(filename):
    # type: (str) -> List[str]
    """Extract the list of files from a tar or zip archive.

    Args:
        filename: name of the archive

    Returns:
        Sorted list of files in the archive, excluding './'

    Raises:
        ValueError: when the file is neither a zip nor a tar archive
        FileNotFoundError: when the provided file does not exist (for Python 3)
        IOError: when the provided file does not exist (for Python 2)
    """
    names = []  # type: List[str]
    if tarfile.is_tarfile(filename):
        with tarfile.open(filename) as tar_file:
            names = sorted(tar_file.getnames())
    elif zipfile.is_zipfile(filename):
        with zipfile.ZipFile(filename) as zip_file:
            names = sorted(zip_file.namelist())
    else:
        raise ValueError("Can not get filenames from '{!s}'. "
                         "Not a tar or zip file".format(filename))
    if "./" in names:
        names.remove("./")
    return names


def parse_pyproject(archive):
    """Parse the pyproject.toml in the archive and return the metadata as dict.

    Args:
        archive: the filename of the archive

    Returns:
        dict of metadata. Empty if no pyproject.toml was found in the toplevel directory
    """
    pyproject = {}
    if tarfile.is_tarfile(archive):
        with tarfile.open(archive) as tar_file:
            for m in tar_file:
                if m.name.endswith('pyproject.toml') and m.name.count("/") == 1:
                    with tar_file.extractfile(m) as fh:
                        pyproject = toml.load(fh)
                    break
    elif zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zip_file:
            for name in zip_file.namelist():
                if name.endswith('pyproject.toml') and name.count("/") == 1:
                    with zip_file.open(name) as fh:
                        pyproject = toml.load(fh)
                    break
    else:
        raise ValueError("Can not extract pyproject.toml from '{!s}'. "
                         "Not a tar or zip file".format(archive))
    return pyproject


def get_pyproject_table(data, key, notfound=None):
    """Return the contents of a toml table.

    Args:
        data: dict of toml contents
        key: period separated table name, e.g. "project.dependencies"
        notfound: return this if the table is not in data, None by default

    Returns:
        content of table (list or dict) or notfound
    """
    table = data
    for level in key.split("."):
        if level in table:
            table = table[level]
        else:
            return notfound
    return table


def get_setuptools_scripts(data):
    """parse setuptools entry_points and return all script names.

    Setuptools style entry_points as returned by metaextract may be
    a string with .ini-style sections or a dict

    (The PEP518 projects.entry-points table does not have scripts subtables.)

    Args:
        data: dict of metadata

    Returns:
        list of script names
    """
    entry_points = data.get('entry_points', None)
    if isinstance(entry_points, str):
        eps = EntryPoints(EntryPoints._from_text(entry_points))
    elif isinstance(entry_points, dict):
        eps = EntryPoints([EntryPoint(*map(str.strip, entry.split("=", 1)), groupname)
                           for groupname, group in entry_points.items()
                           for entry in group
                           if groupname in ["console_scripts", "gui_scripts"]])
    else:
        return []
    scripts = (list(eps.select(group="console_scripts").names) +
               list(eps.select(group="gui_scripts").names))
    return scripts


@contextmanager
def _extract_to_tempdir(archive_filename):
    """extract the given tarball or zipfile to a tempdir and change
    the cwd to the new tempdir. Delete the tempdir at the end"""
    if not os.path.exists(archive_filename):
        raise Exception("Archive '%s' does not exist" % (archive_filename))

    tempdir = tempfile.mkdtemp(prefix="py2pack_")
    current_cwd = os.getcwd()
    try:
        if tarfile.is_tarfile(archive_filename):
            with tarfile.open(archive_filename) as f:
                f.extractall(tempdir)
        elif zipfile.is_zipfile(archive_filename):
            with zipfile.ZipFile(archive_filename) as f:
                f.extractall(tempdir)
        else:
            raise Exception("Can not extract '%s'. "
                            "Not a tar or zip file" % archive_filename)
        os.chdir(tempdir)
        yield tempdir
    finally:
        os.chdir(current_cwd)
        shutil.rmtree(tempdir)


def get_metadata(filename):
    """
    Extracts metadata from the archive filename
    """
    data = {}

    with _extract_to_tempdir(filename) as root_dir:
        dir_list, *_ = os.listdir(root_dir)
        path = os.path.join(root_dir, dir_list)
        mdata = project_wheel_metadata(path, isolated=True)

        data['home_page'] = mdata.get('Home-page')
        data['name'] = mdata.get('Name')
        data['version'] = mdata.get('Version')
        data['description'] = mdata.get('Description')
        data['summary'] = mdata.get('Summary')
        data['license'] = mdata.get('License')
        data['keywords'] = mdata.get('Keywords')
        data['author'] = mdata.get('Author')
        data['author_email'] = mdata.get('Author-email')
        data['maintainer'] = mdata.get('Maintainer')
        data['maintainer_email'] = mdata.get('Maintainer-email')
        data['install_requires'] = mdata.get_all('Requires-Dist')

    return data


def get_user_name():
    return pwd.getpwuid(os.getuid()).pw_name


def no_ending_dot(summary):
    count = len(summary)
    while count > 0:
        count -= 1
        if summary[count] != '.':
            count += 1
            break
    if count == 0:
        return ''
    return summary[0:count]


def single_line(summary):
    return str(summary).replace('\n', ' ').strip()


def pypi_text_file(pkg_info_path):
    pkg_info_file = open(pkg_info_path, 'r')
    text = pypi_text_stream(pkg_info_file)
    pkg_info_file.close()
    return text


def pypi_text_stream(pkg_info_stream):
    pkg_info_lines = parser.Parser().parse(pkg_info_stream)
    return pypi_text_items(pkg_info_lines.items())


def pypi_text_metaextract(library):
    pkg_info_lines = metadata.metadata(library)
    return pypi_text_items(pkg_info_lines.items())


def pypi_text_items(pkg_info_items):
    pkg_info_dict = {}
    for key, value in pkg_info_items:
        key = key.lower().replace('-', '_')
        if key in {'requires_dist', 'provides_extra'}:
            val = dict.setdefault(pkg_info_dict, key, [])
            val.append(value)
        elif key in {'classifier'}:
            val = dict.setdefault(pkg_info_dict, key + 's', [])
            val.append(value)
        elif key in {'project_url'}:
            key1, val = value.split(',', 1)
            pkg_info_dict.setdefault(key + 's', {})[key1.strip()] = val.strip()
        else:
            pkg_info_dict[key] = value
    return {'info': pkg_info_dict, 'urls': []}


def pypi_json_file(file_path):
    json_file = open(file_path, 'r')
    js = pypi_json_stream(json_file)
    json_file.close()
    return js


def pypi_json_stream(json_stream):
    js = json.load(json_stream)
    if 'info' not in js:
        js = {'info': js}
    if 'urls' not in js:
        js['urls'] = []
    return js


def _check_if_pypi_archive_file(path):
    return path.count('/') == 1 and os.path.basename(path) == 'PKG-INFO'


def pypi_archive_file(file_path):
    if tarfile.is_tarfile(file_path):
        with tarfile.open(file_path, 'r') as archive:
            for member in archive.getmembers():
                if _check_if_pypi_archive_file(member.name):
                    return pypi_text_stream(StringIO(archive.extractfile(member).read().decode()))
    elif zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, 'r') as archive:
            for member in archive.namelist():
                if _check_if_pypi_archive_file(member):
                    return pypi_text_stream(StringIO(archive.open(member).read().decode()))
    else:
        raise Exception("Can not extract '%s'. Not a tar or zip file" % file_path)
    raise KeyError('PKG-INFO not found on archive ' + file_path)
