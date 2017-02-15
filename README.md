Huawei-HiLink
===================

Setup Huawei-HiLink USB modem to work on a RaspberryPi and view it's status 

# Huawei Hi-Link 3G Modem Raspberry Pi Setup 

**Tested with  Huawei E3231 and E3131**

\* **Caution:** the E3131 comes in several different hardware variant, make sure your hardware can support **Hi-Link** mode.

## Setup power supply 

If using a newer Raspberry Pi (B+,2 or 3) the Pi should be able to power the USB modem direclty without a y-cable ot usb hub if max power mode is tured on. Ensure a decent 2A PSU is used:

    sudo nano /boot/config.txt

Add the following at bottom of file then save and reboot:

    max_usb_current=1
    
For more info on what this does see [forum post](https://www.raspberrypi.org/forums/viewtopic.php?f=29&t=100244) 
    

1) Install sg3-utils:

    sudo apt-get install sg3-utils

2) Change Huawei Hi-Link USB  mode

`$ lsusb` will probably return `12d1:1f01 Huawei Technologies Co., Ltd.` this is mass storage mode. We need Hi-Link USB modem mode. To switch modes enter command: 

    sudo /usr/bin/sg_raw /dev/sr0 11 06 20 00 00 00 00 00 01 00
    
`$ lsusb` should now return `12d1:14db Huawei Technologies Co., Ltd.`

[See here](http://tjworld.net/wiki/Huawei/E3131UsbHspa) for more information on Huawei USB modes and AT commands. 

3) Set USB mode at boot

To ensure correct USB mode is set on each boot, create the following file:

    sudo nano /etc/udev/rules.d/10-Huawei.rules

copy and paste this line in to it.

    SUBSYSTEMS=="usb", ATTRS{modalias}=="usb:v12D1p1F01*", SYMLINK+="hwcdrom", RUN+="/usr/bin/sg_raw /dev/hwcdrom 11 06 20 00 00 00 00 00 01 00"

Open the network interfaces file to edit:

    sudo nano /etc/network/interfaces

and add the following lines:

    allow-hotplug eth1
    iface eth1 inet dhcp

Now try and start the interface 

    sudo ifup eth1 

`ifconfig` should now show that `eth` is connected to gateway `192.168.1.1`. This is the default IP of the Hi-Link modem. If the gateway of `eth0` (your router) is also this same IP this will cause and issue for testing. 

You may need to reboot the Pi. 



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

