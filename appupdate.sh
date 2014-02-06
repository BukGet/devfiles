#!/bin/bash
# App Server Update Script
# ------------------------
# This script will update the application servers on the host to current, restarting them
# along the way.

HOSTBOX=$(hostname | cut -d "." -f 1)

for veid in $(vzlist -Ho veid | tr -d " ");do
	vzctl exec ${VEID} initctl stop bukget
	vzctl exec ${VEID} git -C /opt/api pull
	vzctl exec ${VEID} pip install --upgrade /opt/api
	vzctl exec ${VEID} sed -i "s/database_host = localhost/database_host = ${HOSTBOX}.vpn.bukget.org" /etc/bukget/api.conf
	vzctl exec ${VEID} initctl start bukget
done