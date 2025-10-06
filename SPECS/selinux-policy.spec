## START: Set by rpmautospec
## (rpmautospec version 0.6.5)
## RPMAUTOSPEC: autochangelog
## END: Set by rpmautospec

# Conditionals for policy types (all built by default)
%bcond targeted 1
%bcond minimum  1
%bcond mls      1

# github repo with selinux-policy sources
%global giturl https://github.com/fedora-selinux/selinux-policy
%global commit 061ed78f650a71a7f47e9a9dcc20e0880e108346
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%define distro redhat
%define polyinstatiate n
%define monolithic n

%define POLICYVER 34
%define POLICYCOREUTILSVER 3.8
%define CHECKPOLICYVER 3.8
Summary: SELinux policy configuration
Name: selinux-policy
Version: 40.13.26
Release: 1%{?dist}
License: GPL-2.0-or-later
Source: %{giturl}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1: Makefile.devel
Source2: selinux-policy.conf

# Tool helps during policy development, to expand system m4 macros to raw allow rules
# Git repo: https://github.com/fedora-selinux/macro-expander.git
Source3: macro-expander

# Include SELinux policy for container from separate container-selinux repo
# Git repo: https://github.com/containers/container-selinux.git
Source4: container-selinux.tgz

# do not ship these modules
Source15: modules-filtered.lst
# modules enabled in -minimum policy
Source16: modules-minimum.lst

Source36: selinux-check-proper-disable.service

# Script to convert /var/run file context entries to /run
Source37: varrun-convert.sh
# Configuration files to dnf-protect targeted and/or mls subpackages
Source38: selinux-policy-targeted.conf
Source39: selinux-policy-mls.conf

# Provide rpm macros for packages installing SELinux modules
Source5: rpm.macros

Url: %{giturl}
BuildArch: noarch
BuildRequires: python3 gawk checkpolicy >= %{CHECKPOLICYVER} m4 policycoreutils-devel >= %{POLICYCOREUTILSVER} bzip2
BuildRequires: make
BuildRequires: systemd-rpm-macros
BuildRequires: groff
Requires(pre): policycoreutils >= %{POLICYCOREUTILSVER}
Requires(post): /bin/awk /usr/bin/sha512sum
Requires(meta): (rpm-plugin-selinux if rpm-libs)
Requires: selinux-policy-any = %{version}-%{release}
Provides: selinux-policy-base = %{version}-%{release}
Suggests: selinux-policy-targeted

%description
SELinux core policy package.
Originally based off of reference policy,
the policy has been adjusted to provide support for Fedora.

%files
%{!?_licensedir:%global license %%doc}
%license COPYING
%dir %{_datadir}/selinux
%dir %{_datadir}/selinux/packages
%dir %{_sysconfdir}/selinux
%ghost %config(noreplace) %{_sysconfdir}/selinux/config
%ghost %{_sysconfdir}/sysconfig/selinux
%{_usr}/lib/tmpfiles.d/selinux-policy.conf
%{_rpmconfigdir}/macros.d/macros.selinux-policy
%{_unitdir}/selinux-check-proper-disable.service
%{_libexecdir}/selinux/varrun-convert.sh

%package sandbox
Summary: SELinux sandbox policy
Requires(pre): selinux-policy-base = %{version}-%{release}
Requires(pre): selinux-policy-targeted = %{version}-%{release}

%description sandbox
SELinux sandbox policy for use with the sandbox utility.

%files sandbox
%verify(not md5 size mtime) %{_datadir}/selinux/packages/sandbox.pp

%post sandbox
rm -f %{_sysconfdir}/selinux/*/modules/active/modules/sandbox.pp.disabled 2>/dev/null
rm -f %{_sharedstatedir}/selinux/*/active/modules/disabled/sandbox 2>/dev/null
%{_sbindir}/semodule -n -X 100 -i %{_datadir}/selinux/packages/sandbox.pp 2> /dev/null
if %{_sbindir}/selinuxenabled ; then
    %{_sbindir}/load_policy
fi;
exit 0

%preun sandbox
if [ $1 -eq 0 ] ; then
    %{_sbindir}/semodule -n -d sandbox 2>/dev/null
    if %{_sbindir}/selinuxenabled ; then
        %{_sbindir}/load_policy
    fi;
fi;
exit 0

%package devel
Summary: SELinux policy development files
Requires(pre): selinux-policy = %{version}-%{release}
Requires: selinux-policy = %{version}-%{release}
Requires: m4 checkpolicy >= %{CHECKPOLICYVER}
Requires: /usr/bin/make
Requires(post): policycoreutils-devel >= %{POLICYCOREUTILSVER}

%description devel
SELinux policy development package.
This package contains:
- interfaces, macros, and patterns for policy development
- a policy example
- the macro-expander utility
and some additional files.

%files devel
%{_bindir}/macro-expander
%dir %{_datadir}/selinux/devel
%dir %{_datadir}/selinux/devel/include
%{_datadir}/selinux/devel/include/*
%exclude %{_datadir}/selinux/devel/include/contrib/container.if
%dir %{_datadir}/selinux/devel/html
%{_datadir}/selinux/devel/html/*html
%{_datadir}/selinux/devel/html/*css
%{_datadir}/selinux/devel/Makefile
%{_datadir}/selinux/devel/example.*
%{_datadir}/selinux/devel/policy.*
%ghost %verify(not md5 size mode mtime) %{_sharedstatedir}/sepolgen/interface_info

%post devel
%{_sbindir}/selinuxenabled && %{_bindir}/sepolgen-ifgen 2>/dev/null
exit 0

%package doc
Summary: SELinux policy documentation
Requires(pre): selinux-policy = %{version}-%{release}
Requires: selinux-policy = %{version}-%{release}

%description doc
SELinux policy documentation package.
This package contains manual pages and documentation of the policy modules.

%files doc
%{_mandir}/man*/*
%exclude %{_mandir}/man8/container_selinux.8.gz
%doc %{_datadir}/doc/%{name}

%define common_params DISTRO=%{distro} UBAC=n DIRECT_INITRC=n MONOLITHIC=%{monolithic} MLS_CATS=1024 MCS_CATS=1024

%define makeCmds() \
%make_build %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 bare \
%make_build %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 conf \
install -p -m0644 ./dist/%1/booleans.conf ./policy/booleans.conf \
install -p -m0644 ./dist/%1/users ./policy/users \

%define makeModulesConf() \
install -p -m0644 ./dist/%1/modules.conf ./policy/modules.conf \

%define installCmds() \
%make_build %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 base.pp \
%make_build %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 validate modules \
make %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 DESTDIR=%{buildroot} install \
make %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 DESTDIR=%{buildroot} install-appconfig \
make %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 DESTDIR=%{buildroot} SEMODULE="%{_sbindir}/semodule -p %{buildroot} -X 100 " load \
%{__mkdir} -p %{buildroot}%{_sysconfdir}/selinux/%1/logins \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.subs \
install -p -m0644 ./config/file_contexts.subs_dist %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files \
install -p -m0644 ./dist/%1/setrans.conf %{buildroot}%{_sysconfdir}/selinux/%1/setrans.conf \
install -p -m0644 ./dist/customizable_types %{buildroot}%{_sysconfdir}/selinux/%1/contexts/customizable_types \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.bin \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.local \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.local.bin \
install -p -m0644 ./dist/booleans.subs_dist %{buildroot}%{_sysconfdir}/selinux/%1 \
rm -f %{buildroot}%{_datadir}/selinux/%1/*pp*  \
%{_bindir}/sha512sum %{buildroot}%{_sysconfdir}/selinux/%1/policy/policy.%{POLICYVER} | cut -d' ' -f 1 > %{buildroot}%{_sysconfdir}/selinux/%1/.policy.sha512; \
rm -rf %{buildroot}%{_sysconfdir}/selinux/%1/contexts/netfilter_contexts  \
rm -rf %{buildroot}%{_sysconfdir}/selinux/%1/modules/active/policy.kern \
rm -f %{buildroot}%{_sharedstatedir}/selinux/%1/active/*.linked \
%nil

%define fileList() \
%defattr(-,root,root) \
%dir %{_sysconfdir}/selinux/%1 \
%config(noreplace) %{_sysconfdir}/selinux/%1/setrans.conf \
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/seusers \
%dir %{_sysconfdir}/selinux/%1/logins \
%dir %{_sharedstatedir}/selinux/%1/active \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/semanage.read.LOCK \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/semanage.trans.LOCK \
%dir %attr(700,root,root) %dir %{_sharedstatedir}/selinux/%1/active/modules \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/modules/100/base \
%dir %{_sysconfdir}/selinux/%1/policy/ \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/policy/policy.%{POLICYVER} \
%{_sysconfdir}/selinux/%1/.policy.sha512 \
%dir %{_sysconfdir}/selinux/%1/contexts \
%config %{_sysconfdir}/selinux/%1/contexts/customizable_types \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/securetty_types \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/dbus_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/x_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/default_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/virtual_domain_context \
%config %{_sysconfdir}/selinux/%1/contexts/virtual_image_context \
%config %{_sysconfdir}/selinux/%1/contexts/lxc_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/systemd_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/sepgsql_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/openssh_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/snapperd_contexts \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/default_type \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/failsafe_context \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/initrc_context \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/removable_context \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/userhelper_context \
%dir %{_sysconfdir}/selinux/%1/contexts/files \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts \
%ghost %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.bin \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.homedirs \
%ghost %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.homedirs.bin \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.local \
%ghost %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.local.bin \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.subs \
%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.subs_dist \
%{_sysconfdir}/selinux/%1/booleans.subs_dist \
%config %{_sysconfdir}/selinux/%1/contexts/files/media \
%dir %{_sysconfdir}/selinux/%1/contexts/users \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/root \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/guest_u \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/xguest_u \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/user_u \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/staff_u \
%dir %{_datadir}/selinux/%1 \
%{_datadir}/selinux/%1/base.lst \
%{_datadir}/selinux/%1/modules.lst \
%{_datadir}/selinux/%1/nonbasemodules.lst \
%dir %{_sharedstatedir}/selinux/%1 \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/commit_num \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/users_extra \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/homedir_template \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/seusers \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/file_contexts \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/policy.kern \
%ghost %{_sharedstatedir}/selinux/%1/active/policy.linked \
%ghost %{_sharedstatedir}/selinux/%1/active/seusers.linked \
%ghost %{_sharedstatedir}/selinux/%1/active/users_extra.linked \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/file_contexts.homedirs \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/modules_checksum \
%ghost %verify(not mode md5 size mtime) %{_sharedstatedir}/selinux/%1/active/modules/400/extra_varrun \
%ghost %verify(not mode md5 size mtime) %{_sharedstatedir}/selinux/%1/active/modules/400/extra_varrun/cil \
%ghost %verify(not mode md5 size mtime) %{_sharedstatedir}/selinux/%1/active/modules/400/extra_varrun/lang_ext \
%nil

%define relabel() \
if [ -s %{_sysconfdir}/selinux/config ]; then \
    . %{_sysconfdir}/selinux/config &> /dev/null || true; \
fi; \
FILE_CONTEXT=%{_sysconfdir}/selinux/%1/contexts/files/file_contexts; \
if %{_sbindir}/selinuxenabled && [ "${SELINUXTYPE}" = %1 -a -f ${FILE_CONTEXT}.pre ]; then \
     %{_sbindir}/fixfiles -C ${FILE_CONTEXT}.pre restore &> /dev/null > /dev/null; \
     rm -f ${FILE_CONTEXT}.pre; \
fi; \
# rebuilding the rpm database still can sometimes result in an incorrect context \
%{_sbindir}/restorecon -R /usr/lib/sysimage/rpm \
# In some scenarios, /usr/bin/httpd is labelled incorrectly after sbin merge. \
# Relabel all files under /usr/bin, in case they got installed before policy \
# was updated and the labels were incorrect. \
%{_sbindir}/restorecon -R /usr/bin /usr/sbin \
if %{_sbindir}/restorecon -e /run/media -R /root /var/log /var/run /etc/passwd* /etc/group* /etc/*shadow* 2> /dev/null;then \
    continue; \
fi;

%define preInstall() \
if [ $1 -ne 1 ] && [ -s %{_sysconfdir}/selinux/config ]; then \
     for MOD_NAME in ganesha ipa_custodia kdbus; do \
        if [ -d %{_sharedstatedir}/selinux/%1/active/modules/100/$MOD_NAME ]; then \
           %{_sbindir}/semodule -n -d $MOD_NAME 2> /dev/null; \
        fi; \
     done; \
     . %{_sysconfdir}/selinux/config; \
     FILE_CONTEXT=%{_sysconfdir}/selinux/%1/contexts/files/file_contexts; \
     if [ "${SELINUXTYPE}" = %1 -a -f ${FILE_CONTEXT} ]; then \
        [ -f ${FILE_CONTEXT}.pre ] || cp -f ${FILE_CONTEXT} ${FILE_CONTEXT}.pre; \
     fi; \
     touch %{_sysconfdir}/selinux/%1/.rebuild; \
     if [ -e %{_sysconfdir}/selinux/%1/.policy.sha512 ]; then \
        POLICY_FILE=`ls %{_sysconfdir}/selinux/%1/policy/policy.* | sort | head -1` \
        sha512=`sha512sum $POLICY_FILE | cut -d ' ' -f 1`; \
	checksha512=`cat %{_sysconfdir}/selinux/%1/.policy.sha512`; \
	if [ "$sha512" == "$checksha512" ] ; then \
		rm %{_sysconfdir}/selinux/%1/.rebuild; \
	fi; \
   fi; \
fi;

%define postInstall() \
if [ -s %{_sysconfdir}/selinux/config ]; then \
    . %{_sysconfdir}/selinux/config &> /dev/null || true; \
fi; \
if [ -e %{_sysconfdir}/selinux/%2/.rebuild ]; then \
   rm %{_sysconfdir}/selinux/%2/.rebuild; \
fi; \
%{_sbindir}/semodule -B -n -s %2 2> /dev/null; \
[ "${SELINUXTYPE}" == "%2" ] && %{_sbindir}/selinuxenabled && load_policy; \
if [ %1 -eq 1 ]; then \
   %{_sbindir}/restorecon -R /root /var/log /run /etc/passwd* /etc/group* /etc/*shadow* 2> /dev/null; \
else \
%relabel %2 \
fi;

%define modulesList() \
awk '$1 !~ "/^#/" && $2 == "=" && $3 == "module" { printf "%%s ", $1 }' ./policy/modules.conf > %{buildroot}%{_datadir}/selinux/%1/modules.lst \
awk '$1 !~ "/^#/" && $2 == "=" && $3 == "base" { printf "%%s ", $1 }' ./policy/modules.conf > %{buildroot}%{_datadir}/selinux/%1/base.lst \

%define nonBaseModulesList() \
modules=`cat %{buildroot}%{_datadir}/selinux/%1/modules.lst` \
for i in $modules; do \
    if [ $i != "sandbox" ] && ! grep -E "^$i$" %{SOURCE15}; then \
        echo "%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/modules/100/$i" >> %{buildroot}%{_datadir}/selinux/%1/nonbasemodules.lst \
    else \
        rm -rf %{buildroot}%{_sharedstatedir}/selinux/{targeted,minimum,mls}/active/modules/100/$i \
    fi \
done;

# Make sure the config is consistent with what packages are installed in the system
# this covers cases when system is installed with selinux-policy-{mls,minimal}
# or selinux-policy-{targeted,mls,minimal} where switched but the machine has not
# been rebooted yet.
# The macro should be called at the beginning of "post" (to make sure load_policy does not fail)
# and in "posttrans" (to make sure that the store is consistent when all package transitions are done)
# Parameter determines the policy type to be set in case of miss-configuration (if backup value is not usable)
# Steps:
# * load values from config and its backup
# * check whether SELINUXTYPE from backup is usable and make sure that it's set in the config if so
# * use "targeted" if it's being installed and BACKUP_SELINUXTYPE cannot be used
# * check whether SELINUXTYPE in the config is usable and change it to newly installed policy if it isn't
%define checkConfigConsistency() \
if [ -f %{_sysconfdir}/selinux/.config_backup ]; then \
    . %{_sysconfdir}/selinux/.config_backup; \
else \
    BACKUP_SELINUXTYPE=targeted; \
fi; \
if [ -s %{_sysconfdir}/selinux/config ]; then \
    . %{_sysconfdir}/selinux/config; \
    if ls %{_sysconfdir}/selinux/$BACKUP_SELINUXTYPE/policy/policy.* &>/dev/null; then \
        if [ "$BACKUP_SELINUXTYPE" != "$SELINUXTYPE" ]; then \
            sed -i 's/^SELINUXTYPE=.*/SELINUXTYPE='"$BACKUP_SELINUXTYPE"'/g' %{_sysconfdir}/selinux/config; \
        fi; \
    elif [ "%1" = "targeted" ]; then \
        if [ "%1" != "$SELINUXTYPE" ]; then \
            sed -i 's/^SELINUXTYPE=.*/SELINUXTYPE=%1/g' %{_sysconfdir}/selinux/config; \
        fi; \
    elif ! ls  %{_sysconfdir}/selinux/$SELINUXTYPE/policy/policy.* &>/dev/null; then \
        if [ "%1" != "$SELINUXTYPE" ]; then \
            sed -i 's/^SELINUXTYPE=.*/SELINUXTYPE=%1/g' %{_sysconfdir}/selinux/config; \
        fi; \
    fi; \
fi;

# Create hidden backup of /etc/selinux/config and prepend BACKUP_ to names
# of variables inside so that they are easy to use later
# This should be done in "pretrans" because config content can change during RPM operations
# The macro has to be used in a script slot with "-p <lua>"
%define backupConfigLua() \
local sysconfdir = rpm.expand("%{_sysconfdir}") \
local config_file = sysconfdir .. "/selinux/config" \
local config_backup = sysconfdir .. "/selinux/.config_backup" \
os.remove(config_backup) \
if posix.stat(config_file) then \
    local f = assert(io.open(config_file, "r"), "Failed to read " .. config_file) \
    local content = f:read("*all") \
    f:close() \
    local backup = content:gsub("SELINUX", "BACKUP_SELINUX") \
    local bf = assert(io.open(config_backup, "w"), "Failed to open " .. config_backup) \
    bf:write(backup) \
    bf:close() \
end

# Remove the local_varrun SELinux module
%define removeVarrunModuleLua() \
if posix.access ("%{_sharedstatedir}/selinux/%1/active/modules/400/extra_varrun/cil", "r") then \
  os.execute ("%{_bindir}/rm -rf %{_sharedstatedir}/selinux/%1/active/modules/400/extra_varrun") \
end

%build

%prep
%autosetup -p 1 -n %{name}-%{commit}
tar -C policy/modules/contrib -xf %{SOURCE4}

%install
# Build targeted policy
%{__rm} -fR %{buildroot}
mkdir -p %{buildroot}%{_sysconfdir}/selinux
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
touch %{buildroot}%{_sysconfdir}/selinux/config
touch %{buildroot}%{_sysconfdir}/sysconfig/selinux
mkdir -p %{buildroot}%{_usr}/lib/tmpfiles.d/
install -p -m0644 %{SOURCE2} %{buildroot}%{_usr}/lib/tmpfiles.d/
mkdir -p %{buildroot}%{_bindir}
install -p -m 755 %{SOURCE3} %{buildroot}%{_bindir}/
mkdir -p %{buildroot}%{_libexecdir}/selinux
install -p -m 755  %{SOURCE37} %{buildroot}%{_libexecdir}/selinux

# Always create policy module package directories
mkdir -p %{buildroot}%{_datadir}/selinux/{targeted,mls,minimum,modules}/
mkdir -p %{buildroot}%{_sharedstatedir}/selinux/{targeted,mls,minimum,modules}/

mkdir -p %{buildroot}%{_datadir}/selinux/packages

mkdir -p %{buildroot}%{_sysconfdir}/dnf/protected.d/

# Install devel
make clean
%if %{with targeted}
# Build targeted policy
%makeCmds targeted mcs allow
%makeModulesConf targeted
%installCmds targeted mcs allow
# install permissivedomains.cil
%{_sbindir}/semodule -p %{buildroot} -X 100 -s targeted -i \
    ./dist/permissivedomains.cil
# recreate sandbox.pp
rm -rf %{buildroot}%{_sharedstatedir}/selinux/targeted/active/modules/100/sandbox
%make_build %common_params UNK_PERMS=allow NAME=targeted TYPE=mcs sandbox.pp
mv sandbox.pp %{buildroot}%{_datadir}/selinux/packages/sandbox.pp
%modulesList targeted
%nonBaseModulesList targeted
install -p -m 644 %{SOURCE38} %{buildroot}%{_sysconfdir}/dnf/protected.d/
%endif

%if %{with minimum}
# Build minimum policy
%makeCmds minimum mcs allow
%makeModulesConf targeted
%installCmds minimum mcs allow
rm -rf %{buildroot}%{_sharedstatedir}/selinux/minimum/active/modules/100/sandbox
install -p -m 644 %{SOURCE16} %{buildroot}%{_datadir}/selinux/minimum/modules-enabled.lst
%modulesList minimum
%nonBaseModulesList minimum
%endif

%if %{with mls}
# Build mls policy
%makeCmds mls mls deny
%makeModulesConf mls
%installCmds mls mls deny
%modulesList mls
%nonBaseModulesList mls
install -p -m 644 %{SOURCE39} %{buildroot}%{_sysconfdir}/dnf/protected.d/
%endif

# remove leftovers when save-previous=true (semanage.conf) is used
rm -rf %{buildroot}%{_sharedstatedir}/selinux/{minimum,targeted,mls}/previous

make %common_params UNK_PERMS=allow NAME=targeted TYPE=mcs DESTDIR=%{buildroot} PKGNAME=%{name} install-docs
make %common_params UNK_PERMS=allow NAME=targeted TYPE=mcs DESTDIR=%{buildroot} PKGNAME=%{name} install-headers
mkdir %{buildroot}%{_datadir}/selinux/devel/
mv %{buildroot}%{_datadir}/selinux/targeted/include %{buildroot}%{_datadir}/selinux/devel/include
install -p -m 644 %{SOURCE1} %{buildroot}%{_datadir}/selinux/devel/Makefile
install -p -m 644 doc/example.* %{buildroot}%{_datadir}/selinux/devel/
install -p -m 644 doc/policy.* %{buildroot}%{_datadir}/selinux/devel/
%{_bindir}/sepolicy manpage -a -p %{buildroot}%{_mandir}/man8/ -w -r %{buildroot}
mkdir %{buildroot}%{_datadir}/selinux/devel/html
mv %{buildroot}%{_datadir}/man/man8/*.html %{buildroot}%{_datadir}/selinux/devel/html
mv %{buildroot}%{_datadir}/man/man8/style.css %{buildroot}%{_datadir}/selinux/devel/html

mkdir -p %{buildroot}%{_rpmconfigdir}/macros.d
install -p -m 644 %{SOURCE5} %{buildroot}%{_rpmconfigdir}/macros.d/macros.selinux-policy
sed -i 's/SELINUXPOLICYVERSION/%{version}/' %{buildroot}%{_rpmconfigdir}/macros.d/macros.selinux-policy
sed -i 's@SELINUXSTOREPATH@%{_sharedstatedir}/selinux@' %{buildroot}%{_rpmconfigdir}/macros.d/macros.selinux-policy

mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE36} %{buildroot}%{_unitdir}

%post
%systemd_post selinux-check-proper-disable.service
if [ ! -s %{_sysconfdir}/selinux/config ]; then
#
#     New install so we will default to targeted policy
#
echo "
# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
# See also:
# https://docs.fedoraproject.org/en-US/quick-docs/getting-started-with-selinux/#getting-started-with-selinux-selinux-states-and-modes
#
# NOTE: In earlier Fedora kernel builds, SELINUX=disabled would also
# fully disable SELinux during boot. If you need a system with SELinux
# fully disabled instead of SELinux running with no policy loaded, you
# need to pass selinux=0 to the kernel command line. You can use grubby
# to persistently set the bootloader to boot with selinux=0:
#
#    grubby --update-kernel ALL --args selinux=0
#
# To revert back to SELinux enabled:
#
#    grubby --update-kernel ALL --remove-args selinux
#
SELINUX=enforcing
# SELINUXTYPE= can take one of these three values:
#     targeted - Targeted processes are protected,
#     minimum - Modification of targeted policy. Only selected processes are protected.
#     mls - Multi Level Security protection.
SELINUXTYPE=targeted

" > %{_sysconfdir}/selinux/config

     ln -sf ../selinux/config %{_sysconfdir}/sysconfig/selinux
     %{_sbindir}/restorecon %{_sysconfdir}/selinux/config 2> /dev/null || :
else
     . %{_sysconfdir}/selinux/config
fi
exit 0

%preun
%systemd_preun selinux-check-proper-disable.service

%postun
%systemd_postun selinux-check-proper-disable.service
if [ $1 = 0 ]; then
     %{_sbindir}/setenforce 0 2> /dev/null
     if [ ! -s %{_sysconfdir}/selinux/config ]; then
          echo "SELINUX=disabled" > %{_sysconfdir}/selinux/config
     else
          sed -i 's/^SELINUX=.*/SELINUX=disabled/g' %{_sysconfdir}/selinux/config
     fi
fi
exit 0

%if %{with targeted}
%package targeted
Summary: SELinux targeted policy
Provides: selinux-policy-any = %{version}-%{release}
Obsoletes: selinux-policy-targeted-sources < 2
Requires(pre): policycoreutils >= %{POLICYCOREUTILSVER}
Requires(pre): coreutils
Requires(pre): selinux-policy = %{version}-%{release}
Requires: selinux-policy = %{version}-%{release}
Conflicts:  audispd-plugins <= 1.7.7-1
Obsoletes: mod_fcgid-selinux <= %{version}-%{release}
Obsoletes: cachefilesd-selinux <= 0.10-1
Conflicts:  seedit
Conflicts:  389-ds-base < 1.2.7, 389-admin < 1.1.12
Conflicts: container-selinux < 2:1.12.1-22
Recommends: (selinux-policy-epel-targeted if epel-release)

%description targeted
SELinux targeted policy package.

%pretrans targeted -p <lua>
%backupConfigLua
%removeVarrunModuleLua targeted

%pre targeted
%preInstall targeted

%post targeted
%checkConfigConsistency targeted
exit 0

%posttrans targeted
%checkConfigConsistency targeted
%{_libexecdir}/selinux/varrun-convert.sh targeted
%postInstall $1 targeted
%{_sbindir}/restorecon -Ri /usr/lib/sysimage/rpm /var/lib/rpm /etc/mdevctl.d

%postun targeted
if [ $1 = 0 ]; then
    if [ -s %{_sysconfdir}/selinux/config ]; then
        source %{_sysconfdir}/selinux/config &> /dev/null || true
    fi
    if [ "$SELINUXTYPE" = "targeted" ]; then
        %{_sbindir}/setenforce 0 2> /dev/null
        if [ ! -s %{_sysconfdir}/selinux/config ]; then
            echo "SELINUX=disabled" > %{_sysconfdir}/selinux/config
        else
            sed -i 's/^SELINUX=.*/SELINUX=disabled/g' %{_sysconfdir}/selinux/config
        fi
    fi
fi
exit 0


%triggerin -- pcre2
%{_sbindir}/selinuxenabled && %{_sbindir}/semodule -nB 2> /dev/null
exit 0

%triggerprein -p <lua> -- container-selinux
%removeVarrunModuleLua targeted

%triggerprein -p <lua> -- pcp-selinux
%removeVarrunModuleLua targeted

%triggerpostun -- pcp-selinux
%{_libexecdir}/selinux/varrun-convert.sh targeted
exit 0

%triggerpostun -- container-selinux
%{_libexecdir}/selinux/varrun-convert.sh targeted
exit 0

%files targeted -f %{buildroot}%{_datadir}/selinux/targeted/nonbasemodules.lst
%config(noreplace) %{_sysconfdir}/dnf/protected.d/selinux-policy-targeted.conf
%config(noreplace) %{_sysconfdir}/selinux/targeted/contexts/users/unconfined_u
%config(noreplace) %{_sysconfdir}/selinux/targeted/contexts/users/sysadm_u
%fileList targeted
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/targeted/active/modules/100/permissivedomains
%endif

%if %{with minimum}
%package minimum
Summary: SELinux minimum policy
Provides: selinux-policy-any = %{version}-%{release}
Requires(post): policycoreutils-python-utils >= %{POLICYCOREUTILSVER}
Requires(pre): coreutils
Requires(pre): selinux-policy = %{version}-%{release}
Requires: selinux-policy = %{version}-%{release}
Conflicts:  seedit
Conflicts: container-selinux <= 1.9.0-9

%description minimum
SELinux minimum policy package.

%pretrans minimum -p <lua>
%backupConfigLua

%pre minimum
%preInstall minimum
if [ $1 -ne 1 ]; then
    %{_sbindir}/semodule -s minimum --list-modules=full | awk '{ if ($4 != "disabled") print $2; }' > %{_datadir}/selinux/minimum/instmodules.lst
fi

%post minimum
%checkConfigConsistency minimum
modules=`cat %{_datadir}/selinux/minimum/modules.lst`
basemodules=`cat %{_datadir}/selinux/minimum/base.lst`
enabledmodules=`cat %{_datadir}/selinux/minimum/modules-enabled.lst`
if [ ! -d %{_sharedstatedir}/selinux/minimum/active/modules/disabled ]; then
    mkdir %{_sharedstatedir}/selinux/minimum/active/modules/disabled
fi
if [ $1 -eq 1 ]; then
for p in $modules; do
    touch %{_sharedstatedir}/selinux/minimum/active/modules/disabled/$p
done
for p in $basemodules $enabledmodules; do
    rm -f %{_sharedstatedir}/selinux/minimum/active/modules/disabled/$p
done
%{_sbindir}/semanage import -S minimum -f - << __eof
login -m  -s unconfined_u -r s0-s0:c0.c1023 __default__
login -m  -s unconfined_u -r s0-s0:c0.c1023 root
__eof
%{_sbindir}/restorecon -R /root /var/log /var/run 2> /dev/null
%{_sbindir}/semodule -B -s minimum 2> /dev/null
else
instpackages=`cat %{_datadir}/selinux/minimum/instmodules.lst`
for p in $packages; do
    touch %{_sharedstatedir}/selinux/minimum/active/modules/disabled/$p
done
for p in $instpackages apache dbus inetd kerberos mta nis; do
    rm -f %{_sharedstatedir}/selinux/minimum/active/modules/disabled/$p
done
%{_sbindir}/semodule -B -s minimum 2> /dev/null
%relabel minimum
fi
exit 0

%posttrans minimum
%checkConfigConsistency minimum
%{_libexecdir}/selinux/varrun-convert.sh minimum
%{_sbindir}/restorecon -Ri /usr/lib/sysimage/rpm /var/lib/rpm

%postun minimum
if [ $1 = 0 ]; then
    if [ -s %{_sysconfdir}/selinux/config ]; then
        source %{_sysconfdir}/selinux/config &> /dev/null || true
    fi
    if [ "$SELINUXTYPE" = "minimum" ]; then
        %{_sbindir}/setenforce 0 2> /dev/null
        if [ ! -s %{_sysconfdir}/selinux/config ]; then
            echo "SELINUX=disabled" > %{_sysconfdir}/selinux/config
        else
            sed -i 's/^SELINUX=.*/SELINUX=disabled/g' %{_sysconfdir}/selinux/config
        fi
    fi
fi
exit 0

%files minimum -f %{buildroot}%{_datadir}/selinux/minimum/nonbasemodules.lst
%config(noreplace) %{_sysconfdir}/selinux/minimum/contexts/users/unconfined_u
%config(noreplace) %{_sysconfdir}/selinux/minimum/contexts/users/sysadm_u
%fileList minimum
%{_datadir}/selinux/minimum/modules-enabled.lst
%endif

%if %{with mls}
%package mls
Summary: SELinux MLS policy
Provides: selinux-policy-any = %{version}-%{release}
Obsoletes: selinux-policy-mls-sources < 2
Requires: policycoreutils-newrole >= %{POLICYCOREUTILSVER} setransd
Requires(pre): policycoreutils >= %{POLICYCOREUTILSVER}
Requires(pre): coreutils
Requires(pre): selinux-policy = %{version}-%{release}
Requires: selinux-policy = %{version}-%{release}
Conflicts:  seedit
Conflicts: container-selinux <= 1.9.0-9

%description mls
SELinux MLS (Multi Level Security) policy package.

%pretrans mls -p <lua>
%backupConfigLua

%pre mls
%preInstall mls

%post mls
%checkConfigConsistency mls
exit 0

%posttrans mls
%checkConfigConsistency mls
%{_libexecdir}/selinux/varrun-convert.sh mls
%postInstall $1 mls
%{_sbindir}/restorecon -Ri /usr/lib/sysimage/rpm /var/lib/rpm

%postun mls
if [ $1 = 0 ]; then
    if [ -s %{_sysconfdir}/selinux/config ]; then
        source %{_sysconfdir}/selinux/config &> /dev/null || true
    fi
    if [ "$SELINUXTYPE" = "mls" ]; then
        %{_sbindir}/setenforce 0 2> /dev/null
        if [ ! -s %{_sysconfdir}/selinux/config ]; then
            echo "SELINUX=disabled" > %{_sysconfdir}/selinux/config
        else
            sed -i 's/^SELINUX=.*/SELINUX=disabled/g' %{_sysconfdir}/selinux/config
        fi
    fi
fi
exit 0

%files mls -f %{buildroot}%{_datadir}/selinux/mls/nonbasemodules.lst
%config(noreplace) %{_sysconfdir}/dnf/protected.d/selinux-policy-mls.conf
%config(noreplace) %{_sysconfdir}/selinux/mls/contexts/users/unconfined_u
%fileList mls
%endif

%changelog
## START: Generated by rpmautospec
* Mon Feb 17 2025 Zdenek Pytela <zpytela@redhat.com> - 40.13.26-1
- Rename winbind_rpcd_* types to samba_dcerpcd_*
Resolves: RHEL-14759
- Allow samba-dcerpcd work with ctdb cluster
Resolves: RHEL-14759
- Revert "Remove socket from unconfined_domain_type allow rule"
Resolves: RHEL-77327
- Dontaudit access of virt-related permissive domains
Resolves: RHEL-77808
- Add selinux_requires_min macro
Resolves: RHEL-54715
- Filter out EPEL related modules
Resolves: RHEL-73505

* Thu Feb 06 2025 Zdenek Pytela <zpytela@redhat.com> - 40.13.25-1
- Update ktlshd policy to read /proc/keys and domain keyrings
Resolves: RHEL-42672
- Allow pcmsensor read nmi_watchdog state information
Resolves: RHEL-52838
- Support peer-to-peer migration of vms using ssh
Resolves: RHEL-77351
- Allow virt_domain read hardware state information unconditionally
Resolves: RHEL-71270
- Allow timemaster write to sysfs files
Resolves: RHEL-44637
- Allow virtqemud map svirt_image_t plain files
Resolves: RHEL-40080
- Allow virtqemud unmount a filesystem with extended attributes
Resolves: RHEL-40080
- Allow virtqemud work with nvdimm devices
Resolves: RHEL-71656
- Update virtqemud policy regarding the svirt_tcg_t domain
Resolves: RHEL-71270
- Allow virtqemud use hostdev usb devices conditionally
Resolves: RHEL-74230
- Support saving and restoring a VM to/from a block device
Resolves: RHEL-76138
- Allow virtnwfilterd dbus chat with firewalld
Resolves: RHEL-76138
- Allow virt_domain to use pulseaudio - conditional
Resolves: RHEL-62763
- Allow virtstoraged write to sysfs files
Resolves: RHEL-44637
- Allow irqbalance to run unconfined scripts conditionally
Resolves: RHEL-54019
- Allow rhsmcertd notify virt-who
Resolves: RHEL-77114
- Allow init mounton crypto sysctl files
Resolves: RHEL-56250

* Mon Jan 27 2025 Zdenek Pytela <zpytela@redhat.com> - 40.13.24-1
- Allow systemd-generator connect to syslog over a unix datagram socket
Resolves: RHEL-75879
- Allow ssh_t to change role to system_r
Resolves: RHEL-53972
- Allow virtnodedev create /etc/mdevctl.d/scripts.d with bin_t type
Resolves: RHEL-39893
- Allow virtqemud manage fixed disk device nodes
Resolves: RHEL-71656
- Allow samba-bgqd connect to cupsd over an unix domain stream socket
Resolves: RHEL-72861
- Allow systemd-machined read the vsock device
Resolves: RHEL-74280
- Allow pcmsensor write nmi_watchdog state information
Resolves: RHEL-52838
- Label /proc/sys/kernel/nmi_watchdog with sysctl_nmi_watchdog_t
Resolves: RHEL-52838

* Fri Jan 24 2025 Zdenek Pytela <zpytela@redhat.com> - 40.13.23-2
- Rebuild other packages with with selinux-policy-40.13.23
Resolves: RHEL-36741

* Thu Jan 23 2025 Zdenek Pytela <zpytela@redhat.com> - 40.13.23-1
- Remove the lockdown class from the policy
Resolves: RHEL-36741
- Remove socket from unconfined_domain_type allow rule
Resolves: RHEL-36741
- Include key_socket in socket_class_set
Resolves: RHEL-36741

* Thu Jan 16 2025 Zdenek Pytela <zpytela@redhat.com> - 40.13.22-1
- Allow staff user dbus chat with virt-dbus
Resolves: RHEL-73914
- Allow virtqemud domain transition to nbdkit
Resolves: RHEL-69118
- Add nbdkit interfaces defined conditionally
Resolves: RHEL-69118
- Allow svirt_t read sysfs files
Resolves: RHEL-71270
- Label /dev/pmem[0-9]+ with fixed_disk_device_t
Resolves: RHEL-71656
- Add support for the KVM guest memfd anon inodes
Resolves: RHEL-69128
- Allow sysadm user dbus chat with virt-dbus
Resolves: RHEL-73914
- Allow initrc_t transition to passwd_t
Resolves: RHEL-71665
- Allow unconfined_service_t transition to passwd_t
Resolves: RHEL-71665

* Wed Jan 08 2025 Zdenek Pytela <zpytela@redhat.com> - 40.13.21-1
- Allow init create vsock socket for sshd
Resolves: RHEL-72549
- Support ssh connections via systemd-ssh-generator
Resolves: RHEL-72549
- Allow ssh generator work with systemd unit files
Resolves: RHEL-72549
- Confine systemd system-ssh-generator
Resolves: RHEL-72549
- Allow login_userdomain getattr nsfs files
Resolves: RHEL-72549
- Allow virtqemud send a generic signal to the ssh client domain
Resolves: RHEL-53972
- Add the auth_dontaudit_read_passwd_file() interface
Resolves: RHEL-71490
- Dontaudit request-key read /etc/passwd
Resolves: RHEL-71490

* Fri Jan 03 2025 Zdenek Pytela <zpytela@redhat.com> - 40.13.20-1
- Allow virtqemud domain transition on numad execution
Resolves: RHEL-65789
- Support virt live migration using ssh
Resolves: RHEL-53972
- Allow ssh_t read systemd config files
Resolves: RHEL-53972
- Allow virtqemud permissions needed for live migration
Resolves: RHEL-43217
- Allow virtqemud the getpgid process permission
Resolves: RHEL-46357
- Allow virtqemud manage nfs dirs when virt_use_nfs boolean is on
Resolves: RHEL-71068
- Allow virtqemud relabelfrom virt_log_t files
Resolves: RHEL-48236
- Allow virtqemud relabel tun_socket
Resolves: RHEL-71394
- Allow gnome-remote-desktop dbus chat with policykit
Resolves: RHEL-35877
- Update ktlsh policy
Resolves: RHEL-42672
- Confine the ktls service
Resolves: RHEL-42672
- Allow request-key to read /etc/passwd
Resolves: RHEL-71490
- Allow request-key to manage all domains' keys
Resolves: RHEL-71490

* Fri Dec 20 2024 Petr Lautrbach <lautrbach@redhat.com> - 40.13.19-2
- Rebuild with SELinux Userspace 3.8

* Wed Dec 18 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.19-1
- Allow systemd-journald getattr nsfs files
Resolves: RHEL-71803
- Allow systemd-related domains getattr nsfs files
Resolves: RHEL-71803

* Fri Dec 13 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.18-1
- Sync dist/targeted/modules.conf with Fedora 42
Resolves: RHEL-70850
- Add support for sap
Resolves: RHEL-70850
- Allow sssd_selinux_manager_t the setcap process permission
Resolves: RHEL-70822
- Allow virtqemud open svirt_devpts_t char files
Resolves: RHEL-43446
- Fix the cups_read_pid_files() interface to use read_files_pattern
Resolves: RHEL-69512

* Thu Dec 12 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.17-1
- Update samba-bgqd policy
Resolves: RHEL-69512
- Allow samba-bgqd read cups config files
Resolves: RHEL-69512
- Allow virtqemud additional permissions for tmpfs_t blk devices
Resolves: RHEL-61235
- Allow virtqemud rw access to svirt_image_t chr files
Resolves: RHEL-61235
- Allow virtqemud rw and setattr access to fixed block devices
Resolves: RHEL-61235
- Label /etc/mdevctl.d/scripts.d with bin_t
Resolves: RHEL-39893
- Fix the /etc/mdevctl\.d(/.*)? regexp
Resolves: RHEL-39893
- Allow virtnodedev watch mdevctl config dirs
Resolves: RHEL-39893
- Make mdevctl_conf_t member of the file_type attribute
Resolves: RHEL-39893
- Label /etc/mdevctl.d with mdevctl_conf_t
Resolves: RHEL-39893
- Allow virtqemud relabelfrom virt_log_t files
Resolves: RHEL-48236
- Allow virtqemud_t relabel virtqemud_var_run_t sock_files
Resolves: RHEL-48236
- Allow virtqemud relabelfrom virtqemud_var_run_t dirs
Resolves: RHEL-48236
- Allow svirt_tcg_t read virtqemud_t fifo_files
Resolves: RHEL-48236
- Allow virtqemud rw and setattr access to sev devices
Resolves: RHEL-69128
- Allow virtqemud directly read and write to a fixed disk
Resolves: RHEL-61235
- Allow svirt_t the sys_rawio capability
Resolves: RHEL-61235
- Allow svirt_t the sys_rawio capability
Resolves: RHEL-61235
- Allow virtqemud connect to sanlock over a unix stream socket
Resolves: RHEL-44352
- allow gdm and iiosensorproxy talk to each other via D-bus
Resolves: RHEL-70850
- Allow sendmail to map mail server configuration files
Related: RHEL-54014
- Allow procmail to read mail aliases
Resolves: RHEL-54014
- Grant rhsmcertd chown capability & userdb access
Resolves: RHEL-68481

* Fri Nov 29 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.16-1
- Fix the file type for /run/systemd/generator
Resolves: RHEL-68313

* Thu Nov 28 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.15-1
- Allow qatlib search the content of the kernel debugging filesystem
Resolves: RHEL-66334
- Allow qatlib connect to systemd-machined over a unix socket
Resolves: RHEL-66334
- Update policy for samba-bgqd
Resolves: RHEL-64908
- Allow httpd get attributes of dirsrv unit files
Resolves: RHEL-62706
- Allow virtstoraged read vm sysctls
Resolves: RHEL-61742
- Allow virtstoraged execute mount programs in the mount domain
Resolves: RHEL-61742
- Update policy for rpc-virtstorage
Resolves: RHEL-61742
- Allow virtstoraged get attributes of configfs dirs
Resolves: RHEL-61742
- Allow virt_driver_domain read virtd-lxc files in /proc
Resolves: RHEL-61742
- Allow virtstoraged manage files with virt_content_t type
Resolves: RHEL-61742
- Allow virtstoraged use the io_uring API
Resolves: RHEL-61742
- Allow virtstoraged execute lvm programs in the lvm domain
Resolves: RHEL-61742
- Allow svirt_t connect to unconfined_t over a unix domain socket
Resolves: RHEL-61246
- Label /usr/lib/node_modules_22/npm/bin with bin_t
Resolves: RHEL-56350
- Allow bacula execute container in the container domain
Resolves: RHEL-39529
- Label /run/systemd/generator with systemd_unit_file_t
Resolves: RHEL-68313

* Tue Nov 19 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.14-1
- mls/modules.conf - fix typo
- Use dist/targeted/modules.conf in build workflow
- Fix default and dist config files
- CI: update to actions/checkout@v4
- Clean up and sync securetty_types
- Bring config files from dist-git into the source repo
- Sync users with Fedora targeted users

* Tue Nov 12 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.13-1
- Revert "Allow unconfined_t execute kmod in the kmod domain"
Resolves: RHEL-65190
- Add policy for /usr/libexec/samba/samba-bgqd
Resolves: RHEL-64908
- Label samba certificates with samba_cert_t
Resolves: RHEL-64908
- Label /usr/bin/samba-gpupdate with samba_gpupdate_exec_t
Resolves: RHEL-64908
- Allow rpcd read network sysctls
Resolves: RHEL-64737
- Label all semanage store files in /etc as semanage_store_t
Resolves: RHEL-65864

* Tue Oct 29 2024 Troy Dawson <tdawson@redhat.com> - 40.13.12-2
- Bump release for October 2024 mass rebuild:
  Resolves: RHEL-64018

* Thu Oct 24 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.12-1
- Dontaudit subscription manager setfscreate and read file contexts
Resolves: RHEL-58009
- Allow the sysadm user use the secretmem API
Resolves: RHEL-40953
- Allow sudodomain list files in /var
Resolves: RHEL-58068
- Allow gnome-remote-desktop watch /etc directory
Resolves: RHEL-35877
- Allow journalctl connect to systemd-userdbd over a unix socket
Resolves: RHEL-58072
- systemd: allow sys_admin capability for systemd_notify_t
Resolves: RHEL-58072
- Allow some confined users send to lldpad over a unix dgram socket
Resolves: RHEL-61634
- Allow lldpad send to sysadm_t over a unix dgram socket
Resolves: RHEL-61634
- Allow lldpd connect to systemd-machined over a unix socket
Resolves: RHEL-61634

* Wed Oct 23 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.11-1
- Allow ping_t read network sysctls
Resolves: RHEL-54299
- Label /usr/lib/node_modules/npm/bin with bin_t
Resolves: RHEL-56350
- Label /run/sssd with sssd_var_run_t
Resolves: RHEL-57065
- Allow virtqemud read virtd_t files
Resolves: RHEL-57713
- Allow wdmd read hardware state information
Resolves: RHEL-57982
- Allow wdmd list the contents of the sysfs directories
Resolves: RHEL-57982
- Label /etc/sysctl.d and /run/sysctl.d with system_conf_t
Resolves: RHEL-58380
- Allow dirsrv read network sysctls
Resolves: RHEL-58381
- Allow lldpad create and use netlink_generic_socket
Resolves: RHEL-61634
- Allow unconfined_t execute kmod in the kmod domain
Resolves: RHEL-61755
- Confine the pcm service
Resolves: RHEL-52838
- Allow iio-sensor-proxy the bpf capability
Resolves: RHEL-62355
- Confine iio-sensor-proxy
Resolves: RHEL-62355

* Wed Oct 16 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.10-1
- Confine gnome-remote-desktop
Resolves: RHEL-35877
- Allow virtqemud get attributes of a tmpfs filesystem
Resolves: RHEL-40855
- Allow virtqemud get attributes of cifs files
Resolves: RHEL-40855
- Allow virtqemud get attributes of filesystems with extended attributes
Resolves: RHEL-39668
- Allow virtqemud get attributes of NFS filesystems
Resolves: RHEL-40855
- Add support for secretmem anon inode
Resolves: RHEL-40953
- Allow systemd-sleep read raw disk data
Resolves: RHEL-49600
- Allow systemd-hwdb send messages to kernel unix datagram sockets
Resolves: RHEL-50810
- Label /run/modprobe.d with modules_conf_t
Resolves: RHEL-54591
- Allow setsebool_t relabel selinux data files
Resolves: RHEL-55412
- Don't audit crontab_domain write attempts to user home
Resolves: RHEL-56349
- Differentiate between staff and sysadm when executing crontab with sudo
Resolves: RHEL-56349
- Add crontab_admin_domtrans interface
Resolves: RHEL-56349
- Add crontab_domtrans interface
Resolves: RHEL-56349
- Allow boothd connect to kernel over a unix socket
Resolves: RHEL-58060
- Fix label of pseudoterminals created from sudodomain
Resolves: RHEL-58068
- systemd: allow systemd_notify_t to send data to kernel_t datagram sockets
Resolves: RHEL-58072
- Allow rsyslog read systemd-logind session files
Resolves: RHEL-40961
- Label /dev/mmcblk0rpmb character device with removable_device_t
Resolves: RHEL-55265
- Label /dev/hfi1_[0-9]+ devices
Resolves: RHEL-62836
- Label /dev/papr-sysparm and /dev/papr-vpd
Resolves: RHEL-56908
- Support SGX devices
Resolves: RHEL-62354
- Suppress semodule's stderr
Resolves: RHEL-59192

* Mon Aug 26 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.9-1
- Allow virtqemud relabelfrom also for file and sock_file
Resolves: RHEL-49763
- Allow virtqemud relabel user tmp files and socket files
Resolves: RHEL-49763
- Update virtqemud policy for libguestfs usage
Resolves: RHEL-49763
- Label /run/libvirt/qemu/channel with virtqemud_var_run_t
Resolves: RHEL-47274

* Tue Aug 13 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.8-1
- Add virt_create_log() and virt_write_log() interfaces
Resolves: RHEL-47274
- Update libvirt policy
Resolves: RHEL-45464
Resolves: RHEL-49763
- Allow svirt_tcg_t map svirt_image_t files
Resolves: RHEL-47274
- Allow svirt_tcg_t read vm sysctls
Resolves: RHEL-47274
- Additional updates stalld policy for bpf usage
Resolves: RHEL-50356

* Thu Aug 08 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.7-1
- Add the swtpm.if interface file for interactions with other domains
Resolves: RHEL-47274
- Allow virtproxyd create and use its private tmp files
Resolves: RHEL-40499
- Allow virtproxyd read network state
Resolves: RHEL-40499
- Allow virtqemud domain transition on swtpm execution
Resolves: RHEL-47274
Resolves: RHEL-49763
- Allow virtqemud relabel virt_var_run_t directories
Resolves: RHEL-47274
Resolves: RHEL-45464
Resolves: RHEL-49763
- Allow virtqemud domain transition on passt execution
Resolves: RHEL-45464
- Allow virt_driver_domain create and use log files in /var/log
Resolves: RHEL-40239
- Allow virt_driver_domain connect to systemd-userdbd over a unix socket
Resolves: RHEL-44932
Resolves: RHEL-44898
- Update stalld policy for bpf usage
Resolves: RHEL-50356
- Allow boothd connect to systemd-userdbd over a unix socket
Resolves: RHEL-45907
- Allow linuxptp configure phc2sys and chronyd over a unix domain socket
Resolves: RHEL-46011
- Allow systemd-machined manage runtime sockets
Resolves: RHEL-49567
- Allow ip command write to ipsec's logs
Resolves: RHEL-41222
- Allow init_t nnp domain transition to firewalld_t
Resolves: RHEL-52481
- Update qatlib policy for v24.02 with new features
Resolves: RHEL-50377
- Allow postfix_domain map postfix_etc_t files
Resolves: RHEL-46327

* Thu Jul 25 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.6-1
- Allow virtnodedevd run udev with a domain transition
Resolves: RHEL-39890
- Allow virtnodedev_t create and use virtnodedev_lock_t
Resolves: RHEL-39890
- Allow svirt attach_queue to a virtqemud tun_socket
Resolves: RHEL-44312
- Label /run/systemd/machine with systemd_machined_var_run_t
Resolves: RHEL-49567
- Allow to create and delete socket files created by rhsm.service

* Tue Jul 16 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.5-1
- Allow to create and delete socket files created by rhsm.service
Resolves: RHEL-40857
- Allow svirt read virtqemud fifo files
Resolves: RHEL-40350
- Allow virt_dbus_t connect to virtqemud_t over a unix stream socket
Resolves: RHEL-37822
- Allow virtqemud read virt-dbus process state
Resolves: RHEL-37822
- Allow virtqemud run ssh client with a transition
Resolves: RHEL-43215
- Allow virtnetworkd exec shell when virt_hooks_unconfined is on
Resolves: RHEL-41168
- Allow NetworkManager the sys_ptrace capability in user namespace
Resolves: RHEL-46717
- Update keyutils policy
Resolves: RHEL-38920
- Allow ip the setexec permission
Resolves: RHEL-41182

* Fri Jun 28 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.4-1
- Confine libvirt-dbus
Resolves: RHEL-37822
- Allow sssd create and use io_uring
Resolves: RHEL-43448
- Allow virtqemud the kill capability in user namespace
Resolves: RHEL-44996
- Allow login_userdomain execute systemd-tmpfiles in the caller domain
Resolves: RHEL-44191
- Allow virtqemud read vm sysctls
Resolves: RHEL-40938
- Allow svirt_t read vm sysctls
Resolves: RHEL-40938
- Allow rshim get options of the netlink class for KOBJECT_UEVENT family
Resolves: RHEL-40859
- Allow systemd-hostnamed read the vsock device
Resolves: RHEL-45309
- Allow systemd (PID 1) manage systemd conf files
Resolves: RHEL-45304
- Allow journald read systemd config files and directories
Resolves: RHEL-45304
- Allow systemd_domain read systemd_conf_t dirs
Resolves: RHEL-45304
- Label systemd configuration files with systemd_conf_t
Resolves: RHEL-45304
- Allow dhcpcd the kill capability
Resolves: RHEL-43417
- Add support for libvirt hooks
Resolves: RHEL-41168

* Mon Jun 24 2024 Troy Dawson <tdawson@redhat.com> - 40.13.3-2
- Bump release for June 2024 mass rebuild

* Tue Jun 18 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.3-1
- Allow virtqemud manage nfs files when virt_use_nfs boolean is on
Resolves: RHEL-40205
- Allow virt_driver_domain read files labeled unconfined_t
Resolves: RHEL-40262
- Allow virt_driver_domain dbus chat with policykit
Resolves: RHEL-40346
- Escape "interface" as a file name in a virt filetrans pattern
Resolves: RHEL-34769
- Allow setroubleshootd get attributes of all sysctls
Resolves: RHEL-40923
- Allow qemu-ga read vm sysctls
Resolves: RHEL-40829
- Allow sbd to trace processes in user namespace
Resolves: RHEL-39989
- Allow request-key execute scripts
Resolves: RHEL-38920
- Update policy for haproxyd
Resolves: RHEL-40877

* Fri Jun 07 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.2-1
- Allow all domains read and write z90crypt device
Resolves: RHEL-28539
- Allow dhcpc read /run/netns files
Resolves: RHEL-39510
- Allow bootupd search efivarfs dirs
Resolves: RHEL-39514

* Fri May 17 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13.1-1
- Allow logwatch read logind sessions files
Resolves: RHEL-30441
- Allow sulogin relabel tty1
Resolves: RHEL-30440
- Dontaudit sulogin the checkpoint_restore capability
Resolves: RHEL-30440
- Allow postfix smtpd map aliases file
Resolves: RHEL-35544
- Ensure dbus communication is allowed bidirectionally
Resolves: RHEL-35783
- Allow various services read and write z90crypt device
Resolves: RHEL-28539
- Allow dhcpcd use unix_stream_socket
Resolves: RHEL-33081
- Allow xdm_t to watch and watch_reads mount_var_run_t
Resolves: RHEL-36073
- Allow plymouthd log during shutdown
Resolves: RHEL-30455
- Update rpm configuration for the /var/run equivalency change
Resolves: RHEL-36094

* Mon Feb 12 2024 Zdenek Pytela <zpytela@redhat.com> - 40.13-1
- Only allow confined user domains to login locally without unconfined_login
- Add userdom_spec_domtrans_confined_admin_users interface
- Only allow admindomain to execute shell via ssh with ssh_sysadm_login
- Add userdom_spec_domtrans_admin_users interface
- Move ssh dyntrans to unconfined inside unconfined_login tunable policy
- Update ssh_role_template() for user ssh-agent type
- Allow init to inherit system DBus file descriptors
- Allow init to inherit fds from syslogd
- Allow any domain to inherit fds from rpm-ostree
- Update afterburn policy
- Allow init_t nnp domain transition to abrtd_t

* Tue Feb 06 2024 Zdenek Pytela <zpytela@redhat.com> - 40.12-1
- Rename all /var/lock file context entries to /run/lock
- Rename all /var/run file context entries to /run
- Invert the "/var/run = /run" equivalency

* Mon Feb 05 2024 Zdenek Pytela <zpytela@redhat.com> - 40.11-1
- Replace init domtrans rule for confined users to allow exec init
- Update dbus_role_template() to allow user service status
- Allow polkit status all systemd services
- Allow setroubleshootd create and use inherited io_uring
- Allow load_policy read and write generic ptys
- Allow gpg manage rpm cache
- Allow login_userdomain name_bind to howl and xmsg udp ports
- Allow rules for confined users logged in plasma
- Label /dev/iommu with iommu_device_t
- Remove duplicate file context entries in /run
- Dontaudit getty and plymouth the checkpoint_restore capability
- Allow su domains write login records
- Revert "Allow su domains write login records"
- Allow login_userdomain delete session dbusd tmp socket files
- Allow unix dgram sendto between exim processes
- Allow su domains write login records
- Allow smbd_t to watch user_home_dir_t if samba_enable_home_dirs is on

* Wed Jan 24 2024 Zdenek Pytela <zpytela@redhat.com> - 40.10-1
- Allow chronyd-restricted read chronyd key files
- Allow conntrackd_t to use bpf capability2
- Allow systemd-networkd manage its runtime socket files
- Allow init_t nnp domain transition to colord_t
- Allow polkit status systemd services
- nova: Fix duplicate declarations
- Allow httpd work with PrivateTmp
- Add interfaces for watching and reading ifconfig_var_run_t
- Allow collectd read raw fixed disk device
- Allow collectd read udev pid files
- Set correct label on /etc/pki/pki-tomcat/kra
- Allow systemd domains watch system dbus pid socket files
- Allow certmonger read network sysctls
- Allow mdadm list stratisd data directories
- Allow syslog to run unconfined scripts conditionally
- Allow syslogd_t nnp_transition to syslogd_unconfined_script_t
- Allow qatlib set attributes of vfio device files

* Tue Jan 09 2024 Zdenek Pytela <zpytela@redhat.com> - 40.9-1
- Allow systemd-sleep set attributes of efivarfs files
- Allow samba-dcerpcd read public files
- Allow spamd_update_t the sys_ptrace capability in user namespace
- Allow bluetooth devices work with alsa
- Allow alsa get attributes filesystems with extended attributes

* Tue Jan 02 2024 Yaakov Selkowitz <yselkowi@redhat.com> - 40.8-2
- Limit %%selinux_requires to version, not release

* Thu Dec 21 2023 Zdenek Pytela <zpytela@redhat.com> - 40.8-1
- Allow hypervkvp_t write access to NetworkManager_etc_rw_t
- Add interface for write-only access to NetworkManager rw conf
- Allow systemd-sleep send a message to syslog over a unix dgram socket
- Allow init create and use netlink netfilter socket
- Allow qatlib load kernel modules
- Allow qatlib run lspci
- Allow qatlib manage its private runtime socket files
- Allow qatlib read/write vfio devices
- Label /etc/redis.conf with redis_conf_t
- Remove the lockdown-class rules from the policy
- Allow init read all non-security socket files
- Replace redundant dnsmasq pattern macros
- Remove unneeded symlink perms in dnsmasq.if
- Add additions to dnsmasq interface
- Allow nvme_stas_t create and use netlink kobject uevent socket
- Allow collectd connect to statsd port
- Allow keepalived_t to use sys_ptrace of cap_userns
- Allow dovecot_auth_t connect to postgresql using UNIX socket

* Wed Dec 13 2023 Zdenek Pytela <zpytela@redhat.com> - 40.7-1
- Make named_zone_t and named_var_run_t a part of the mountpoint attribute
- Allow sysadm execute traceroute in sysadm_t domain using sudo
- Allow sysadm execute tcpdump in sysadm_t domain using sudo
- Allow opafm search nfs directories
- Add support for syslogd unconfined scripts
- Allow gpsd use /dev/gnss devices
- Allow gpg read rpm cache
- Allow virtqemud additional permissions
- Allow virtqemud manage its private lock files
- Allow virtqemud use the io_uring api
- Allow ddclient send e-mail notifications
- Allow postfix_master_t map postfix data files
- Allow init create and use vsock sockets
- Allow thumb_t append to init unix domain stream sockets
- Label /dev/vas with vas_device_t
- Change domain_kernel_load_modules boolean to true
- Create interface selinux_watch_config and add it to SELinux users

* Tue Nov 28 2023 Zdenek Pytela <zpytela@redhat.com> - 40.6-1
- Add afterburn to modules-targeted-contrib.conf
- Update cifs interfaces to include fs_search_auto_mountpoints()
- Allow sudodomain read var auth files
- Allow spamd_update_t read hardware state information
- Allow virtnetworkd domain transition on tc command execution
- Allow sendmail MTA connect to sendmail LDA
- Allow auditd read all domains process state
- Allow rsync read network sysctls
- Add dhcpcd bpf capability to run bpf programs
- Dontaudit systemd-hwdb dac_override capability
- Allow systemd-sleep create efivarfs files

* Tue Nov 14 2023 Zdenek Pytela <zpytela@redhat.com> - 40.5-1
- Allow map xserver_tmpfs_t files when xserver_clients_write_xshm is on
- Allow graphical applications work in Wayland
- Allow kdump work with PrivateTmp
- Allow dovecot-auth work with PrivateTmp
- Allow nfsd get attributes of all filesystems
- Allow unconfined_domain_type use io_uring cmd on domain
- ci: Only run Rawhide revdeps tests on the rawhide branch
- Label /var/run/auditd.state as auditd_var_run_t
- Allow fido-device-onboard (FDO) read the crack database
- Allow ip an explicit domain transition to other domains
- Label /usr/libexec/selinux/selinux-autorelabel with semanage_exec_t
- Allow  winbind_rpcd_t processes access when samba_export_all_* is on
- Enable NetworkManager and dhclient to use initramfs-configured DHCP connection
- Allow ntp to bind and connect to ntske port.
- Allow system_mail_t manage exim spool files and dirs
- Dontaudit keepalived setattr on keepalived_unconfined_script_exec_t
- Label /run/pcsd.socket with cluster_var_run_t
- ci: Run cockpit tests in PRs

* Thu Oct 19 2023 Zdenek Pytela <zpytela@redhat.com> - 40.4-1
- Add map_read map_write to kernel_prog_run_bpf
- Allow systemd-fstab-generator read all symlinks
- Allow systemd-fstab-generator the dac_override capability
- Allow rpcbind read network sysctls
- Support using systemd containers
- Allow sysadm_t to connect to iscsid using a unix domain stream socket
- Add policy for coreos installer
- Add coreos_installer to modules-targeted-contrib.conf

* Tue Oct 17 2023 Zdenek Pytela <zpytela@redhat.com> - 40.3-1
- Add policy for nvme-stas
- Confine systemd fstab,sysv,rc-local
- Label /etc/aliases.lmdb with etc_aliases_t
- Create policy for afterburn
- Add nvme_stas to modules-targeted-contrib.conf
- Add plans/tests.fmf

* Tue Oct 10 2023 Zdenek Pytela <zpytela@redhat.com> - 40.2-1
- Add the virt_supplementary module to modules-targeted-contrib.conf
- Make new virt drivers permissive
- Split virt policy, introduce virt_supplementary module
- Allow apcupsd cgi scripts read /sys
- Merge pull request #1893 from WOnder93/more-early-boot-overlay-fixes
- Allow kernel_t to manage and relabel all files
- Add missing optional_policy() to files_relabel_all_files()

* Tue Oct 03 2023 Zdenek Pytela <zpytela@redhat.com> - 40.1-1
- Allow named and ndc use the io_uring api
- Deprecate common_anon_inode_perms usage
- Improve default file context(None) of /var/lib/authselect/backups
- Allow udev_t to search all directories with a filesystem type
- Implement proper anon_inode support
- Allow targetd write to the syslog pid sock_file
- Add ipa_pki_retrieve_key_exec() interface
- Allow kdumpctl_t to list all directories with a filesystem type
- Allow udev additional permissions
- Allow udev load kernel module
- Allow sysadm_t to mmap modules_object_t files
- Add the unconfined_read_files() and unconfined_list_dirs() interfaces
- Set default file context of HOME_DIR/tmp/.* to <<none>>
- Allow kernel_generic_helper_t to execute mount(1)

## END: Generated by rpmautospec
