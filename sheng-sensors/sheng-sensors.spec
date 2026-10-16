%global debug_package %{nil}

Name:           sheng-sensors
Version:        20240917
Release:        3%{?dist}
Summary:        Sensor configuration files for Xiaomi Pad 6S Pro (sheng)
License:        Unknown
URL:            https://github.com/ianchb/sm8550-mainline
BuildArch:      noarch
BuildRequires:  systemd-rpm-macros
Requires:       fastrpc
Requires:       fastrpc-services
Source0:        %{name}-%{version}.tar.gz
Source1:        adsprpcd-sensorspd.service

%description
Proprietary sensor configuration files (JSON configs, udev rules, systemd
overrides) for the Qualcomm Sensor Core on Xiaomi Pad 6S Pro (SM8550).

%prep
%autosetup

%build
# Nothing to build

%install
mkdir -p %{buildroot}%{_prefix}
cp -a usr/* %{buildroot}%{_prefix}/
# Fedora's fastrpc-services only ships rootpd/audiopd/sdsp units; the SensorPD
# daemon (adsprpcd sensorspd) is missing, so we ship it here. libadsprpc looks
# for the machine config under /usr/share/hexagon-dsp/conf.d, while the config
# tree actually lives under /usr/share/qcom — symlink to bridge the gap.
install -Dm644 %{SOURCE1} %{buildroot}%{_unitdir}/adsprpcd-sensorspd.service
ln -s qcom %{buildroot}%{_datadir}/hexagon-dsp

%files
%dir %{_datadir}/qcom
%{_datadir}/qcom/conf.d
%{_datadir}/qcom/sm8550
%{_prefix}/lib/udev/rules.d/81-sheng-ssc-sensors.rules
%{_prefix}/lib/udev/rules.d/99-touchscreen-sheng.rules
%{_prefix}/lib/systemd/system/iio-sensor-proxy.service.d/10-sheng-sensors.conf
%{_unitdir}/adsprpcd-sensorspd.service
%{_datadir}/hexagon-dsp

%post
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload || :
    if [ -e /sys/devices/virtual/misc/fastrpc-adsp ]; then
        udevadm trigger /sys/devices/virtual/misc/fastrpc-adsp || :
    fi
fi
%systemd_post adsprpcd-sensorspd.service
if command -v systemctl >/dev/null 2>&1; then
    systemctl daemon-reload || :
    if [ -d /run/systemd/system ]; then
        systemctl try-restart iio-sensor-proxy.service || :
    fi
fi

%preun
%systemd_preun adsprpcd-sensorspd.service

%postun
%systemd_postun_with_restart adsprpcd-sensorspd.service

%changelog
* Sat Oct 17 2026 Sheng Packaging <packaging@sheng.local> - 20240917-3
- License: Proprietary -> Unknown. "Proprietary" is not a valid SPDX tag and
  does not describe config files whose provenance mixes the GPL-2.0 mainline
  tree with local units; left unclassified on purpose.

* Mon Oct 12 2026 Sheng Packaging <packaging@sheng.local> - 20240917-2
- Drop Requires: iio-sensor-proxy-ssc; sheng-sensors is config-only and no
  longer forces the SSC-enabled proxy. Install iio-sensor-proxy-ssc separately.

* Mon Oct 12 2026 ianchb <ianchb@users.noreply.github.com> - 20240917-1
- Ship adsprpcd-sensorspd.service (SensorPD daemon missing from fastrpc-services)
  and symlink /usr/share/hexagon-dsp -> qcom so libadsprpc finds the machine
  config. Require fastrpc and fastrpc-services.

