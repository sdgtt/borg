#!/bin/bash
if [ -z "$KICKSTART_IP" ]
then
      echo "ERROR: KICKSTART_IP is not defined"
      exit 1
fi
if [ -z "$SERVER_ROOT_IP" ]
then
      echo "ERROR: SERVER_ROOT_IP is not defined"
      exit 1
fi

# NFS must be setup on host first
apt install -y nfs-kernel-server
service nfs-kernel-server start
modeprobe nfs
mkdir -p /srv

# Build container
docker build -t borg .

# Run with necessary arguments and info
docker run  -v /srv:/srv -e KICKSTART_IP="$KICKSTART_IP"  -e SERVER_ROOT_IP="$SERVER_ROOT" --init --privileged --name borg1 -p 6000:6000 -p 111:111 -p 2049:2049 -p 1048:1048 -p 69:69 borg
