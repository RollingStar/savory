#!/bin/sh

_FUNCTIONS=/etc/rc.d/functions
[ -f ${_FUNCTIONS} ] && . ${_FUNCTIONS}

. /etc/sysconfig/mntus

VERSION_FILE=/etc/prettyversion.txt
SAVE_PRETTY=${VERSION_FILE}-beforesavory
NF_INI=/opt/amazon/ebook/config/netfront.ini
SAVE_NF_INI=${NF_INI}-beforesavory
SAVORYCTL=/etc/init.d/savoryctl

# If savory is already there, bail out
if [ ! -f $SAVORYCTL ]; then
    update_progressbar 90
    return 0
fi

rm -f $SAVORYCTL 
rm -f /etc/rc5.d/S99savoryctl

update_progressbar 50

if [ -f $SAVE_NF_INI ]; then
    cp $SAVE_NF_INI $NF_INI
fi

update_progressbar 60

if [ -f $SAVE_PRETTY ]; then
    cp $SAVE_PRETTY $VERSION_FILE
fi
update_progressbar 100

return 0


