#!/bin/sh
type getarg > /dev/null 2>&1 || . /lib/dracut-lib.sh

# If SELinux is disabled exit now
getarg "selinux=0" > /dev/null && return 0

SELINUX="enforcing"
# shellcheck disable=SC1090
[ -e "$NEWROOT/etc/selinux/config" ] && . "$NEWROOT/etc/selinux/config"
[ "$SELINUX" == "disabled" ] && return 0

getargbool 0 rd.live.overlay.overlayfs && overlayfs="yes"

if [ -n "$overlayfs" ]; then
    [ -e /sysroot ] && chcon -t root_t /sysroot
    [ -e /run/overlayfs ] && chcon -t root_t /run/overlayfs
    [ -e /run/ovlwork ] && chcon -t root_t /run/ovlwork
fi
