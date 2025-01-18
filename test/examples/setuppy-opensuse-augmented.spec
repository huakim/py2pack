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
Summary:        setuppy generator
License:        FIXME-UNKNOWN
URL:            https://github.com/git/setuppy.py
Source:         https://files.pythonhosted.org/packages/source/s/setuppy/setuppy-%{version}.tar.gz
BuildRequires:  python-rpm-macros
BuildRequires:  %{python_module pip}
BuildRequires:  %{python_module setuptools}
BuildRequires:  %{python_module wheel}
BuildRequires:  fdupes
BuildArch:      noarch
%python_subpackages

%description
None

%prep
%autosetup -p1 -n setuppy-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%python_expand %fdupes %{buildroot}%{$python_sitelib}

%files %{python_files}
%doc README.md
%{python_sitelib}/setuppy
%{python_sitelib}/setuppy-%{version}.dist-info

%changelog
