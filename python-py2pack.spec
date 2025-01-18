Name:           python-py2pack
Version:        0.9.0
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        Generate distribution packages from PyPI

# No license information obtained, it's up to the packager to fill it in
License:        LGPL
URL:            https://github.com/openSUSE/py2pack
Source:         %{pypi_source py2pack}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'py2pack' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-py2pack
Summary:        %{summary}

%description -n python3-py2pack %_description


%prep
%autosetup -p1 -n py2pack-%{version}


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
# Add top-level Python module names here as arguments, you can use globs
%pyproject_save_files -l ...


%check
%pyproject_check_import


%files -n python3-py2pack -f %{pyproject_files}


%changelog
%autochangelog
