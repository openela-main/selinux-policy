# github repo with selinux-policy sources
%global giturl https://github.com/fedora-selinux/selinux-policy
%global commit 1f99cdaa26c4ecbb26362cb21f6cd3eb0ec473a3
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%define distro redhat
%define polyinstatiate n
%define monolithic n
%if %{?BUILD_DOC:0}%{!?BUILD_DOC:1}
%define BUILD_DOC 1
%endif
%if %{?BUILD_TARGETED:0}%{!?BUILD_TARGETED:1}
%define BUILD_TARGETED 1
%endif
%if %{?BUILD_MINIMUM:0}%{!?BUILD_MINIMUM:1}
%define BUILD_MINIMUM 1
%endif
%if %{?BUILD_MLS:0}%{!?BUILD_MLS:1}
%define BUILD_MLS 1
%endif
%define POLICYVER 33
%define POLICYCOREUTILSVER 3.4-1
%define CHECKPOLICYVER 3.2
Summary: SELinux policy configuration
Name: selinux-policy
Version: 38.1.23
Release: 1%{?dist}.2
License: GPLv2+
Source: %{giturl}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1: modules-targeted-base.conf
Source31: modules-targeted-contrib.conf
Source2: booleans-targeted.conf
Source3: Makefile.devel
Source4: setrans-targeted.conf
Source5: modules-mls-base.conf
Source32: modules-mls-contrib.conf
Source6: booleans-mls.conf
Source8: setrans-mls.conf
Source14: securetty_types-targeted
Source15: securetty_types-mls
#Source16: modules-minimum.conf
Source17: booleans-minimum.conf
Source18: setrans-minimum.conf
Source19: securetty_types-minimum
Source20: customizable_types
Source22: users-mls
Source23: users-targeted
Source25: users-minimum
Source26: file_contexts.subs_dist
Source27: selinux-policy.conf
Source28: permissivedomains.cil
Source30: booleans.subs_dist

# Tool helps during policy development, to expand system m4 macros to raw allow rules
# Git repo: https://github.com/fedora-selinux/macro-expander.git
Source33: macro-expander

# Include SELinux policy for container from separate container-selinux repo
# Git repo: https://github.com/containers/container-selinux.git
Source35: container-selinux.tgz

Source36: selinux-check-proper-disable.service

# Provide rpm macros for packages installing SELinux modules
Source102: rpm.macros

Url: %{giturl}
BuildArch: noarch
BuildRequires: python3 gawk checkpolicy >= %{CHECKPOLICYVER} m4 policycoreutils-devel >= %{POLICYCOREUTILSVER} bzip2
BuildRequires: make
BuildRequires: systemd-rpm-macros
Requires(pre): policycoreutils >= %{POLICYCOREUTILSVER}
Requires(post): /bin/awk /usr/bin/sha512sum
Requires(meta): rpm-plugin-selinux
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
%{_sbindir}/semodule -n -X 100 -i %{_datadir}/selinux/packages/sandbox.pp
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
%exclude %{_datadir}/selinux/devel/include/contrib/passt.if
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
%{_mandir}/ru/*/*
%doc %{_datadir}/doc/%{name}

%define common_params DISTRO=%{distro} UBAC=n DIRECT_INITRC=n MONOLITHIC=%{monolithic} MLS_CATS=1024 MCS_CATS=1024

%define makeCmds() \
%make_build %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 bare \
%make_build %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 conf \
cp -f selinux_config/booleans-%1.conf ./policy/booleans.conf \
cp -f selinux_config/users-%1 ./policy/users \
#cp -f selinux_config/modules-%1-base.conf  ./policy/modules.conf \

%define makeModulesConf() \
cp -f selinux_config/modules-%1-%2.conf  ./policy/modules-base.conf \
cp -f selinux_config/modules-%1-%2.conf  ./policy/modules.conf \
if [ %3 == "contrib" ];then \
	cp selinux_config/modules-%1-%3.conf ./policy/modules-contrib.conf; \
	cat selinux_config/modules-%1-%3.conf >> ./policy/modules.conf; \
fi; \

%define installCmds() \
%make_build %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 base.pp \
%make_build %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 validate modules \
make %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 DESTDIR=%{buildroot} install \
make %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 DESTDIR=%{buildroot} install-appconfig \
make %common_params UNK_PERMS=%3 NAME=%1 TYPE=%2 DESTDIR=%{buildroot} SEMODULE="%{_sbindir}/semodule -p %{buildroot} -X 100 " load \
%{__mkdir} -p %{buildroot}%{_sysconfdir}/selinux/%1/logins \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.subs \
install -m0644 selinux_config/securetty_types-%1 %{buildroot}%{_sysconfdir}/selinux/%1/contexts/securetty_types \
install -m0644 selinux_config/file_contexts.subs_dist %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files \
install -m0644 selinux_config/setrans-%1.conf %{buildroot}%{_sysconfdir}/selinux/%1/setrans.conf \
install -m0644 selinux_config/customizable_types %{buildroot}%{_sysconfdir}/selinux/%1/contexts/customizable_types \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.bin \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.local \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.local.bin \
cp %{SOURCE30} %{buildroot}%{_sysconfdir}/selinux/%1 \
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
%{_datadir}/selinux/%1/modules-base.lst \
%{_datadir}/selinux/%1/modules-contrib.lst \
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
if %{_sbindir}/restorecon -e /run/media -R /root /var/log /var/run /etc/passwd* /etc/group* /etc/*shadow* 2> /dev/null;then \
    continue; \
fi;

%define preInstall() \
if [ $1 -ne 1 ] && [ -s %{_sysconfdir}/selinux/config ]; then \
     for MOD_NAME in ganesha ipa_custodia kdbus; do \
        if [ -d %{_sharedstatedir}/selinux/%1/active/modules/100/$MOD_NAME ]; then \
           %{_sbindir}/semodule -n -d $MOD_NAME; \
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
%{_sbindir}/semodule -B -n -s %2; \
[ "${SELINUXTYPE}" == "%2" ] && %{_sbindir}/selinuxenabled && load_policy; \
if [ %1 -eq 1 ]; then \
   %{_sbindir}/restorecon -R /root /var/log /run /etc/passwd* /etc/group* /etc/*shadow* 2> /dev/null; \
else \
%relabel %2 \
fi;

%define modulesList() \
awk '$1 !~ "/^#/" && $2 == "=" && $3 == "module" { printf "%%s ", $1 }' ./policy/modules-base.conf > %{buildroot}%{_datadir}/selinux/%1/modules-base.lst \
awk '$1 !~ "/^#/" && $2 == "=" && $3 == "base" { printf "%%s ", $1 }' ./policy/modules-base.conf > %{buildroot}%{_datadir}/selinux/%1/base.lst \
if [ -e ./policy/modules-contrib.conf ];then \
	awk '$1 !~ "/^#/" && $2 == "=" && $3 == "module" { printf "%%s ", $1 }' ./policy/modules-contrib.conf > %{buildroot}%{_datadir}/selinux/%1/modules-contrib.lst; \
fi;

%define nonBaseModulesList() \
contrib_modules=`cat %{buildroot}%{_datadir}/selinux/%1/modules-contrib.lst` \
base_modules=`cat %{buildroot}%{_datadir}/selinux/%1/modules-base.lst` \
for i in $contrib_modules $base_modules; do \
    if [ $i != "sandbox" ];then \
        echo "%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/modules/100/$i" >> %{buildroot}%{_datadir}/selinux/%1/nonbasemodules.lst \
    fi; \
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

%build

%prep
%setup -n %{name}-%{commit} -q
tar -C policy/modules/contrib -xf %{SOURCE35}

mkdir selinux_config
for i in %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5} %{SOURCE6} %{SOURCE8} %{SOURCE14} %{SOURCE15} %{SOURCE17} %{SOURCE18} %{SOURCE19} %{SOURCE20} %{SOURCE22} %{SOURCE23} %{SOURCE25} %{SOURCE26} %{SOURCE31} %{SOURCE32};do
 cp $i selinux_config
done

%install
# Build targeted policy
%{__rm} -fR %{buildroot}
mkdir -p %{buildroot}%{_sysconfdir}/selinux
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
touch %{buildroot}%{_sysconfdir}/selinux/config
touch %{buildroot}%{_sysconfdir}/sysconfig/selinux
mkdir -p %{buildroot}%{_usr}/lib/tmpfiles.d/
cp %{SOURCE27} %{buildroot}%{_usr}/lib/tmpfiles.d/
mkdir -p %{buildroot}%{_bindir}
install -m 755  %{SOURCE33} %{buildroot}%{_bindir}/

# Always create policy module package directories
mkdir -p %{buildroot}%{_datadir}/selinux/{targeted,mls,minimum,modules}/
mkdir -p %{buildroot}%{_sharedstatedir}/selinux/{targeted,mls,minimum,modules}/

mkdir -p %{buildroot}%{_datadir}/selinux/packages

# Install devel
make clean
%if %{BUILD_TARGETED}
# Build targeted policy
%makeCmds targeted mcs allow
%makeModulesConf targeted base contrib
%installCmds targeted mcs allow
# install permissivedomains.cil
%{_sbindir}/semodule -p %{buildroot} -X 100 -s targeted -i %{SOURCE28}
# recreate sandbox.pp
rm -rf %{buildroot}%{_sharedstatedir}/selinux/targeted/active/modules/100/sandbox
%make_build %common_params UNK_PERMS=allow NAME=targeted TYPE=mcs sandbox.pp
mv sandbox.pp %{buildroot}%{_datadir}/selinux/packages/sandbox.pp
%modulesList targeted
%nonBaseModulesList targeted
%endif

%if %{BUILD_MINIMUM}
# Build minimum policy
%makeCmds minimum mcs allow
%makeModulesConf targeted base contrib
%installCmds minimum mcs allow
rm -rf %{buildroot}%{_sharedstatedir}/selinux/minimum/active/modules/100/sandbox
%modulesList minimum
%nonBaseModulesList minimum
%endif

%if %{BUILD_MLS}
# Build mls policy
%makeCmds mls mls deny
%makeModulesConf mls base contrib
%installCmds mls mls deny
%modulesList mls
%nonBaseModulesList mls
%endif

# remove leftovers when save-previous=true (semanage.conf) is used
rm -rf %{buildroot}%{_sharedstatedir}/selinux/{minimum,targeted,mls}/previous

mkdir -p %{buildroot}%{_mandir}
cp -R  man/* %{buildroot}%{_mandir}
make %common_params UNK_PERMS=allow NAME=targeted TYPE=mcs DESTDIR=%{buildroot} PKGNAME=%{name} install-docs
make %common_params UNK_PERMS=allow NAME=targeted TYPE=mcs DESTDIR=%{buildroot} PKGNAME=%{name} install-headers
mkdir %{buildroot}%{_datadir}/selinux/devel/
mv %{buildroot}%{_datadir}/selinux/targeted/include %{buildroot}%{_datadir}/selinux/devel/include
install -m 644 selinux_config/Makefile.devel %{buildroot}%{_datadir}/selinux/devel/Makefile
install -m 644 doc/example.* %{buildroot}%{_datadir}/selinux/devel/
install -m 644 doc/policy.* %{buildroot}%{_datadir}/selinux/devel/
%{_bindir}/sepolicy manpage -a -p %{buildroot}%{_datadir}/man/man8/ -w -r %{buildroot}
mkdir %{buildroot}%{_datadir}/selinux/devel/html
mv %{buildroot}%{_datadir}/man/man8/*.html %{buildroot}%{_datadir}/selinux/devel/html
mv %{buildroot}%{_datadir}/man/man8/style.css %{buildroot}%{_datadir}/selinux/devel/html

mkdir -p %{buildroot}%{_rpmconfigdir}/macros.d
install -m 644 %{SOURCE102} %{buildroot}%{_rpmconfigdir}/macros.d/macros.selinux-policy
sed -i 's/SELINUXPOLICYVERSION/%{version}-%{release}/' %{buildroot}%{_rpmconfigdir}/macros.d/macros.selinux-policy
sed -i 's@SELINUXSTOREPATH@%{_sharedstatedir}/selinux@' %{buildroot}%{_rpmconfigdir}/macros.d/macros.selinux-policy

mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE36} %{buildroot}%{_unitdir}

rm -rf selinux_config

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
# https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/using_selinux/changing-selinux-states-and-modes_using-selinux#changing-selinux-modes-at-boot-time_changing-selinux-states-and-modes
#
# NOTE: Up to RHEL 8 release included, SELINUX=disabled would also
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

%if %{BUILD_TARGETED}
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

%description targeted
SELinux targeted policy package.

%pretrans targeted -p <lua>
%backupConfigLua

%pre targeted
%preInstall targeted

%post targeted
%checkConfigConsistency targeted
%postInstall $1 targeted
exit 0

%posttrans targeted
%checkConfigConsistency targeted

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
%{_sbindir}/selinuxenabled && %{_sbindir}/semodule -nB
exit 0

%triggerpostun -- selinux-policy-targeted < 3.12.1-74
rm -f %{_sysconfdir}/selinux/*/modules/active/modules/sandbox.pp.disabled 2>/dev/null
exit 0

%triggerpostun targeted -- selinux-policy-targeted < 3.13.1-138
CR=$'\n'
INPUT=""
for i in `find %{_sysconfdir}/selinux/targeted/modules/active/modules/ -name \*disabled`; do
    module=`basename $i | sed 's/.pp.disabled//'`
    if [ -d %{_sharedstatedir}/selinux/targeted/active/modules/100/$module ]; then
        touch %{_sharedstatedir}/selinux/targeted/active/modules/disabled/$p
    fi
done
for i in `find %{_sysconfdir}/selinux/targeted/modules/active/modules/ -name \*.pp`; do
    INPUT="${INPUT}${CR}module -N -a $i"
done
for i in $(find %{_sysconfdir}/selinux/targeted/modules/active -name \*.local); do
    cp $i %{_sharedstatedir}/selinux/targeted/active
done
echo "$INPUT" | %{_sbindir}/semanage import -S targeted -N
if %{_sbindir}/selinuxenabled ; then
        %{_sbindir}/load_policy
fi
exit 0

%files targeted -f %{buildroot}%{_datadir}/selinux/targeted/nonbasemodules.lst
%config(noreplace) %{_sysconfdir}/selinux/targeted/contexts/users/unconfined_u
%config(noreplace) %{_sysconfdir}/selinux/targeted/contexts/users/sysadm_u
%fileList targeted
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/targeted/active/modules/100/permissivedomains
%endif

%if %{BUILD_MINIMUM}
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
contribpackages=`cat %{_datadir}/selinux/minimum/modules-contrib.lst`
basepackages=`cat %{_datadir}/selinux/minimum/modules-base.lst`
if [ ! -d %{_sharedstatedir}/selinux/minimum/active/modules/disabled ]; then
    mkdir %{_sharedstatedir}/selinux/minimum/active/modules/disabled
fi
if [ $1 -eq 1 ]; then
for p in $contribpackages; do
    touch %{_sharedstatedir}/selinux/minimum/active/modules/disabled/$p
done
for p in $basepackages apache dbus inetd kerberos mta nis; do
    rm -f %{_sharedstatedir}/selinux/minimum/active/modules/disabled/$p
done
%{_sbindir}/semanage import -S minimum -f - << __eof
login -m  -s unconfined_u -r s0-s0:c0.c1023 __default__
login -m  -s unconfined_u -r s0-s0:c0.c1023 root
__eof
%{_sbindir}/restorecon -R /root /var/log /var/run 2> /dev/null
%{_sbindir}/semodule -B -s minimum
else
instpackages=`cat %{_datadir}/selinux/minimum/instmodules.lst`
for p in $contribpackages; do
    touch %{_sharedstatedir}/selinux/minimum/active/modules/disabled/$p
done
for p in $instpackages apache dbus inetd kerberos mta nis; do
    rm -f %{_sharedstatedir}/selinux/minimum/active/modules/disabled/$p
done
%{_sbindir}/semodule -B -s minimum
%relabel minimum
fi
exit 0

%posttrans minimum
%checkConfigConsistency minimum

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

%triggerpostun minimum -- selinux-policy-minimum < 3.13.1-138
if [ `ls -A %{_sharedstatedir}/selinux/minimum/active/modules/disabled/` ]; then
    rm -f %{_sharedstatedir}/selinux/minimum/active/modules/disabled/*
fi
CR=$'\n'
INPUT=""
for i in `find %{_sysconfdir}/selinux/minimum/modules/active/modules/ -name \*disabled`; do
    module=`basename $i | sed 's/.pp.disabled//'`
    if [ -d %{_sharedstatedir}/selinux/minimum/active/modules/100/$module ]; then
        touch %{_sharedstatedir}/selinux/minimum/active/modules/disabled/$p
    fi
done
for i in `find %{_sysconfdir}/selinux/minimum/modules/active/modules/ -name \*.pp`; do
    INPUT="${INPUT}${CR}module -N -a $i"
done
echo "$INPUT" | %{_sbindir}/semanage import -S minimum -N
if %{_sbindir}/selinuxenabled ; then
    %{_sbindir}/load_policy
fi
exit 0

%files minimum -f %{buildroot}%{_datadir}/selinux/minimum/nonbasemodules.lst
%config(noreplace) %{_sysconfdir}/selinux/minimum/contexts/users/unconfined_u
%config(noreplace) %{_sysconfdir}/selinux/minimum/contexts/users/sysadm_u
%fileList minimum
%endif

%if %{BUILD_MLS}
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
%postInstall $1 mls
exit 0

%posttrans mls
%checkConfigConsistency mls

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

%triggerpostun mls -- selinux-policy-mls < 3.13.1-138
CR=$'\n'
INPUT=""
for i in `find %{_sysconfdir}/selinux/mls/modules/active/modules/ -name \*disabled`; do
    module=`basename $i | sed 's/.pp.disabled//'`
    if [ -d %{_sharedstatedir}/selinux/mls/active/modules/100/$module ]; then
        touch %{_sharedstatedir}/selinux/mls/active/modules/disabled/$p
    fi
done
for i in `find %{_sysconfdir}/selinux/mls/modules/active/modules/ -name \*.pp`; do
    INPUT="${INPUT}${CR}module -N -a $i"
done
echo "$INPUT" | %{_sbindir}/semanage import -S mls -N
if %{_sbindir}/selinuxenabled ; then
        %{_sbindir}/load_policy
fi
exit 0


%files mls -f %{buildroot}%{_datadir}/selinux/mls/nonbasemodules.lst
%config(noreplace) %{_sysconfdir}/selinux/mls/contexts/users/unconfined_u
%fileList mls
%endif

%changelog
* Wed Jan 10 2024 Zdenek Pytela <zpytela@redhat.com> - 38.1.23-1.2
- Allow qatlib set attributes of vfio device files
Resolves: RHEL-19052
- Allow qatlib load kernel modules
Resolves: RHEL-19052
- Allow qatlib run lspci
Resolves: RHEL-19052
- Allow qatlib manage its private runtime socket files
Resolves: RHEL-19052
- Allow qatlib read/write vfio devices
Resolves: RHEL-19052

* Tue Dec 05 2023 Juraj Marcin <jmarcin@redhat.com> - 38.1.23-1.1
- Allow ip an explicit domain transition to other domains
Resolves: RHEL-14248

* Fri Aug 25 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.23-1
- Allow cups-pdf connect to the system log service
Resolves: rhbz#2234765
- Update policy for qatlib
Resolves: rhbz#2080443

* Thu Aug 24 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.22-1
- Allow qatlib  to modify hardware state information.
Resolves: rhbz#2080443
- Update policy for fdo
Resolves: rhbz#2229722
- Allow gpsd, oddjob and oddjob_mkhomedir_t write user_tty_device_t chr_file
Resolves: rhbz#2223305
- Allow svirt to rw /dev/udmabuf
Resolves: rhbz#2223727
- Allow keepalived watch var_run dirs
Resolves: rhbz#2186759

* Thu Aug 17 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.21-1
- Allow logrotate_t to map generic files in /etc
Resolves: rhbz#2231257
- Allow insights-client manage user temporary files
Resolves: rhbz#2224737
- Make insights_client_t an unconfined domain
Resolves: rhbz#2225526

* Fri Aug 11 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.20-1
- Allow user_u and staff_u get attributes of non-security dirs
Resolves: rhbz#2215507
- Allow cloud_init create dhclient var files and init_t manage net_conf_t
Resolves: rhbz#2225418
- Allow samba-dcerpc service manage samba tmp files
Resolves: rhbz#2230365
- Update samba-dcerpc policy for printing
Resolves: rhbz#2230365
- Allow sysadm_t run kernel bpf programs
Resolves: rhbz#2229936
- allow mon_procd_t self:cap_userns sys_ptrace
Resolves: rhbz#2221986
- Remove nsplugin_role from mozilla.if
Resolves: rhbz#2221251
- Allow unconfined user filetrans chrome_sandbox_home_t
Resolves: rhbz#2187893
- Allow pdns name_bind and name_connect all ports
Resolves: rhbz#2047945
- Allow insights-client read and write cluster tmpfs files
Resolves: rhbz#2221631
- Allow ipsec read nsfs files
Resolves: rhbz#2230277
- Allow upsmon execute upsmon via a helper script
Resolves: rhbz#2228403
- Fix labeling for no-stub-resolv.conf
Resolves: rhbz#2148390
- Add use_nfs_home_dirs boolean for mozilla_plugin
Resolves: rhbz#2214298
- Change wording in /etc/selinux/config
Resolves: rhbz#2143153

* Thu Aug 03 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.19-1
- Allow qatlib to read sssd public files
Resolves: rhbz#2080443
- Fix location for /run/nsd
Resolves: rhbz#2181600
- Allow samba-rpcd work with passwords
Resolves: rhbz#2107092
- Allow rpcd_lsad setcap and use generic ptys
Resolves: rhbz#2107092
- Allow gpsd,oddjob,oddjob_mkhomedir rw user domain pty
Resolves: rhbz#2223305
- Allow keepalived to manage its tmp files
Resolves: rhbz#2179212
- Allow nscd watch system db dirs
Resolves: rhbz#2152124

* Fri Jul 21 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.18-1
- Boolean: Allow virt_qemu_ga create ssh directory
Resolves: rhbz#2181402
- Allow virt_qemu_ga_t create .ssh dir with correct label
Resolves: rhbz#2181402
- Set default ports for keylime policy
Resolves: RHEL-594
- Allow unconfined service inherit signal state from init
Resolves: rhbz#2186233
- Allow sa-update connect to systemlog services
Resolves: rhbz#2220643
- Allow sa-update manage spamc home files
Resolves: rhbz#2220643
- Label only /usr/sbin/ripd and ripngd with zebra_exec_t
Resolves: rhbz#2213605
- Add the files_getattr_non_auth_dirs() interface
Resolves: rhbz#2076933
- Update policy for the sblim-sfcb service
Resolves: rhbz#2076933
- Define equivalency for /run/systemd/generator.early
Resolves: rhbz#2213516

* Thu Jun 29 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.17-1
- Add the qatlib  module
Resolves: rhbz#2080443
- Add the fdo module
Resolves: rhbz#2026795
- Add the booth module to modules.conf
Resolves: rhbz#2128833

* Thu Jun 29 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.16-1
- Remove permissive from fdo
Resolves: rhbz#2026795
- Add the qatlib  module
Resolves: rhbz#2080443
- Add the fdo module
Resolves: rhbz#2026795
- Add the booth module to modules.conf
Resolves: rhbz#2128833
- Add policy for FIDO Device Onboard
Resolves: rhbz#2026795
- Create policy for qatlib
Resolves: rhbz#2080443
- Add policy for boothd
Resolves: rhbz#2128833
- Add list_dir_perms to kerberos_read_keytab
Resolves: rhbz#2112729
- Allow nsd_crond_t write nsd_var_run_t & connectto nsd_t
Resolves: rhbz#2209973
- Allow collectd_t read network state symlinks
Resolves: rhbz#2209650
- Revert "Allow collectd_t read proc_net link files"
Resolves: rhbz#2209650
- Allow insights-client execmem
Resolves: rhbz#2207894
- Label udf tools with fsadm_exec_t
Resolves: rhbz#2039774

* Thu Jun 15 2023 Zdenek Pytela <zpytela@redhat.com> - 38.1.15-1
- Add fs_delete_pstore_files() interface
Resolves: rhbz#2181565
- Add fs_read_pstore_files() interface
Resolves: rhbz#2181565
- Allow insights-client getsession process permission
Resolves: rhbz#2214581
- Allow insights-client work with pipe and socket tmp files
Resolves: rhbz#2214581
- Allow insights-client map generic log files
Resolves: rhbz#2214581
- Allow insights-client read unconfined service semaphores
Resolves: rhbz#2214581
- Allow insights-client get quotas of all filesystems
Resolves: rhbz#2214581
- Allow haproxy read hardware state information
Resolves: rhbz#2164691
- Allow cupsd dbus chat with xdm
Resolves: rhbz#2143641
- Allow dovecot_deliver_t create/map dovecot_spool_t dir/file
Resolves: rhbz#2165863
- Add none file context for polyinstantiated tmp dirs
Resolves: rhbz#2099194
- Add support for the systemd-pstore service
Resolves: rhbz#2181565
- Label /dev/userfaultfd with userfaultfd_t
Resolves: rhbz#2175290
- Allow collectd_t read proc_net link files
Resolves: rhbz#2209650
- Label smtpd with sendmail_exec_t
Resolves: rhbz#2213573
- Label msmtp and msmtpd with sendmail_exec_t
Resolves: rhbz#2213573
- Allow dovecot-deliver write to the main process runtime fifo files
Resolves: rhbz#2211787
- Allow subscription-manager execute ip
Resolves: rhbz#2211566
- Allow ftpd read network sysctls
Resolves: rhbz#2175856

* Fri May 26 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.14-1
- Allow firewalld rw ica_tmpfs_t files
Resolves: rhbz#2207487
- Add chromium_sandbox_t setcap capability
Resolves: rhbz#2187893
- Allow certmonger manage cluster library files
Resolves: rhbz#2179022
- Allow wireguard to rw network sysctls
Resolves: rhbz#2192154
- Label /usr/lib/systemd/system/proftpd.* & vsftpd.* with ftpd_unit_file_t
Resolves: rhbz#2188173
- Allow plymouthd_t bpf capability to run bpf programs
Resolves: rhbz#2184803
- Update pkcsslotd policy for sandboxing
Resolves: rhbz#2209235
- Allow unconfined_service_t to create .gnupg labeled as gpg_secret_t
Resolves: rhbz#2203201

* Thu May 18 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.13-1
- Allow insights-client work with teamdctl
Resolves: rhbz#2190178
- Allow virsh name_connect virt_port_t
Resolves: rhzb#2187290
- Allow cupsd to create samba_var_t files
Resolves: rhbz#2174445
- Allow dovecot to map files in /var/spool/dovecot
Resolves: rhbz#2165863
- Add tunable to allow squid bind snmp port
Resolves: rhbz#2151378
- Allow rhsmcert request the kernel to load a module
Resolves: rhbz#2203359
- Allow snmpd read raw disk data
Resolves: rhbz#2196528

* Fri Apr 14 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.12-1
- Allow cloud-init domain transition to insights-client domain
Resolves: rhbz#2162663
- Allow chronyd send a message to cloud-init over a datagram socket
Resolves: rhbz#2162663
- Allow dmidecode write to cloud-init tmp files
Resolves: rhbz#2162663
- Allow login_pgm setcap permission
Resolves: rhbz#2174331
- Allow tshark the setsched capability
Resolves: rhbz#2165634
- Allow chronyc read network sysctls
Resolves: rhbz#2173604
- Allow systemd-timedated watch init runtime dir
Resolves: rhbz#2175137
- Add journalctl the sys_resource capability
Resolves: rhbz#2153782
- Allow system_cronjob_t transition to rpm_script_t
Resolves: rhbz#2173685
- Revert "Allow system_cronjob_t domtrans to rpm_script_t"
Resolves: rhbz#2173685
- Allow insights-client tcp connect to all ports
Resolves: rhbz#2183083
- Allow insights-client work with su and lpstat
Resolves: rhbz#2183083
- Allow insights-client manage fsadm pid files
Resolves: rhbz#2183083
- Allow insights-client read all sysctls
Resolves: rhbz#2183083
- Allow rabbitmq to read network sysctls
Resolves: rhbz#2184999

* Tue Mar 28 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.11-2
- rebuilt
Resolves: rhbz#2172268

* Mon Mar 27 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.11-1
- Allow passt manage qemu pid sock files
Resolves: rhbz#2172268
- Exclude passt.if from selinux-policy-devel
Resolves: rhbz#2172268

* Fri Mar 24 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.10-1
- Add support for the passt_t domain
Resolves: rhbz#2172268
- Allow virtd_t and svirt_t work with passt
Resolves: rhbz#2172268
- Add new interfaces in the virt module
Resolves: rhbz#2172268
- Add passt interfaces defined conditionally
Resolves: rhbz#2172268

* Thu Mar 16 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.9-1
- Boolean: allow qemu-ga manage ssh home directory
Resolves: rhbz#2178612
- Allow wg load kernel modules, search debugfs dir
Resolves: rhbz#2176487

* Thu Feb 16 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.8-1
- Allow svirt to map svirt_image_t char files
Resolves: rhbz#2170482
- Fix opencryptoki file names in /dev/shm
Resolves: rhbz#2166283

* Wed Feb 15 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.7-1
- Allow staff_t getattr init pid chr & blk files and read krb5
Resolves: rhbz#2112729
- Allow firewalld to rw z90crypt device
Resolves: rhbz#2166877
- Allow httpd work with tokens in /dev/shm
Resolves: rhbz#2166283

* Thu Feb 09 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.6-1
- Allow modemmanager create hardware state information files
Resolves: rhbz#2149560
- Dontaudit ftpd the execmem permission
Resolves: rhbz#2164434
- Allow nm-dispatcher plugins read generic files in /proc
Resolves: rhbz#2164845
- Label systemd-journald feature LogNamespace
Resolves: rhbz#2124797
- Boolean: allow qemu-ga read ssh home directory
Resolves: rhbz#1917024

* Thu Jan 26 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.5-1
- Reuse tmpfs_t also for the ramfs filesystem
Resolves: rhbz#2160391
- Allow systemd-resolved watch tmpfs directories
Resolves: rhbz#2160391
- Allow hostname_t to read network sysctls.
Resolves: rhbz#2161958
- Allow ModemManager all permissions for netlink route socket
Resolves: rhbz#2149560
- Allow unconfined user filetransition for sudo log files
Resolves: rhbz#2160388
- Allow sudodomain use sudo.log as a logfile
Resolves: rhbz#2160388
- Allow nm-cloud-setup dispatcher plugin restart nm services
Resolves: rhbz#2154414
- Allow wg to send msg to kernel, write to syslog and dbus connections
Resolves: rhbz#2149452
- Allow rshim bpf cap2 and read sssd public files
Resolves: rhbz#2080439
- Allow svirt request the kernel to load a module
Resolves: rhbz#2144735
- Rebase selinux-policy to the latest one in rawhide
Resolves: rhbz#2014606

* Thu Jan 12 2023 Nikola Knazekova <nknazeko@redhat.com> - 38.1.4-1
- Add lpr_roles  to system_r roles
Resolves: rhbz#2152150
- Allow insights client work with gluster and pcp
Resolves: rhbz#2152150
- Add interfaces in domain, files, and unconfined modules
Resolves: rhbz#2152150
- Label fwupdoffline and fwupd-detect-cet with fwupd_exec_t
Resolves: rhbz#2152150
- Add insights additional capabilities
Resolves: rhbz#2152150
- Revert "Allow insights-client run lpr and allow the proper role"
Resolves: rhbz#2152150
- Allow prosody manage its runtime socket files
Resolves: rhbz#2157891
- Allow syslogd read network sysctls
Resolves: rhbz#2156068
- Allow NetworkManager and wpa_supplicant the bpf capability
Resolves: rhbz#2137085
- Allow sysadm_t read/write ipmi devices
Resolves: rhbz#2158419
- Allow wireguard to create udp sockets and read net_conf
Resolves: rhbz#2149452
- Allow systemd-rfkill the bpf capability
Resolves: rhbz#2149390
- Allow load_policy_t write to unallocated ttys
Resolves: rhbz#2145181
- Allow winbind-rpcd manage samba_share_t files and dirs
Resolves: rhbz#2150680

* Thu Dec 15 2022 Nikola Knazekova <nknazeko@redhat.com> - 38.1.3-1
- Allow stalld to read /sys/kernel/security/lockdown file
Resolves: rhbz#2140673
- Allow syslog the setpcap capability
Resolves: rhbz#2151841
- Allow pulseaudio to write to session_dbusd tmp socket files
Resolves: rhbz#2132942
- Allow keepalived to set resource limits
Resolves: rhbz#2151212
- Add policy for mptcpd
Resolves: bz#1972222
- Add policy for rshim
Resolves: rhbz#2080439
- Allow insights-client dbus chat with abrt
Resolves: rhbz#2152166
- Allow insights-client work with pcp and manage user config files
Resolves: rhbz#2152150
- Allow insights-client run lpr and allow the proper role
Resolves: rhbz#2152150
- Allow insights-client tcp connect to various ports
Resolves: rhbz#2152150
- Allow insights-client dbus chat with various services
Resolves: rhbz#2152150
- Allow journalctl relabel with var_log_t and syslogd_var_run_t files
Resolves: rhbz#2152823

* Wed Nov 30 2022 Zdenek Pytela <zpytela@redhat.com> - 38.1.2-1
- Allow insights client communicate with cupsd, mysqld, openvswitch, redis
Resolves: rhbz#2124549
- Allow insights client read raw memory devices
Resolves: rhbz#2124549
- Allow networkmanager_dispatcher_plugin work with nscd
Resolves: rhbz#2149317
- Allow ipsec_t only read tpm devices
Resolves: rhbz#2147380
- Watch_sb all file type directories.
Resolves: rhbz#2139363
- Add watch and watch_sb dosfs interface
Resolves: rhbz#2139363
- Revert "define lockdown class and access"
Resolves: rhbz#2145266
- Allow postfix/smtpd read kerberos key table
Resolves: rhbz#2145266
- Remove the lockdown class from the policy
Resolves: rhbz#2145266
- Remove label for /usr/sbin/bgpd
Resolves: rhbz#2145266
- Revert "refpolicy: drop unused socket security classes"
Resolves: rhbz#2145266

* Mon Nov 21 2022 Zdenek Pytela <zpytela@redhat.com> - 38.1.1-1
- Rebase selinux-policy to the latest one in rawhide
Resolves: rhbz#2082524

* Wed Nov 16 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.47-1
- Add domain_unix_read_all_semaphores() interface
Resolves: rhbz#2123358
- Allow chronyd talk with unconfined user over unix domain dgram socket
Resolves: rhbz#2141255
- Allow unbound connectto unix_stream_socket
Resolves: rhbz#2141236
- added policy for systemd-socket-proxyd
Resolves: rhbz#2141606
- Allow samba-dcerpcd use NSCD services over a unix stream socket
Resolves: rhbz#2121729
- Allow insights-client unix_read all domain semaphores
Resolves: rhbz#2123358
- Allow insights-client manage generic locks
Resolves: rhbz#2123358
- Allow insights-client create gluster log dir with a transition
Resolves: rhbz#2123358
- Allow insights-client domain transition on semanage execution
Resolves: rhbz#2123358
- Disable rpm verification on interface_info
Resolves: rhbz#2134515

* Fri Nov 04 2022 Nikola Knazekova <nknazeko@redhat.com> - 34.1.46-1
- new version
Resolves: rhbz#2134827

* Thu Nov 03 2022 Nikola Knazekova <nknazeko@redhat.com> - 34.1.45-1
- Add watch_sb interfaces
Resolves: rhbz#2139363
- Add watch interfaces
Resolves: rhbz#2139363
- Allow dhcpd bpf capability to run bpf programs
Resolves: rhbz#2134827
- Allow netutils and traceroute bpf capability to run bpf programs
Resolves: rhbz#2134827
- Allow pkcs_slotd_t bpf capability to run bpf programs
Resolves: rhbz#2134827
- Allow xdm bpf capability to run bpf programs
Resolves: rhbz#2134827
- Allow pcscd bpf capability to run bpf programs
Resolves: rhbz#2134827
- Allow lldpad bpf capability to run bpf programs
Resolves: rhbz#2134827
- Allow keepalived bpf capability to run bpf programs
Resolves: rhbz#2134827
- Allow ipsec bpf capability to run bpf programs
Resolves: rhbz#2134827
- Allow fprintd bpf capability to run bpf programs
Resolves: rhbz#2134827
- Allow iptables list cgroup directories
Resolves: rhbz#2134829
- Allow dirsrv_snmp_t to manage dirsrv_config_t & dirsrv_var_run_t files
Resolves: rhbz#2042515
- Dontaudit dirsrv search filesystem sysctl directories
Resolves: rhbz#2134726

* Thu Oct 13 2022 Nikola Knazekova <nknazeko@redhat.com> - 34.1.44-1
- Allow insights-client domtrans on unix_chkpwd execution
Resolves: rhbz#2126091
- Allow insights-client connect to postgresql with a unix socket
Resolves: rhbz#2126091
- Allow insights-client send null signal to rpm and system cronjob
Resolves: rhbz#2126091
- Allow insights-client manage samba var dirs
Resolves: rhbz#2126091
- Allow rhcd compute selinux access vector
Resolves: rhbz#2126091
- Add file context entries for insights-client and rhc
Resolves: rhbz#2126161
- Allow pulseaudio create gnome content (~/.config)
Resolves: rhbz#2132942
- Allow rhsmcertd execute gpg
Resolves: rhbz#2130204
- Label ports 10161-10162 tcp/udp with snmp
Resolves: rhbz#2133221
- Allow lldpad send to unconfined_t over a unix dgram socket
Resolves: rhbz#2112044
- Label port 15354/tcp and 15354/udp with opendnssec
Resolves: rhbz#2057501
- Allow aide to connect to systemd_machined with a unix socket.
Resolves: bz#2062936
- Allow ftpd map ftpd_var_run files
Resolves: bz#2124943
- Allow ptp4l respond to pmc
Resolves: rhbz#2131689
- Allow radiusd connect to the radacct port
Resolves: rhbz#2132424
- Allow xdm execute gnome-atspi services
Resolves: rhbz#2132244
- Allow ptp4l_t name_bind ptp_event_port_t
Resolves: rhbz#2130170
- Allow targetclid to manage tmp files
Resolves: rhbz#2127408
- Allow sbd the sys_ptrace capability
Resolves: rhbz#2124695

* Thu Sep 08 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.43-1
- Update rhcd policy for executing additional commands 5
Resolves: rhbz#2119351
- Update rhcd policy for executing additional commands 4
Resolves: rhbz#2119351
- Allow rhcd create rpm hawkey logs with correct label
Resolves: rhbz#2119351
- Update rhcd policy for executing additional commands 3
Resolves: rhbz#2119351
- Allow sssd to set samba setting
Resolves: rhbz#2121125
- Allow journalctl read rhcd fifo files
Resolves: rhbz#2119351
- Update insights-client policy for additional commands execution 5
Resolves: rhbz#2121125
- Confine insights-client systemd unit
Resolves: rhbz#2121125
- Update insights-client policy for additional commands execution 4
Resolves: rhbz#2121125
- Update insights-client policy for additional commands execution 3
Resolves: rhbz#2121125
- Allow rhcd execute all executables
Resolves: rhbz#2119351
- Update rhcd policy for executing additional commands 2
Resolves: rhbz#2119351
- Update insights-client policy for additional commands execution 2
Resolves: rhbz#2121125

* Mon Aug 29 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.42-1
- Label /var/log/rhc-worker-playbook with rhcd_var_log_t
Resolves: rhbz#2119351
- Update insights-client policy (auditctl, gpg, journal)
Resolves: rhbz#2107363

* Thu Aug 25 2022 Nikola Knazekova <nknazeko@redhat.com> - 34.1.41-1
- Allow unconfined domains to bpf all other domains
Resolves: RHBZ#2112014
- Allow stalld get and set scheduling policy of all domains.
Resolves: rhbz#2105038
- Allow unconfined_t transition to targetclid_home_t
Resolves: RHBZ#2106360
- Allow samba-bgqd to read a printer list
Resolves: rhbz#2118977
- Allow system_dbusd ioctl kernel with a unix stream sockets
Resolves: rhbz#2085392
- Allow chronyd bind UDP sockets to ptp_event ports.
Resolves: RHBZ#2118631
- Update tor_bind_all_unreserved_ports interface
Resolves: RHBZ#2089486
- Remove permissive domain for rhcd_t
Resolves: rhbz#2119351
- Allow unconfined and sysadm users transition for /root/.gnupg
Resolves: rhbz#2121125
- Add gpg_filetrans_admin_home_content() interface
Resolves: rhbz#2121125
- Update rhcd policy for executing additional commands
Resolves: rhbz#2119351
- Update insights-client policy for additional commands execution
Resolves: rhbz#2119507
- Add rpm setattr db files macro
Resolves: rhbz#2119507
- Add userdom_view_all_users_keys() interface
Resolves: rhbz#2119507
- Allow gpg read and write generic pty type
Resolves: rhbz#2119507
- Allow chronyc read and write generic pty type
Resolves: rhbz#2119507

* Wed Aug 10 2022 Nikola Knazekova <nknazeko@redhat.com> - 34.1.40-1
- Allow systemd-modules-load write to /dev/kmsg and send a message to syslogd
Resolves: RHBZ#2088257
- Allow systemd_hostnamed label /run/systemd/* as hostnamed_etc_t
Resolves: RHBZ#1976684
- Allow samba-bgqd get a printer list
Resolves: rhbz#2112395
- Allow networkmanager to signal unconfined process
Resolves: RHBZ#2074414
- Update NetworkManager-dispatcher policy
Resolves: RHBZ#2101910
- Allow openvswitch search tracefs dirs
Resolves: rhbz#1988164
- Allow openvswitch use its private tmpfs files and dirs
Resolves: rhbz#1988164
- Allow openvswitch fsetid capability
Resolves: rhbz#1988164

* Tue Aug 02 2022 Nikola Knazekova <nknazeko@redhat.com> - 34.1.39-1
- Add support for systemd-network-generator
Resolves: RHBZ#2111069
- Allow systemd work with install_t unix stream sockets
Resolves: rhbz#2111206
- Allow sa-update to get init status and start systemd files
Resolves: RHBZ#2061844

* Fri Jul 15 2022 Nikola Knazekova <nknazeko@redhat.com> - 34.1.38-1
- Allow some domains use sd_notify()
Resolves: rhbz#2056565
- Revert "Allow rabbitmq to use systemd notify"
Resolves: rhbz#2056565
- Update winbind_rpcd_t
Resolves: rhbz#2102084
- Update chronyd_pid_filetrans() to allow create dirs
Resolves: rhbz#2101910
- Allow keepalived read the contents of the sysfs filesystem
Resolves: rhbz#2098130
- Define LIBSEPOL version 3.4-1
Resolves: rhbz#2095688

* Wed Jun 29 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.37-1
- Allow targetclid read /var/target files
Resolves: rhbz#2020169
- Update samba-dcerpcd policy for kerberos usage 2
Resolves: rhbz#2096521
- Allow samba-dcerpcd work with sssd
Resolves: rhbz#2096521
- Allow stalld set scheduling policy of kernel threads
Resolves: rhbz#2102224

* Tue Jun 28 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.36-1
- Allow targetclid read generic SSL certificates (fixed)
Resolves: rhbz#2020169
- Fix file context pattern for /var/target
Resolves: rhbz#2020169
- Use insights_client_etc_t in insights_search_config()
Resolves: rhbz#1965013

* Fri Jun 24 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.35-1
-Add the corecmd_watch_bin_dirs() interface
Resolves: rhbz#1965013
- Update rhcd policy
Resolves: rhbz#1965013
- Allow rhcd search insights configuration directories
Resolves: rhbz#1965013
- Add the kernel_read_proc_files() interface
Resolves: rhbz#1965013
- Update insights_client_filetrans_named_content()
Resolves: rhbz#2081425
- Allow transition to insights_client named content
Resolves: rhbz#2081425
- Add the insights_client_filetrans_named_content() interface
Resolves: rhbz#2081425
- Update policy for insights-client to run additional commands 3
Resolves: rhbz#2081425
- Allow insights-client execute its private memfd: objects
Resolves: rhbz#2081425
- Update policy for insights-client to run additional commands 2
Resolves: rhbz#2081425
- Use insights_client_tmp_t instead of insights_client_var_tmp_t
Resolves: rhbz#2081425
- Change space indentation to tab in insights-client
Resolves: rhbz#2081425
- Use socket permissions sets in insights-client
Resolves: rhbz#2081425
- Update policy for insights-client to run additional commands
Resolves: rhbz#2081425
- Allow init_t to rw insights_client unnamed pipe
Resolves: rhbz#2081425
- Fix insights client
Resolves: rhbz#2081425
- Update kernel_read_unix_sysctls() for sysctl_net_unix_t handling
Resolves: rhbz#2081425
- Do not let system_cronjob_t create redhat-access-insights.log with var_log_t
Resolves: rhbz#2081425
- Allow stalld get scheduling policy of kernel threads
Resolves: rhbz#2096776
- Update samba-dcerpcd policy for kerberos usage
Resolves: rhbz#2096521
- Allow winbind_rpcd_t connect to self over a unix_stream_socket
Resolves: rhbz#2096255
- Allow dlm_controld send a null signal to a cluster daemon
Resolves: rhbz#2095884
- Allow dhclient manage pid files used by chronyd
The chronyd_manage_pid_files() interface was added.
- Resolves: rhbz#2094155
Allow install_t nnp_domtrans to setfiles_mac_t
- Resolves: rhbz#2073010
- Allow rabbitmq to use systemd notify
Resolves: rhbz#2056565
- Allow ksmctl create hardware state information files
Resolves: rhbz#2021131
- Label /var/target with targetd_var_t
Resolves: rhbz#2020169
- Allow targetclid read generic SSL certificates
Resolves: rhbz#2020169

* Thu Jun 09 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.34-1
- Allow stalld setsched and sys_nice
Resolves: rhbz#2092864
- Allow rhsmcertd to create cache file in /var/cache/cloud-what
Resolves: rhbz#2092333
- Update policy for samba-dcerpcd
Resolves: rhbz#2083509
- Add support for samba-dcerpcd
Resolves: rhbz#2083509
- Allow rabbitmq to access its private memfd: objects
Resolves: rhbz#2056565
- Confine targetcli
Resolves: rhbz#2020169
- Add policy for wireguard
Resolves: 1964862
- Label /var/cache/insights with insights_client_cache_t
Resolves: rhbz#2062136
- Allow ctdbd nlmsg_read on netlink_tcpdiag_socket
Resolves: rhbz#2094489
- Allow auditd_t noatsecure for a transition to audisp_remote_t
Resolves: rhbz#2081907

* Fri May 27 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.33-1
- Allow insights-client manage gpg admin home content
Resolves: rhbz#2062136
- Add the gpg_manage_admin_home_content() interface
Resolves: rhbz#2062136
- Add rhcd policy
Resolves: bz#1965013
- Allow svirt connectto virtlogd
Resolves: rhbz#2000881
- Add ksm service to ksmtuned
Resolves: rhbz#2021131
- Allow nm-privhelper setsched permission and send system logs
Resolves: rhbz#2053639
- Update the policy for systemd-journal-upload
Resolves: rhbz#2085369
- Allow systemd-journal-upload watch logs and journal
Resolves: rhbz#2085369
- Create a policy for systemd-journal-upload
Resolves: rhbz#2085369
- Allow insights-client create and use unix_dgram_socket
Resolves: rhbz#2087765
- Allow insights-client search gconf homedir
Resolves: rhbz#2087765

* Wed May 11 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.32-1
- Dontaudit guest attempts to dbus chat with systemd domains
Resolves: rhbz#2062740
- Dontaudit guest attempts to dbus chat with system bus types
Resolves: rhbz#2062740
- Fix users for SELinux userspace 3.4
Resolves: rhbz#2079290
- Removed adding to attribute unpriv_userdomain from userdom_unpriv_type template
Resolves: rhbz#2076681
- Allow systemd-sleep get removable devices attributes
Resolves: rhbz#2082404
- Allow systemd-sleep tlp_filetrans_named_content()
Resolves: rhbz#2082404
- Allow systemd-sleep execute generic programs
Resolves: rhbz#2082404
- Allow systemd-sleep execute shell
Resolves: rhbz#2082404
- Allow systemd-sleep transition to sysstat_t
Resolves: rhbz#2082404
- Allow systemd-sleep transition to tlp_t
Resolves: rhbz#2082404
- Allow systemd-sleep transition to unconfined_service_t on bin_t executables
Resolves: rhbz#2082404
- allow systemd-sleep to set timer for suspend-then-hibernate
Resolves: rhbz#2082404
- Add default fc specifications for patterns in /opt
Resolves: rhbz#2081059
- Use a named transition in systemd_hwdb_manage_config()
Resolves: rhbz#2061725

* Wed May 04 2022 Nikola Knazekova <nknazeko@redhat.com> - 34.1.31-2
- Remove "v" from the package version

* Mon May 02 2022 Nikola Knazekova <nknazeko@redhat.com> - v34.1.31-1
- Label /var/run/machine-id as machineid_t
Resolves: rhbz#2061680
- Allow insights-client create_socket_perms for tcp/udp sockets
Resolves: rhbz#2077377
- Allow insights-client read rhnsd config files
Resolves: rhbz#2077377
- Allow rngd drop privileges via setuid/setgid/setcap
Resolves: rhbz#2076642
- Allow tmpreaper the sys_ptrace userns capability
Resolves: rhbz#2062823
- Add stalld to modules.conf
Resolves: rhbz#2042614
- New policy for stalld
Resolves: rhbz#2042614
- Label new utility of NetworkManager nm-priv-helper
Resolves: rhbz#2053639
- Exclude container.if from selinux-policy-devel
Resolves: rhbz#1861968

* Tue Apr 19 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.30-2
- Update source branches to build a new package for RHEL 9.1.0

* Tue Apr 12 2022 Nikola Knazekova <nknazeko@redhat.com> - 34.1.30-1
- Allow administrative users the bpf capability
Resolves: RHBZ#2070982
- Allow NetworkManager talk with unconfined user over unix domain dgram socket
Resolves: rhbz#2064688
- Allow hostapd talk with unconfined user over unix domain dgram socket
Resolves: rhbz#2064688
- Allow fprintd read and write hardware state information
Resolves: rhbz#2062911
- Allow fenced read kerberos key tables
Resolves: RHBZ#2060722
- Allow init watch and watch_reads user ttys
Resolves: rhbz#2060289
- Allow systemd watch and watch_reads console devices
Resolves: rhbz#2060289
- Allow nmap create and use rdma socket
Resolves: RHBZ#2059603

* Thu Mar 31 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.29-1
- Allow qemu-kvm create and use netlink rdma sockets
Resolves: rhbz#2063612
- Label corosync-cfgtool with cluster_exec_t
Resolves: rhbz#2061277

* Thu Mar 24 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.28-1
- Allow logrotate a domain transition to cluster administrative domain
Resolves: rhbz#2061277
- Change the selinuxuser_execstack boolean value to true
Resolves: rhbz#2064274

* Thu Feb 24 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.27-1
- Allow ModemManager connect to the unconfined user domain
Resolves: rhbz#2000196
- Label /dev/wwan.+ with modem_manager_t
Resolves: rhbz#2000196
- Allow systemd-coredump userns capabilities and root mounton
Resolves: rhbz#2057435
- Allow systemd-coredump read and write usermodehelper state
Resolves: rhbz#2057435
- Allow sysadm_passwd_t to relabel passwd and group files
Resolves: rhbz#2053458
- Allow systemd-sysctl read the security state information
Resolves: rhbz#2056999
- Remove unnecessary /etc file transitions for insights-client
Resolves: rhbz#2055823
- Label all content in /var/lib/insights with insights_client_var_lib_t
Resolves: rhbz#2055823
- Update insights-client policy
Resolves: rhbz#2055823
- Update insights-client: fc pattern, motd, writing to etc
Resolves: rhbz#2055823
- Update specfile to buildrequire policycoreutils-devel >= 3.3-5
- Add modules_checksum to %files

* Thu Feb 17 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.26-1
- Remove permissive domain for insights_client_t
Resolves: rhbz#2055823
- New policy for insight-client
Resolves: rhbz#2055823
- Allow confined sysadmin to use tool vipw
Resolves: rhbz#2053458
- Allow chage domtrans to sssd
Resolves: rhbz#2054657
- Remove label for /usr/sbin/bgpd
Resolves: rhbz#2055578
- Dontaudit pkcsslotd sys_admin capability
Resolves: rhbz#2055639
- Do not change selinuxuser_execmod and selinuxuser_execstack
Resolves: rhbz#2055822
- Allow tuned to read rhsmcertd config files
Resolves: rhbz#2055823

* Mon Feb 14 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.25-1
- Allow systemd watch unallocated ttys
Resolves: rhbz#2054150
- Allow alsa bind mixer controls to led triggers
Resolves: rhbz#2049732
- Allow alsactl set group Process ID of a process
Resolves: rhbz#2049732
- Allow unconfined to run virtd bpf
Resolves: rhbz#2033504

* Fri Feb 04 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.24-1
- Allow tumblerd write to session_dbusd tmp socket files
Resolves: rhbz#2000039
- Allow login_userdomain write to session_dbusd tmp socket files
Resolves: rhbz#2000039
- Allow login_userdomain create session_dbusd tmp socket files
Resolves: rhbz#2000039
- Allow gkeyringd_domain write to session_dbusd tmp socket files
Resolves: rhbz#2000039
- Allow systemd-logind delete session_dbusd tmp socket files
Resolves: rhbz#2000039
- Allow gdm-x-session write to session dbus tmp sock files
Resolves: rhbz#2000039
- Allow sysadm_t nnp_domtrans to systemd_tmpfiles_t
Resolves: rhbz#2039453
- Label exFAT utilities at /usr/sbin
Resolves: rhbz#1972225

* Wed Feb 02 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.23-1
- Allow systemd nnp_transition to login_userdomain
Resolves: rhbz#2039453
- Label /var/run/user/%{USERID}/dbus with session_dbusd_tmp_t
Resolves: rhbz#2000039
- Change /run/user/[0-9]+ to /run/user/%{USERID} for proper labeling
Resolves: rhbz#2000039
- Allow scripts to enter LUKS password
Resolves: rhbz#2048521
- Allow system_mail_t read inherited apache system content rw files
Resolves: rhbz#2049372
- Add apache_read_inherited_sys_content_rw_files() interface
Related: rhbz#2049372
- Allow sanlock get attributes of filesystems with extended attributes
Resolves: rhbz#2047811
- Associate stratisd_data_t with device filesystem
Resolves: rhbz#2039974
- Allow init read stratis data symlinks
Resolves: rhbz#2039974
- Label /run/stratisd with stratisd_var_run_t
Resolves: rhbz#2039974
- Allow domtrans to sssd_t and role access to sssd
Resolves: rhbz#2039757
- Creating interface sssd_run_sssd()
Resolves: rhbz#2039757
- Fix badly indented used interfaces
Resolves: rhbz#2039757
- Allow domain transition to sssd_t
Resolves: rhbz#2039757
- Label /dev/nvme-fabrics with fixed_disk_device_t
Resolves: rhbz#2039759
- Allow local_login_t nnp_transition to login_userdomain
Resolves: rhbz#2039453
- Allow xdm_t nnp_transition to login_userdomain
Resolves: rhbz#2039453
- Make cupsd_lpd_t a daemon
Resolves: rhbz#2039449
- Label utilities for exFAT filesystems with fsadm_exec_t
Resolves: rhbz#1972225
- Dontaudit sfcbd sys_ptrace cap_userns
Resolves: rhbz#2040311

* Tue Jan 11 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.22-1
- Allow sshd read filesystem sysctl files
Resolves: rhbz#2036585
- Revert "Allow sshd read sysctl files"
Resolves: rhbz#2036585

* Mon Jan 10 2022 Zdenek Pytela <zpytela@redhat.com> - 34.1.21-1
- Remove the lockdown class from the policy
Resolves: rhbz#2017848
- Revert "define lockdown class and access"
Resolves: rhbz#2017848
- Allow gssproxy access to various system files.
Resolves: rhbz#2026974
- Allow gssproxy read, write, and map ica tmpfs files
Resolves: rhbz#2026974
- Allow gssproxy read and write z90crypt device
Resolves: rhbz#2026974
- Allow sssd_kcm read and write z90crypt device
Resolves: rhbz#2026974
- Allow abrt_domain read and write z90crypt device
Resolves: rhbz#2026974
- Allow NetworkManager read and write z90crypt device
Resolves: rhbz#2026974
- Allow smbcontrol read the network state information
Resolves: rhbz#2038157
- Allow virt_domain map vhost devices
Resolves: rhbz#2035702
- Allow fcoemon request the kernel to load a module
Resolves: rhbz#2034463
- Allow lldpd connect to snmpd with a unix domain stream socket
Resolves: rhbz#2033315
- Allow ModemManager create a qipcrtr socket
Resolves: rhbz#2036582
- Allow ModemManager request to load a kernel module
Resolves: rhbz#2036582
- Allow sshd read sysctl files
Resolves: rhbz#2036585

* Wed Dec 15 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.20-1
- Allow dnsmasq watch /etc/dnsmasq.d directories
Resolves: rhbz#2029866
- Label /usr/lib/pcs/pcs_snmp_agent with cluster_exec_t
Resolves: rhbz#2029316
- Allow lldpd use an snmp subagent over a tcp socket
Resolves: rhbz#2028561
- Allow smbcontrol use additional socket types
Resolves: rhbz#2027751
- Add write permisson to userfaultfd_anon_inode_perms
Resolves: rhbz#2027660
- Allow xdm_t watch generic directories in /lib
Resolves: rhbz#1960010
- Allow xdm_t watch fonts directories
Resolves: rhbz#1960010
- Label /dev/ngXnY and /dev/nvme-subsysX with fixed_disk_device_t
Resolves: rhbz#2027994
- Add hwtracing_device_t type for hardware-level tracing and debugging
Resolves: rhbz#2029392
- Change dev_getattr_infiniband_dev() to use getattr_chr_files_pattern()
Resolves: rhbz#2028791
- Allow arpwatch get attributes of infiniband_device_t devices
Resolves: rhbz#2028791
- Allow tcpdump and nmap get attributes of infiniband_device_t
Resolves: rhbz#2028791

* Mon Nov 29 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.19-1
- Allow redis get attributes of filesystems with extended attributes
Resolves: rhbz#2014611
- Allow dirsrv read slapd tmpfs files
Resolves: rhbz#2015928
- Revert "Label /dev/shm/dirsrv/ with dirsrv_tmpfs_t label"
Resolves: rhbz#2015928
- Allow login_userdomain open/read/map system journal
Resolves: rhbz#2017838
- Allow login_userdomain read and map /var/lib/systemd files
Resolves: rhbz#2017838
- Allow nftables read NetworkManager unnamed pipes
Resolves: rhbz#2023456
- Allow xdm watch generic directories in /var/lib
Resolves: rhbz#1960010
- Allow xdm_t watch generic pid directories
Resolves: rhbz#1960010

* Mon Nov 01 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.18-1
- Allow fetchmail search cgroup directories
Resolves: rhbz#2015118
- Add the auth_read_passwd_file() interface
Resolves: rhbz#2014611
- Allow redis-sentinel execute a notification script
Resolves: rhbz#2014611
- Support new PING_CHECK health checker in keepalived
Resolves: rhbz#2014423

* Thu Oct 14 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.17-1
- Label /usr/sbin/virtproxyd as virtd_exec_t
Resolves: rhbz#2002143
- Allow at-spi-bus-launcher read and map xdm pid files
Resolves: rhbz#2011772
- Remove references to init_watch_path_type attribute
Resolves: rhbz#2007960
- Remove all redundant watch permissions for systemd
Resolves: rhbz#2007960
- Allow systemd watch non_security_file_type dirs, files, lnk_files
Resolves: rhbz#2007960
- Allow systemd-resolved watch /run/systemd
Resolves: rhbz#1992461
- Allow sssd watch /run/systemd
Resolves: rhbz#1992461

* Thu Sep 23 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.16-1
- Allow fprintd install a sleep delay inhibitor
Resolves: rhbz#1999537
- Update mount_manage_pid_files() to use manage_files_pattern
Resolves: rhbz#1999997
- Allow gnome at-spi processes create and use stream sockets
Resolves: rhbz#2004885
- Allow haproxy list the sysfs directories content
Resolves: rhbz#1986823
- Allow virtlogd_t read process state of user domains
Resolves: rhbz#1994592
- Support hitless reloads feature in haproxy
Resolves: rhbz#1997182
- Allow firewalld load kernel modules
Resolves: rhbz#1999152
- Allow communication between at-spi and gdm processes
Resolves: rhbz#2003037
- Remove "ipa = module" from modules-targeted-contrib.conf
Resolves: rhbz#2006039

* Mon Aug 30 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.15-1
- Update ica_filetrans_named_content() with create_file_perms
Resolves: rhbz#1976180
- Allow various domains work with ICA crypto accelerator
Resolves: rhbz#1976180
- Add ica module
Resolves: rhbz#1976180
- Revert "Support using ICA crypto accelerator on s390x arch"
Resolves: rhbz#1976180
- Fix the gnome_atspi_domtrans() interface summary
Resolves: rhbz#1972655
- Add support for at-spi
Resolves: rhbz#1972655
- Add permissions for system dbus processes
Resolves: rhbz#1972655
- Allow /tmp file transition for dbus-daemon also for sock_file
Resolves: rhbz#1972655

* Wed Aug 25 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.14-1
- Support using ICA crypto accelerator on s390x arch
Resolves: rhbz#1976180
- Allow systemd delete /run/systemd/default-hostname
Resolves: rhbz#1978507
- Label /usr/bin/Xwayland with xserver_exec_t
Resolves: rhbz#1993151
- Label /usr/libexec/gdm-runtime-config with xdm_exec_t
Resolves: rhbz#1993151
- Allow tcpdump read system state information in /proc
Resolves: rhbz#1972577
- Allow firewalld drop capabilities
Resolves: rhbz#1989641

* Thu Aug 12 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.13-1
- Add "/" at the beginning of dev/shm/var\.lib\.opencryptoki.* regexp
Resolves: rhbz#1977915
- Set default file context for /sys/firmware/efi/efivars
Resolves: rhbz#1972372
- Allow tcpdump run as a systemd service
Resolves: rhbz#1972577
- Allow nmap create and use netlink generic socket
Resolves: rhbz#1985212
- Allow nscd watch system db files in /var/db
Resolves: rhbz#1989416
- Allow systemd-gpt-auto-generator read udev pid files
Resolves: rhbz#1992638

* Tue Aug 10 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.12-1
- Revert "update libs_filetrans_named_content() to have support for /usr/lib/debug directory"
Resolves: rhbz#1990813
- Label /dev/crypto/nx-gzip with accelerator_device_t
Resolves: rhbz#1973953
- Label /usr/bin/qemu-storage-daemon with virtd_exec_t
Resolves: rhbz#1977245
- Allow systemd-machined stop generic service units
Resolves: rhbz#1979522
- Label /.k5identity file allow read of this file to rpc.gssd
Resolves: rhbz#1980610

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 34.1.11-2
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Thu Jul 29 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.11-1
- Allow hostapd bind UDP sockets to the dhcpd port
Resolves: rhbz#1979968
- Allow mdadm read iscsi pid files
Resolves: rhbz#1976073
- Unconfined domains should not be confined
Resolves: rhbz#1977986
- Allow NetworkManager_t to watch /etc
Resolves: rhbz#1980000
- Allow using opencryptoki for ipsec
Resolves: rhbz#1977915

* Wed Jul 14 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.10-1
- Allow bacula get attributes of cgroup filesystems
Resolves: rhbz#1976917
- Label /dev/wmi/dell-smbios as acpi_device_t
Resolves: rhbz#1972382
- Add the lockdown integrity permission to dev_map_userio_dev()
Resolves: rhbz#1966758
- Allow virtlogd_t to create virt_var_lockd_t dir
Resolves: rhbz#1974875

* Tue Jun 22 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.9-1
- Allow systemd-coredump getattr nsfs files and net_admin capability
Resolves: rhbz#1965372
- Label /run/libvirt/common with virt_common_var_run_t
Resolves: rhbz#1969209
- Label /usr/bin/arping plain file with netutils_exec_t
Resolves: rhbz#1952515
- Make usbmuxd_t a daemon
Resolves: rhbz#1965411
- Allow usbmuxd get attributes of cgroup filesystems
Resolves: rhbz#1965411
- Label /dev/dma_heap/* char devices with dma_device_t
- Revert "Label /dev/dma_heap/* char devices with dma_device_t"
- Revert "Label /dev/dma_heap with dma_device_dir_t"
- Revert "Associate dma_device_dir_t with device filesystem"
Resolves: rhbz#1967818
- Label /var/lib/kdump with kdump_var_lib_t
Resolves: rhbz#1965989
- Allow systemd-timedated watch runtime dir and its parent
Resolves: rhbz#1970865
- Label /run/fsck with fsadm_var_run_t
Resolves: rhbz#1970911

* Thu Jun 10 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.8-1
- Associate dma_device_dir_t with device filesystem
Resolves: rhbz#1954116
- Add default file context specification for dnf log files
Resolves: rhbz#1955223
- Allow using opencryptoki for certmonger
Resolves: rhbz#1961756
- Label var.lib.opencryptoki.* files and create pkcs_tmpfs_filetrans()
Resolves: rhbz#1961756
- Allow httpd_sys_script_t read, write, and map hugetlbfs files
Resolves: rhbz#1964890
- Dontaudit daemon open and read init_t file
Resolves: rhbz#1965412
- Allow sanlock get attributes of cgroup filesystems
Resolves: rhbz#1965217

* Tue Jun 08 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.7-1
- Set default file context for /var/run/systemd instead of /run/systemd
Resolves: rhbz#1966492

* Mon Jun 07 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.6-1
- Label /dev/dma_heap with dma_device_dir_t
Resolves: rhbz#1954116
- Allow pkcs-slotd create and use netlink_kobject_uevent_socket
Resolves: rhbz#1963252
- Label /run/systemd/default-hostname with hostname_etc_t
Resolves: rhbz#1966492

* Thu May 27 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.5-1
- Label /dev/trng with random_device_t
Resolves: rhbz#1962260
- Label /dev/zram[0-9]+ block device files with fixed_disk_device_t
Resolves: rhbz#1954116
- Label /dev/udmabuf character device with dma_device_t
Resolves: rhbz#1954116
- Label /dev/dma_heap/* char devices with dma_device_t
Resolves: rhbz#1954116
- Label /dev/acpi_thermal_rel char device with acpi_device_t
Resolves: rhbz#1954116
- Allow fcoemon create sysfs files
Resolves: rhbz#1952292

* Wed May 12 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.4-1
- Allow sysadm_t dbus chat with tuned
Resolves: rhbz#1953643
- Allow tuned write profile files with file transition
Resolves: rhbz#1953643
- Allow tuned manage perf_events
Resolves: rhbz#1953643
- Make domains use kernel_write_perf_event() and kernel_manage_perf_event()
Resolves: rhbz#1953643
- Add kernel_write_perf_event() and kernel_manage_perf_event()
Resolves: rhbz#1953643
- Allow syslogd_t watch root and var directories
Resolves: rhbz#1957792
- Allow tgtd create and use rdma socket
Resolves: rhbz#1955559
- Allow aide connect to init with a unix socket
Resolves: rhbz#1926343

* Wed Apr 28 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.3-1
- Allow domain create anonymous inodes
Resolves: rhbz#1954145
- Add anon_inode class to the policy
Resolves: rhbz#1954145
- Allow pluto IKEv2 / ESP over TCP
Resolves: rhbz#1951471
- Add brltty new permissions required by new upstream version
Resolves: rhbz#1947842
- Label /var/lib/brltty with brltty_var_lib_t
Resolves: rhbz#1947842
- Allow login_userdomain create cgroup files
Resolves: rhbz#1951114
- Allow aide connect to systemd-userdbd with a unix socket
Resolves: rhbz#1926343
- Allow cups-lpd read its private runtime socket files
Resolves: rhbz#1947397
- Label /etc/redis as redis_conf_t
Resolves: rhbz#1947874
- Add file context specification for /usr/libexec/realmd
Resolves: rhbz#1946495

* Thu Apr 22 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.2-1
- Further update make-rhat-patches.sh for RHEL 9.0 beta
- Add file context specification for /var/tmp/tmp-inst
Resolves: rhbz#1924656

* Wed Apr 21 2021 Zdenek Pytela <zpytela@redhat.com> - 34.1.1-1
- Update selinux-policy.spec and make-rhat-patches.sh for RHEL 9.0 beta
- Allow unconfined_service_t confidentiality and integrity lockdown
Resolves: rhbz#1950267

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 34-2
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937
