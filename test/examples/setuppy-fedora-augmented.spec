%define pypi_name setuppy
%define python_name python3-%{pypi_name}
Name:           python-%{pypi_name}
Version:        2021.6.4
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        setup.py generator

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        FIXME-UNKNOWN
URL:            https://github.com/git/setuppy.py
Source:         https://files.pythonhosted.org/packages/source/s/setuppy/setuppy-%{version}.tar.gz

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  fdupes
BuildArch:      noarch

# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
None}

%description %_description

%package -n %{python_name}
Summary:        %{summary}

%description -n %{python_name} %_description

%prep
%autosetup -p1 -n setuppy-%{version}


%generate_buildrequires
# Keep only those extras which you actually want to package or use during tests
%pyproject_buildrequires 


%build
%pyproject_wheel


%install
%pyproject_install
# For official Fedora packages, including files with '*' +auto is not allowed
# Replace it with a list of relevant Python modules/globs and list extra files in %%files
%pyproject_save_files '*' +auto

%files -n %{python_name} -f %{pyproject_files}

%changelog
%autochangelog

