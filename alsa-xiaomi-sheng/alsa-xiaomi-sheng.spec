%global debug_package %{nil}

Name:           alsa-xiaomi-sheng
Version:        1.0
Release:        2%{?dist}
Summary:        ALSA UCM configuration for Xiaomi Pad 6S Pro (sheng)
License:        BSD-3-Clause
URL:            https://github.com/map220v/alsa-ucm-conf
BuildArch:      noarch
Requires:       alsa-ucm
Source0:        %{name}-%{version}.tar.gz

%description
ALSA Use Case Manager configuration for Xiaomi Pad 6S Pro 12.4 (sheng).
Provides audio routing profiles for speakers, headphones, HDMI/DisplayPort,
and microphones via the Qualcomm SM8550 audio subsystem (WCD938X codec +
CS35L43 speaker amplifiers).

%prep
%autosetup

%build
# Nothing to build

%install
mkdir -p %{buildroot}%{_datadir}/alsa/ucm2/Xiaomi/sheng
cp -a usr/share/alsa/ucm2/Xiaomi/sheng/* %{buildroot}%{_datadir}/alsa/ucm2/Xiaomi/sheng/
install -Dm644 etc/modprobe.d/99-sheng-alsa-no-snd-seq.conf \
    %{buildroot}%{_sysconfdir}/modprobe.d/99-sheng-alsa-no-snd-seq.conf

%files
%defattr(644, root, root, 755)
%{_datadir}/alsa/ucm2/Xiaomi/sheng
%config(noreplace) %{_sysconfdir}/modprobe.d/99-sheng-alsa-no-snd-seq.conf

%changelog
* Sat Oct 17 2026 Sheng Packaging <packaging@sheng.local> - 1.0-2
- License: MIT -> BSD-3-Clause. The UCM files under
  %{_datadir}/alsa/ucm2/Xiaomi/sheng come from map220v/alsa-ucm-conf, whose
  LICENSE is BSD 3-Clause, not MIT.
