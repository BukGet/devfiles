#!/bin/bash
# Application Server Creation Script
# ----------------------------------
# This script will configure and startup the current application server template,
# update the template to current, then restart the template in preperation for
# insertion into the environment.

VEID=$1
HOSTBOX=$(hostname | cut -d "." -f 1)

vzctl create ${VEID} --ostemplate bukget-api --config basic
vzctl set ${VEID} --save --onboot yes
vzctl set ${VEID} --save --hostname ${HOSTBOX}app${VEID}.bukget.org
vzctl set ${VEID} --save --ipadd 192.168.0.${VEID}
vzctl set ${VEID} --save --nameserver 8.8.8.8 --nameserver 8.8.4.4
vzctl set ${VEID} --save --ram 3G --swap 1G
vzctl set ${VEID} --save --dcachesize 66636812:103449560
vzctl set ${VEID} --save --privvmpages 524288:524288
vzctl set ${VEID} --save --tcprcvbuf 40000000:40000000
vzctl set ${VEID} --save --tcpsndbuf 4000000:4000000
vzctl set ${VEID} --save --numtcpsock 1000:1000
vzctl set ${VEID} --save --oomguarpages 262144
vzctl set ${VEID} --save --kmemsize 31457280:34603008
vzctl start ${VEID}
vzctl exec ${VEID} sed -i "s/database_host = localhost/database_host = ${HOSTBOX}.vpn.bukget.org" /etc/bukget/api.conf
vzctl exec ${VEID} initctl stop bukget
vzctl exec ${VEID} initctl start bukget