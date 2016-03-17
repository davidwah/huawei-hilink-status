# Huawei AT commands

*Tested with E3131, E3232 & E353

These Huawei USB modems can opperate in several modes

```html
<h2 id="DeviceFunctions">Device Functions</h2>
<table class="wiki">
<tr><td> <strong>Function</strong> </td><td> <strong>Vendor</strong> </td><td> <strong>Product</strong> </td><td> <strong>Description</strong> </td><td> <strong>Command</strong> </td><td> <strong>Comments</strong>
</td></tr><tr><td> 0 </td><td> 12D1 </td><td> 1F01 </td><td> USB Mass Storage </td><td> </td><td> Virtual CD-ROM image emulator containing device drivers for Microsoft Windows,Apple Mac OSX, and Linux
</td></tr><tr><td> 1 </td><td> 12D1 </td><td> 14DB </td><td> CDC Ethernet </td><td> </td><td> Embedded VXWORKS OS with web-server (HiLink mode)
</td></tr><tr><td> </td><td> 12D1 </td><td> 14DC </td><td> CDC Ethernet + SD Storage </td><td> </td><td> Embedded VXWORKS OS with web-server. (HiLink mode)
</td></tr><tr><td> 2 </td><td> 12D1 </td><td> </td><td> Serial modem </td><td> </td><td> Presents 2 serial ports (one for control, one for data).
</td></tr><tr><td> 3 </td><td> 12D1 </td><td> 1442 </td><td> CDC Ethernet + 2x serial ports </td><td> http://192.168.1.1/html/switchProjectMode.html </td><td> <tt>DEVICE_MODE_PROJECT_MODE=0. Called when in HiLink mode.</tt>
</td></tr><tr><td> 4 </td><td> 12D1 </td><td> 1441 </td><td> CDC Ethernet + SD Storage + 3x serial ports </td><td> http://192.168.1.1/html/switchDebugMode.html </td><td> <tt>DEVICE_MODE_DEBUG_MODE = 1. Called when in HiLink mode. Presents 3 serial ports. port 2 == AT commands, port 3 == QXWORKS OS diagnostic C shell.</tt>
</td></tr></table>
```

[Source](http://tjworld.net/wiki/Huawei/E3131UsbHspa)

We usually want to opperate in Hi-Link mode `14DB`. However there maybe a time when we need more control over the modem and require AT commands.

## Switch from Hi-Link to Debug Mode

http://192.168.1.1/html/switchDebugMode.html

`dmesg` should now show three serial ports

```
ttyUSB1 - serial modem
ttyUSB2 - AT commands
ttyUSB3 - QXWORKS OS diagnostic C shell
```

We can now connect via mincom

    sudo minicom -D /dev/ttyUSB1 -b9600
    
`at` should return `OK`

To switch back to Hi-Link mode enter

```
AT^U2DIAG=119
AT+CFUN=4
AT+CFUN=6
```
Each command should return `OK`

[Source](https://www.riecktron.co.za/en/information/55)