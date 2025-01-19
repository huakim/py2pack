#
# spec file for package python-setuppy
#
# Copyright (c) __YEAR__ SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           python-setuppy
Version:        2021.6.4
Release:        0
Summary:        setup.py generator
License:        Unlicense (FIXME:No SPDX)
URL:            https://github.com/git/setuppy.py
Source:         https://files.pythonhosted.org/packages/source/s/setuppy/setuppy-%{version}.tar.gz
BuildRequires:  python-rpm-macros
BuildRequires:  %{python_module pip}
BuildRequires:  fdupes
BuildArch:      noarch
%python_subpackages

%description
[![](https://img.shields.io/badge/released-2021.6.4-green.svg?longCache=True)](https://pypi.org/project/setuppy/)
[![](https://img.shields.io/badge/license-Unlicense-blue.svg?longCache=True)](https://unlicense.org/)

### Installation
```bash
$ pip install setuppy
```

### How it works
+   environment variables `SETUPPY_KEY`
+   attrs
+   methods `get_key`

##### default methods
method|value
-|-
`get_install_requires`|`requirements.txt` lines
`get_name`|`os.path.basename(os.getcwd()).split('.')[0]`
`get_packages`|`setuptools.find_packages()`
`get_scripts`|`bin/` or `scripts/` files

### Examples
```bash
$ cd path/to/project
$ export SETUPPY_VERSION="42"
$ python -m setuppy > setup.py
```

`setup.py`
```python
setup(
    name='project',
    version='42',
    install_requires=[
        ...
    ],
    packages=[
        ...
    ]
)
```




subclassing
```python
from setuppy import SetupPy

class MySetupPy(SetupPy):
    def get_scripts(self):
        ...

print(MySetupPy(version="42"))
```

%prep
%autosetup -p1 -n setuppy-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%python_expand %fdupes %{buildroot}%{$python_sitelib}

%files %{python_files}
%{python_sitelib}/setuppy
%{python_sitelib}/setuppy-%{version}.dist-info

%changelog
