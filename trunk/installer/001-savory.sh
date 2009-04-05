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
if [ -f $SAVORYCTL ]; then
    update_progressbar 90
    return 0
fi


update_progressbar 20 

cp savoryctl $SAVORYCTL
chown root.root $SAVORYCTL
chmod 755 $SAVORYCTL
ln -s $SAVORYCTL /etc/rc5.d/S99savoryctl

update_progressbar 50


if [ -f $NF_INI ]; then
    cp $NF_INI $SAVE_NF_INI
    sed 's/dlexts=prc mobi txt azw$/dlexts=prc mobi txt azw epub lrf lit pdf fb2 odt/' $SAVE_NF_INI > /tmp/netfront-temp
    sed 's/dlmimes=application\/x-mobipocket-ebook text\/x-prc$/dlmimes=application\/x-mobipocket-ebook text\/x-prc application\/pdf/' /tmp/netfront-temp > /tmp/netfront-temp-2

    if [ -s /tmp/netfront-temp-2 ]; then
        cp /tmp/netfront-temp-2 $NF_INI
    fi

fi

update_progressbar 60


cp $VERSION_FILE $SAVE_PRETTY
sed 's/$/ UNSUPPORTED SAVORY-0.06/' $SAVE_PRETTY > $VERSION_FILE

update_progressbar 100

return 0


