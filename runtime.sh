set -x

# THE FOLLOWING VARIABLES MUST BE DEFINED
#KICKSTART_IP="192.168.86.65"
#SERVER_ROOT_IP="192.168.86
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

# Get packages
apt update
apt install -y nfs-kernel-server rpcbind dnsmasq kpartx unzip tar xz-utils

# Setup reference image
wget https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip
unzip 2021-05-07-raspios-buster-armhf-lite.zip
rm 2021-05-07-raspios-buster-armhf-lite.zip
mkdir /imgs
mv *.img /imgs/rpi.img
cd /imgs
kpartx -a -v *.img
ls /dev/mapper
A=$(ls /dev/mapper/loop*p1)
ROOT=${A: 12:-2}
mkdir {bootmnt,rootmnt}
mount /dev/mapper/${ROOT}p1 bootmnt/
mount /dev/mapper/${ROOT}p2 rootmnt/

# Create NFS share and TFTP boot share
# For /etc/dnsmasq.conf the line port 0 if removed if the DHCP and TFTP server are the same
mkdir -p /srv/tftpboot
mkdir -p /srv/nfs/rpi4
cp -a rootmnt/* /srv/nfs/rpi4
cp -a bootmnt/* /srv/nfs/rpi4/boot/
touch /srv/nfs/rpi4/boot/ssh
sed -i /UUID/d /srv/nfs/rpi4/etc/fstab
echo "/srv/nfs/rpi4 *(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports
set -x

SERVER_BC_IP=${SERVER_ROOT_IP}.255

cat > /etc/dnsmasq.conf << EOF
port 0
dhcp-range=${SERVER_BC_IP},proxy
log-dhcp
enable-tftp
tftp-root=/srv/tftpboot
pxe-service=0,"Raspberry Pi Boot"
EOF
echo "console=serial0,115200 console=tty root=/dev/nfs nfsroot=${KICKSTART_IP}:/srv/nfs/rpi4,vers=3 rw ip=dhcp rootwait elevator=deadline" > /srv/nfs/rpi4/boot/cmdline.txt

# Create Kuiper image post boot which will be written to SD card
wget http://swdownloads.analog.com/cse/kuiper/2021-02-23-ADI-Kuiper.img.xz
unxz 2021-02-23-ADI-Kuiper.img.xz
mkdir /srv/nfs/img
mv 2021-02-23-ADI-Kuiper.img /srv/nfs/img/
echo "/srv/nfs/img *(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports

# Add script for post boot
wget https://gist.githubusercontent.com/tfcollins/55ea3b1e3ef19ffc45bd2d6fc3398a93/raw/3f6393cefccbba8b0bb5b2b18845d6405262d0a7/write_sd_remote.py
mv write_sd_remote.py /srv/nfs/rpi4/home/pi/
echo "echo raspberry | sudo -S python3 /home/pi/write_sd.py" >> /srv/nfs/rpi4/home/pi/.bashrc

# Enable autologin (I Think this works?)
mkdir -p /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d
echo "[Service]" > /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d/autologin.conf
echo "ExecStart=" >> /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d/autologin.conf
echo "ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM" >> /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d/autologin.conf

echo "[Service]" > /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d/noclear.conf
echo "TTYVTDisallocate=no" >> /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d/noclear.conf

# Enable all services
service rpcbind start
service rpcbind start
service nfs-server start
service dnsmasq start

# Start up API server
uvicorn borg.main:app --reload --host 0.0.0.0 --port 6000

