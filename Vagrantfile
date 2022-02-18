# -*- mode: ruby -*-
# vi: set ft=ruby :

#TODO: Set these parameters as an environment variable
KICKSTART_IP="192.168.10.10"
SERVER_ROOT_IP="192.168.10"
DEFAULT_INTERFACE="eno1"

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.hostname = "borg"
  config.vm.define "borg-vm"

  # Set VM name in Virtualbox
  config.vm.provider "virtualbox" do |v|
    v.name = "borg-vm"
    v.memory = 2048
  end
  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  config.vm.network "public_network", ip: KICKSTART_IP, bridge: DEFAULT_INTERFACE

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #

  config.vm.provision "file", source: "borg", destination: "$HOME/borg"
  config.vm.provision "file", source: "supervisor.conf", destination: "$HOME/supervisor.conf"


  config.vm.provision "shell", env: {"KICKSTART_IP"=> KICKSTART_IP, "SERVER_ROOT_IP"=>SERVER_ROOT_IP}, inline: <<-SHELL
    # mkdir borg
    # mv * borg/
    # ls
    ls borg/
    apt-get update
    apt-get install -y nfs-server nfs-common nfs-client dnsmasq kpartx unzip tar xz-utils
    # Set up shares
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

    SERVER_BC_IP=${SERVER_ROOT_IP}.255

    echo "port=0" >> /etc/dnsmasq.conf
    echo "dhcp-range=${SERVER_BC_IP},proxy" >> /etc/dnsmasq.conf
    echo "log-dhcp" >> /etc/dnsmasq.conf
    echo "enable-tftp" >> /etc/dnsmasq.conf
    echo "tftp-root=/srv/tftpboot" >> /etc/dnsmasq.conf
    echo 'pxe-service=0,"Raspberry Pi Boot"' >> /etc/dnsmasq.conf
    
    echo "console=serial0,115200 console=tty root=/dev/nfs nfsroot=${KICKSTART_IP}:/srv/nfs/rpi4,vers=3 rw ip=dhcp rootwait elevator=deadline" > /srv/nfs/rpi4/boot/cmdline.txt

    # Create Kuiper image post boot which will be written to SD card
    wget http://swdownloads.analog.com/cse/kuiper/2021-02-23-ADI-Kuiper.img.xz
    unxz 2021-02-23-ADI-Kuiper.img.xz
    mkdir /srv/nfs/img
    mv 2021-02-23-ADI-Kuiper.img /srv/nfs/img/
    echo "/srv/nfs/img *(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports

    # Add script for post boot
    wget https://gist.githubusercontent.com/tfcollins/55ea3b1e3ef19ffc45bd2d6fc3398a93/raw/3f6393cefccbba8b0bb5b2b18845d6405262d0a7/write_sd_remote.py
    #### make some correction to the script ####
    sed -i "s/192.168.86.44/${KICKSTART_IP}/g" write_sd_remote.py
    sed -i "s/imgs/img/g" write_sd_remote.py
    mv write_sd_remote.py /srv/nfs/rpi4/home/pi/ 
    #### make some correction to the script ####
    # echo "echo raspberry | sudo -S python3 /home/pi/write_sd_remote.py" >> /srv/nfs/rpi4/home/pi/.bashrc

    # # Enable autologin (I Think this works?)
    # mkdir -p /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d
    # echo "[Service]" > /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d/autologin.conf
    # # echo "ExecStart=" >> /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d/autologin.conf
    # echo "ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM" >> /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d/autologin.conf

    # echo "[Service]" > /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d/noclear.conf
    # echo "TTYVTDisallocate=no" >> /srv/nfs/rpi4/etc/systemd/system/getty@tty1.service.d/noclear.conf

    # Enable and start all services
    systemctl enable dnsmasq
    systemctl enable rpcbind
    systemctl enable nfs-server
    systemctl start dnsmasq
    systemctl start rpcbind
    systemctl start nfs-server

    # Start up API server
    apt-get install -y python3-pip
    pip3 install fastapi uvicorn pickledb
    # uvicorn borg.main:app --reload --host 0.0.0.0 --port 6000

    # Install and configure supervisord to manage the borg service
    apt-get install supervisor
    service supervisor restart
    cp /home/vagrant/supervisor.conf /etc/supervisor/conf.d/borg.conf
    supervisorctl reread
    supervisorctl update
    supervisorctl status borg
  SHELL

end
