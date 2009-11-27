#!/bin/sh

_FUNCTIONS=/etc/rc.d/functions
[ -f ${_FUNCTIONS} ] && . ${_FUNCTIONS}

. /etc/sysconfig/mntus

VERSION_FILE=/etc/prettyversion.txt
NF_INI=/opt/amazon/ebook/config/netfront.ini
SAVORYCTL=/etc/init.d/savoryctl
SAVORYLNK=/etc/rc5.d/S99savoryctl

#Remove previous version backup files
SAVE_NF_INI=${NF_INI}-beforesavory
SAVE_PRETTY=${VERSION_FILE}-beforesavory
rm -f $SAVE_PRETTY
rm -f $SAVE_NF_INI

if [ -f $SAVORYCTL ]; then
    rm -f $SAVORYCTL 
fi
rm -f /etc/rc5.d/S99savoryctl

update_progressbar 20

if [ -f $NF_INI ]; then
    VAR=$(grep -e '^dlexts=' $NF_INI)
    VAR2=$(echo $VAR | sed -r -e 's: ?epub lrf lit pdf fb2 odt::g')
    sed -i -r -e "s:$VAR:$VAR2:g" $NF_INI

    VAR=$(grep -e '^dlmimes=' $NF_INI)
    VAR2=$(echo $VAR | sed -r -e 's: ?application/pdf::g')
    sed -i -r -e "s:$VAR:$VAR2:g" $NF_INI

    # Special case for Savory 0.06
    sed -i -r -e "s:dlmimes=application/x-mobipocket-ebook text/x-prc ?application/pdf:dlmimes=application/x-mobipocket-ebook text/x-prc:g" $NF_INI

fi

update_progressbar 60

if [ -f $VERSION_FILE ]; then
    sed -i -r -e 's/ UNSUPPORTED SAVORY-0.[0-9]+//g' $VERSION_FILE
    sed -i -r -e 's/( +\+ Savory [0-9]\.[0-9]\.[0-9]|$)//g' $VERSION_FILE
fi

update_progressbar 100

return 0
