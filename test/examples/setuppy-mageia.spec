%define mod_name setuppy

Name:           python-%{mod_name}
Version:        2021.6.4
Release:        %mkrel 1
Url:            https://github.com/git/setuppy.py
Summary:        setup.py generator
License:        Unlicense (FIXME:No SPDX)
Group:          Development/Python
Source:         https://files.pythonhosted.org/packages/source/s/setuppy/setuppy-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-buildroot
BuildRequires:  python-devel

%description
setup.py generator


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
