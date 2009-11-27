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

update_progressbar 20 

if [ -f $SAVORYCTL ]; then
    rm -f $SAVORYCTL
fi
cp savoryctl $SAVORYCTL
chown root:root $SAVORYCTL
chmod 755 $SAVORYCTL

rm -f $SAVORYLNK
ln -s $SAVORYCTL $SAVORYLNK

update_progressbar 50

if [ -f $NF_INI ]; then
    VAR=$(grep -e '^dlexts=' $NF_INI)
    VAR2=$(echo $VAR | sed -r 's: ?epub lrf lit pdf fb2 odt::g' | sed -r 's:$: epub lrf lit pdf fb2 odt:g')
    sed -i -r "s:$VAR:$VAR2:g" $NF_INI

    VAR=$(grep -e '^dlmimes=' $NF_INI)
    VAR2=$(echo $VAR | sed -r 's: ?application/pdf::g' | sed -r 's:$: application/pdf:g')
    sed -i -r "s:$VAR:$VAR2:g" $NF_INI
fi

update_progressbar 60

if [ -f $VERSION_FILE ]; then
#Remove older style version name, and update version number
    sed -i -r 's/ UNSUPPORTED SAVORY-0.[0-9]+//g' $VERSION_FILE
    sed -i -r 's/( +\+ Savory [0-9]\.[0-9]\.[0-9]|$)/ \+ Savory 0.0.8/' $VERSION_FILE
fi

update_progressbar 100

return 0
