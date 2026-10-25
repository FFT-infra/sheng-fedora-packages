%undefine        _debugsource_packages
# No debuginfo subpackage, matching the --nodebuginfo that the CI builds pass:
# Copr has no way to pass extra rpmbuild options, so the spec has to say it.
%global debug_package %{nil}
%global KERNEL_VER 7.2.6
%global KERNEL_TAG 7.2.6-mac
%global KERNEL_RPMVER 7.2.6
%global DEVICE_NAME sheng
%global PLATFORM_NAME sm8550
# Appended to the kernel release string so the patched kernel is distinguishable
# from the stock one by `uname -r` alone. Without it both builds produce
# 7.2.6-sm8550-g42f3b40 and neither the operator nor %pre can tell them apart.
%global IRIS_SUFFIX -iris1

Version:         %{KERNEL_RPMVER}
Release:         8.%{DEVICE_NAME}.iris1%{?dist}
ExclusiveArch:  aarch64
Name:            kernel-%{PLATFORM_NAME}
Summary:         Mainline Linux kernel for %{PLATFORM_NAME} devices
License:         GPL-2.0-only
URL:             https://github.com/ianchb/sm8550-mainline

Source0:         %{url}/archive/%{KERNEL_TAG}.tar.gz
Source1:         https://github.com/ianchb/sm8550-mainline/releases/download/%{KERNEL_VER}/sm8550.config
Source2:         scripts/mkbootimg
Source3:         extra-sm8550.config
Source4:         ukify.conf
Source5:         99-sheng-generic.conf
# The four Iris kernel patches this kernel carries. Each is owned by the
# driver repository and fetched here by commit, so there is exactly one copy
# of it.
#
# The commit is 5a0fcb5, which carries all four files plus their SHA256SUMS.
# It is also what the `iris-kernel-patches-v1` tag on that repository points
# at, so the URLs stay resolvable after the pull request branch that
# introduced them is gone. Do not repoint them at a commit that only a pull
# request head keeps alive: closing the request lets GitHub collect it and
# spectool then fails an hour into a build.
#
# 0001-0003 carry preimage blob ids that match the Source0 tag tree, so they
# apply at offset 0. 0004 was rebased from a different tree: its preimage is
# fdcf460, the tag has 246ad0a, and it lands at offset -3 lines in
# iris_buffer.c. All four apply with --fuzz=0, which is what %prep uses, so a
# genuine mismatch still fails the build.
#
# Source6: decode-order output plus a 64-buffer CAPTURE queue. Prerequisites
# for the zero-copy Import path; without them the driver falls back to
# display-order output and refuses Import.
Source6:         https://raw.githubusercontent.com/FFT-infra/qualcomm-iris-vaapi/5a0fcb58461deeb8b6392f07cb42b2804accbe9e/packaging/kernel/0001-media-iris-decode-order-output-and-64-capture-buffers.patch
# Source7: encoder loop-filter controls (H.264 mode/alpha/beta and the HEVC
# equivalents). Without them a non-default deblocking request is refused.
Source7:         https://raw.githubusercontent.com/FFT-infra/qualcomm-iris-vaapi/5a0fcb58461deeb8b6392f07cb42b2804accbe9e/packaging/kernel/0002-media-iris-deblocking-filter-controls.patch
# Source8: the encoder REQUEST_SYNC_FRAME control. Without it a requested IDR
# moves the intra period instead of asking the firmware for a sync frame.
Source8:         https://raw.githubusercontent.com/FFT-infra/qualcomm-iris-vaapi/5a0fcb58461deeb8b6392f07cb42b2804accbe9e/packaging/kernel/0003-media-iris-encoder-request-sync-frame.patch
# Source9: a CAPTURE error completion keeps the firmware timestamp. Without
# it a corrupt picture cannot be named and fails only at the drain or the
# sync bound.
Source9:         https://raw.githubusercontent.com/FFT-infra/qualcomm-iris-vaapi/5a0fcb58461deeb8b6392f07cb42b2804accbe9e/packaging/kernel/0004-media-iris-preserve-timestamps-on-error-buffers.patch
# sha256 of each source, in source order. spectool does not verify them; the
# %prep check does, so a rewritten upstream commit cannot silently change
# what this package ships.
%global IRIS_PATCH1_SHA256 be465d291212c127a93f87a98a68d8f299f82e16f27999b907ca16c6ea2071b7
%global IRIS_PATCH2_SHA256 f742c7aa1fd7a986070798813dd58b77765d9053a228e1897fca3021829ddf3a
%global IRIS_PATCH3_SHA256 b8e3600e79b9277448d7b84445cf28b623dbbac546081c685153e3dba247f0a9
%global IRIS_PATCH4_SHA256 75321dfa1731fcebcc171129e6f290ff6dd97b244ff087b25357673f9696ca52
Patch1:          0001-media-iris-decode-order-output-and-64-capture-buffers.patch
Patch2:          0002-media-iris-deblocking-filter-controls.patch
Patch3:          0003-media-iris-encoder-request-sync-frame.patch
Patch4:          0004-media-iris-preserve-timestamps-on-error-buffers.patch

BuildRequires:   bc bison dwarves diffutils elfutils-devel findutils git-core hmaccalc hostname make openssl-devel perl-interpreter rsync tar which flex bzip2 xz zstd python3 python3-devel python3-pyyaml rust rust-src bindgen rustfmt clippy opencsd-devel net-tools
BuildRequires:   clang lld llvm ccache systemd-boot-unsigned systemd-ukify

Provides:        kernel               = %{version}-%{release}
Provides:        kernel-core          = %{version}-%{release}
Provides:        kernel-modules       = %{version}-%{release}
Provides:        kernel-modules-core  = %{version}-%{release}
Requires:        dracut
Requires:        systemd-ukify
Requires:        systemd-boot-unsigned

%description
Mainline kernel for %{PLATFORM_NAME}, packaged for standard Fedora systems
with UEFI boot support. Built from source archive with commit hash resolved
from the upstream tag (e.g. %{KERNEL_VER}-%{PLATFORM_NAME}-gXXXXXXXXX), with
the four Iris patches applied and %{IRIS_SUFFIX} appended to the release
string.

%prep
%setup -q -n sm8550-mainline-%{KERNEL_TAG}

# Verify every Iris patch before applying any of them: the URLs above are
# pinned to a commit, but pinning a commit does not pin a hash, so this is the
# check that makes the payload reproducible. One check for all four, so a
# mismatch names the file instead of stopping on whichever came first.
(
  cd "%{_sourcedir}" &&
  echo "%{IRIS_PATCH1_SHA256}  0001-media-iris-decode-order-output-and-64-capture-buffers.patch
%{IRIS_PATCH2_SHA256}  0002-media-iris-deblocking-filter-controls.patch
%{IRIS_PATCH3_SHA256}  0003-media-iris-encoder-request-sync-frame.patch
%{IRIS_PATCH4_SHA256}  0004-media-iris-preserve-timestamps-on-error-buffers.patch" \
      | sha256sum -c -
)
%patch -P1 -P2 -P3 -P4 -p1

# Resolve tag to commit hash without full clone
COMMIT_HASH=$(git ls-remote %{url}.git refs/tags/%{KERNEL_TAG} | awk '{print $1}' | cut -c1-7)
echo "Tag %{KERNEL_TAG} commit: ${COMMIT_HASH}"
LOCALVERSION_FULL="-%{PLATFORM_NAME}-g${COMMIT_HASH}%{IRIS_SUFFIX}"
echo "${LOCALVERSION_FULL}" > .lkv_suffix

cp %{SOURCE1} .config
sed -i '/^CONFIG_LOCALVERSION=/d' .config
sed -i 's/^CONFIG_LOCALVERSION_AUTO=y/CONFIG_LOCALVERSION_AUTO=n/' .config

# Append extra config (zswap support); make olddefconfig normalizes it
cat %{SOURCE3} >> .config

%build
LOCALVERSION_FULL=$(cat .lkv_suffix)

export CCACHE_DIR="${CCACHE_DIR:-$HOME/.ccache}"
export CCACHE_MAXSIZE="${CCACHE_MAXSIZE:-10G}"
export CCACHE_SLOPPINESS="file_macro,locale,time_macros"
export CCACHE_NOHASHDIR="true"
mkdir -p "$CCACHE_DIR"

make ARCH=arm64 CC="ccache clang" LLVM=1 LOCALVERSION="${LOCALVERSION_FULL}" olddefconfig
make ARCH=arm64 CC="ccache clang" LLVM=1 LOCALVERSION="${LOCALVERSION_FULL}" \
    -j%{?_smp_build_ncpus} Image Image.gz modules dtbs

# Save the full kernel version for %%install
echo "%{KERNEL_VER}${LOCALVERSION_FULL}" > %{_topdir}/BUILD/kernel-version

%install
KERNEL_RELEASE=$(cat %{_topdir}/BUILD/kernel-version)
LOCALVERSION_FULL=$(cat .lkv_suffix)

# 1. Install modules
make ARCH=arm64 CC="ccache clang" LLVM=1 LOCALVERSION="${LOCALVERSION_FULL}" \
    INSTALL_MOD_PATH=%{buildroot} modules_install
rm -rf %{buildroot}/lib/modules/*/build
rm -rf %{buildroot}/lib/modules/*/source
# UsrMerge
mkdir -p %{buildroot}/usr
mv %{buildroot}/lib %{buildroot}/usr/

# 2. Install kernel image, System.map, and config to /boot. These are
#    versioned so multiple kernel versions can coexist; booting happens via
#    the flashed boot.img, not these /boot files.
install -Dm644 arch/arm64/boot/Image     %{buildroot}/boot/Image-${KERNEL_RELEASE}
install -Dm644 arch/arm64/boot/Image     %{buildroot}/boot/vmlinuz-${KERNEL_RELEASE}
install -Dm644 arch/arm64/boot/Image.gz  %{buildroot}/boot/Image.gz-${KERNEL_RELEASE}
install -Dm644 System.map                %{buildroot}/boot/System.map-${KERNEL_RELEASE}
install -Dm644 .config                   %{buildroot}/boot/config-${KERNEL_RELEASE}

# 3. Install device tree
install -Dm644 arch/arm64/boot/dts/qcom/sm8550-xiaomi-%{DEVICE_NAME}.dtb \
    %{buildroot}/boot/sm8550-xiaomi-%{DEVICE_NAME}-${KERNEL_RELEASE}.dtb
install -Dm644 arch/arm64/boot/dts/qcom/sm8550-xiaomi-%{DEVICE_NAME}.dtb \
    %{buildroot}/usr/lib/modules/${KERNEL_RELEASE}/dtb/qcom/sm8550-xiaomi-%{DEVICE_NAME}.dtb

# 4. Generate boot.img (Debian-style: outside of kernel tree, image.gz + dtb first)
cat arch/arm64/boot/Image.gz \
    arch/arm64/boot/dts/qcom/sm8550-xiaomi-%{DEVICE_NAME}.dtb \
    > Image.gz-dtb_%{DEVICE_NAME}
install -Dm644 Image.gz-dtb_%{DEVICE_NAME} \
    %{buildroot}/boot/Image.gz-dtb_%{DEVICE_NAME}-${KERNEL_RELEASE}
mv Image.gz-dtb_%{DEVICE_NAME} zImage_%{DEVICE_NAME}

chmod +x %{SOURCE2}
%{SOURCE2} --kernel zImage_%{DEVICE_NAME} \
    --cmdline "root=PARTLABEL=linux rootwait rw" \
    --base 0x00000000 --kernel_offset 0x00008000 \
    --tags_offset 0x01e00000 --pagesize 4096 --id \
    -o %{_topdir}/BUILD/boot_%{DEVICE_NAME}_dualboot.img
%{SOURCE2} --kernel zImage_%{DEVICE_NAME} \
    --cmdline "root=PARTLABEL=userdata rootwait rw" \
    --base 0x00000000 --kernel_offset 0x00008000 \
    --tags_offset 0x01e00000 --pagesize 4096 --id \
    -o %{_topdir}/BUILD/boot_%{DEVICE_NAME}_singleboot.img

# 6. Install UKI/dracut config (consumed by %posttrans)
install -Dm644 %{SOURCE4} %{buildroot}%{_sysconfdir}/systemd/ukify.conf
install -Dm644 %{SOURCE5} %{buildroot}%{_sysconfdir}/dracut.conf.d/99-sheng-generic.conf

%files
%license COPYING
/boot/Image-*
/boot/Image.gz-*
/boot/Image.gz-dtb_%{DEVICE_NAME}-*
/boot/sm8550-xiaomi-%{DEVICE_NAME}-*.dtb
/boot/vmlinuz-*
/boot/System.map-*
/boot/config-*
/usr/lib/modules/*
%config(noreplace) %{_sysconfdir}/systemd/ukify.conf
%config(noreplace) %{_sysconfdir}/dracut.conf.d/99-sheng-generic.conf

%pre
# Clean up old kernel files from previous version on upgrade
if [ -f /usr/lib/modules/.kernel-version ]; then
    OLD_KVER=$(cat /usr/lib/modules/.kernel-version)
    if [ -n "$OLD_KVER" ]; then
        rm -rf "/usr/lib/modules/$OLD_KVER" 2>/dev/null || :
        rm -f "/boot/System.map-$OLD_KVER" 2>/dev/null || :
        rm -f "/boot/config-$OLD_KVER" 2>/dev/null || :
        rm -f "/boot/vmlinuz-$OLD_KVER" 2>/dev/null || :
        rm -f "/boot/initramfs-$OLD_KVER.img" 2>/dev/null || :
        rm -f "/boot/efi/EFI/fedora/fedora-$OLD_KVER.efi" 2>/dev/null || :
        rm -f "/boot/Image-$OLD_KVER" 2>/dev/null || :
        rm -f "/boot/Image.gz-$OLD_KVER" 2>/dev/null || :
        rm -f "/boot/Image.gz-dtb_%{DEVICE_NAME}-$OLD_KVER" 2>/dev/null || :
        rm -f "/boot/sm8550-xiaomi-%{DEVICE_NAME}-$OLD_KVER.dtb" 2>/dev/null || :
    fi
fi

%posttrans
set -e

# Determine the newly installed kernel version from the modules directory.
# %pre removed the previous kernel's modules, so the newest (and only) left
# is this package's own. .kernel-version is intentionally not in %files so
# multiple kernel versions do not claim the same file.
KERNEL_RELEASE=$(ls -dt /usr/lib/modules/*/ 2>/dev/null | head -1 | sed 's#/$##; s#.*/##')
if [ -z "$KERNEL_RELEASE" ]; then
    echo "CRITICAL: no kernel modules directory found" >&2
    exit 1
fi
echo "${KERNEL_RELEASE}" > /usr/lib/modules/.kernel-version

# 1. Build module dependencies for the new kernel
depmod -a "${KERNEL_RELEASE}"

echo "--- Generating UKI for ${KERNEL_RELEASE} using dracut + ukify ---"

UKI_DIR="/boot/efi/EFI/fedora"
INITRD_PATH="/boot/initramfs-${KERNEL_RELEASE}.img"
KERNEL_PATH="/boot/vmlinuz-${KERNEL_RELEASE}"
DTB_PATH="/usr/lib/modules/${KERNEL_RELEASE}/dtb/qcom/sm8550-xiaomi-%{DEVICE_NAME}.dtb"
UKI_OUTPUT_PATH="${UKI_DIR}/fedora-${KERNEL_RELEASE}.efi"
mkdir -p "${UKI_DIR}"

# 2. Generate initramfs with dracut (reads /etc/dracut.conf.d/)
dracut --kver "${KERNEL_RELEASE}" --force
if [ ! -f "${INITRD_PATH}" ]; then
    echo "CRITICAL: dracut failed to generate initramfs at ${INITRD_PATH}" >&2
    exit 1
fi
echo "Initramfs generated at ${INITRD_PATH}"

# 3. Assemble the UKI with systemd-ukify. Static config (Cmdline/Stub) is read
#    from /etc/systemd/ukify.conf, which this package installs.
if [ ! -f /usr/lib/systemd/boot/efi/linuxaa64.efi.stub ]; then
    echo "CRITICAL: EFI stub /usr/lib/systemd/boot/efi/linuxaa64.efi.stub missing (install systemd-boot-unsigned)" >&2
    exit 1
fi
ukify build \
    --linux="${KERNEL_PATH}" \
    --initrd="${INITRD_PATH}" \
    --devicetree="${DTB_PATH}" \
    --output="${UKI_OUTPUT_PATH}"

if [ ! -f "${UKI_OUTPUT_PATH}" ]; then
    echo "CRITICAL: ukify failed to generate UKI at ${UKI_OUTPUT_PATH}" >&2
    rm -f "${INITRD_PATH}"
    exit 1
fi
echo "SUCCESS: UKI generated at ${UKI_OUTPUT_PATH}"

# 4. Remove the standalone initramfs; only the UKI is kept
rm -f "${INITRD_PATH}"

echo "--- UKI generation complete for ${KERNEL_RELEASE} ---"

%changelog
* Mon Oct 26 2026 Sheng Packaging <packaging@sheng.local> - 7.2.6-8.sheng.iris1
- Fetch the Iris patches from FFT-infra/qualcomm-iris-vaapi at 5a0fcb5, the
  commit the iris-kernel-patches-v1 tag points at. The previous commit was
  reachable only through a pull request head, which GitHub collects once the
  request closes; the payload is byte-identical (same four sha256 values).

* Sun Oct 25 2026 Sheng Packaging <packaging@sheng.local> - 7.2.6-7.sheng.iris1
- Carry all four Iris patches, not only decode-order: encoder loop-filter
  controls (Source7), the encoder REQUEST_SYNC_FRAME control (Source8) and
  the timestamp on CAPTURE error completions (Source9). Each is fetched by
  commit from phxinyang/qualcomm-iris-vaapi and verified by its own sha256
  before any patch is applied. The release number moves because the payload
  does; -iris1 stays so the module path is unchanged.

* Thu Oct 22 2026 Sheng Packaging <packaging@sheng.local> - 7.2.6-6.sheng.iris1
- Apply the Iris decode-order + 64-CAPTURE-buffer patch (Source6, fetched by
  commit from phxinyang/qualcomm-iris-vaapi and verified by sha256)
- Append -iris1 to the kernel release so uname -r distinguishes this kernel
  from the stock 7.2.6-sm8550-g42f3b40 build

* Sun Oct 18 2026 Sheng Packaging <packaging@sheng.local> - 7.2.6-5.sheng
- Drop the optional sheng DTS patch logic and its patch file

* Sat Oct 17 2026 Sheng Packaging <packaging@sheng.local> - 7.2.6-4.sheng
- License: GPLv2 -> GPL-2.0-only (SPDX; upstream sm8550-mainline carries the
  kernel's GPL-2.0 COPYING)
- Ship the upstream license text (%license COPYING)
