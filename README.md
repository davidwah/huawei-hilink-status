huawei-hilink-status
===================

Unsophisticated Python command-line utility to show device information and the connection status from Huawei HiLink modems.

# Huawei Hi-Link 3G Modem RasPi Setup 

I followed the techmind guide which worked well with the Huawei e3231 which operates as a 'HiLink' modem: [http://www.techmind.org/rpi](http://www.techmind.org/rpi)

The main steps in the event that the techmind guide is not available are:

1) Install sg3-utils:

    sudo apt-get install sg3-utils

2) After restarting the raspberrypi, the usb dongle will likely need to be placed in the correct mode:

    sudo /usr/bin/sg_raw /dev/sr0 11 06 20 00 00 00 00 00 01 00

3) To automate this step so that the pi always boots up into the correct mode.

Create the following file:

    sudo nano /etc/udev/rules.d/10-Huawei.rules

copy and paste this line in to it.

    SUBSYSTEMS=="usb", ATTRS{modalias}=="usb:v12D1p1F01*", SYMLINK+="hwcdrom", RUN+="/usr/bin/sg_raw /dev/hwcdrom 11 06 20 00 00 00 00 00 01 00"

Open the network interfaces file to edit:

    sudo nano /etc/network/interfaces

and add the following lines:

    allow-hotplug eth1
    iface eth1 inet dhcp

Complete the setup by rebooting the pi:

    sudo reboot

_For debugging: typing the command lsusb is useful, the Huawei Technologies entry should be in mode: 12d1:14db not 12d1:1f01_

# Status Utility Installation
The utility uses the xmltodict module which can be installed using ```pip```:
```
apt-get install python-pip
pip install xmltodict
pip install requests
```

## Usage example

```
$ python ./hstatus.py
Huawei E3276 LTE Modem (IMEI: 861711012616361)
  Hardware version: CH2F4276GM
  Software version: 22.250.04.00.186
  Serial: B3A3TC2313833197
  MAC address (modem): 00:0D:87:22:34:AC
  Connection status: Connected
    Network type: W-CDMA (3G)
    Signal level: ***** (92%)
    Roaming: Enabled
    Modem WAN IP address: 10.197.32.60
    Public IP address: 32.131.81.221
    DNS IP addresses: 212.113.0.4, 66.28.0.61
    Network operator: Swisscom
    Connected for: 00:49:33 (hh:mm:ss)
    Downloaded: 737.0 KB
    Uploaded: 178.0 KB
  Total downloaded: 47.69 MB
  Total uploaded: 19.86 MB
```

