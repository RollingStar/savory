#!/bin/sh

_FUNCTIONS=/etc/rc.d/functions
[ -f ${_FUNCTIONS} ] && . ${_FUNCTIONS}

. /etc/sysconfig/mntus

rm -f ${MNTUS_MP}/update*.bin

display_update_screen_success

sync
sleep 10

/sbin/reboot

return 0

