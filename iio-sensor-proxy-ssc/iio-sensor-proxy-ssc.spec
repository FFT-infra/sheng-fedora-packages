%global debug_package %{nil}

Name:           iio-sensor-proxy-ssc
Version:        3.9
Release:        2%{?dist}
Provides:       iio-sensor-proxy%{?_isa}
Conflicts:      iio-sensor-proxy
Summary:        IIO sensors to D-Bus proxy (with Qualcomm SSC support)
# SPDX identifier instead of the legacy "GPLv3": upstream's meson.build declares
# the project GPLv3+ and only the individual file headers say "version 3", so
# "only" (the legacy GPLv3 tag) understated it — same call the Debian packaging
# in marble-deb-package makes in debian/copyright and Fedora in its own spec.
License:        GPL-3.0-or-later
URL:            https://gitlab.freedesktop.org/hadess/iio-sensor-proxy
Source0:        %{url}/-/archive/%{version}/iio-sensor-proxy-%{version}.tar.gz
Source1:        49-iio-sensor-proxy.rules
ExclusiveArch:  aarch64
BuildRequires:  gcc meson ninja-build
BuildRequires:  glib2-devel libgudev-devel polkit-devel
BuildRequires:  pkgconfig(udev) dbus-devel
BuildRequires:  libssc libqmi-devel libmbim-devel
BuildRequires:  systemd-rpm-macros
Requires:       dbus glib2 libgudev polkit
Requires:       libssc systemd

%description
iio-sensor-proxy with Qualcomm Sensor Core (SSC) support enabled.
Proxies IIO sensor data to D-Bus, enabling accelerometer, ambient light,
and proximity sensor access on Qualcomm Snapdragon platforms.

%prep
%autosetup -n iio-sensor-proxy-%{version}

%build
%meson \
    -Db_lto=true \
    -Dssc-support=enabled \
    -Dsystemdsystemunitdir=%{_unitdir}
%meson_build

%install
%meson_install
install -Dm644 %{SOURCE1} %{buildroot}%{_datadir}/polkit-1/rules.d/49-iio-sensor-proxy.rules

%files
# Upstream's own text and readme; GPL-3.0-or-later requires shipping the license
# text with the binary, and Fedora's iio-sensor-proxy spec does the same.
%license COPYING
%doc README.md
%{_bindir}/monitor-sensor
%{_libexecdir}/iio-sensor-proxy
%{_unitdir}/iio-sensor-proxy.service
%{_udevrulesdir}/80-iio-sensor-proxy.rules
%{_datadir}/dbus-1/system.d/net.hadess.SensorProxy.conf
%{_datadir}/polkit-1/actions/net.hadess.SensorProxy.policy
%{_datadir}/polkit-1/rules.d/49-iio-sensor-proxy.rules

%post
%systemd_post iio-sensor-proxy.service
systemctl enable iio-sensor-proxy.service

%preun
%systemd_preun iio-sensor-proxy.service

%postun
%systemd_postun_with_restart iio-sensor-proxy.service

%changelog
* Fri Oct 16 2026 Sheng Packaging <packaging@sheng.local> - 3.9-2
- License: GPLv3 -> SPDX GPL-3.0-or-later (matches upstream meson.build's GPLv3+)
- Ship the upstream license text and README (%license COPYING, %doc README.md)

* Mon Oct 12 2026 Sheng Packaging <packaging@sheng.local> - 3.9-1
- Rename iio-sensor-proxy-sheng to iio-sensor-proxy-ssc (SSC-enabled variant)
- Add Obsoletes: iio-sensor-proxy-sheng so upgrades auto-remove the old name
- Keep Provides/Conflicts: iio-sensor-proxy; drop device-specific wording
