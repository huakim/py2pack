%define mod_name sampleproject

Name:           python-%{mod_name}
Version:        3.0.0
Release:        %mkrel 1
Url:            
Summary:        A sample Python project
License:        Copyright (c) 2016 The Python Packaging Authority (PyPA)  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.  (FIXME:No SPDX)
Group:          Development/Python
Source:         https://files.pythonhosted.org/packages/source/s/sampleproject/sampleproject-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-buildroot
BuildRequires:  python-devel

%description
A sample Python project


%prep
%setup -q -n %{mod_name}-%{version}

%build
%{__python} setup.py build

%install
%{__python} setup.py install --prefix=%{_prefix} --root=%{buildroot}

%clean
rm -rf %{buildroot}

%files -f
%defattr(-,root,root)
%{python_sitelib}/*
