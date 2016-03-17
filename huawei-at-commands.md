# Huawei AT commands

*Tested with E3131, E3232 & E353

These Huawei USB modems can opperate in several modes

```html
| **Function** | **Vendor** | **Product** | **Description** | **Command** | **Comments** |
| 0 | 12D1 | 1F01 | USB Mass Storage | Virtual CD-ROM image emulator containing device drivers for Microsoft Windows,Apple Mac OSX, and Linux |
| 1 | 12D1 | 14DB | CDC Ethernet | Embedded VXWORKS OS with web-server (HiLink mode) |
 12D1 | 14DC | CDC Ethernet + SD Storage | Embedded VXWORKS OS with web-server. (HiLink mode) |
| 2 | 12D1 | Serial modem | Presents 2 serial ports (one for control, one for data). |
| 3 | 12D1 | 1442 | CDC Ethernet + 2x serial ports | http://192.168.1.1/html/switchProjectMode.html | <tt>DEVICE_MODE_PROJECT_MODE=0\. Called when in HiLink mode.</tt> |
| 4 | 12D1 | 1441 | CDC Ethernet + SD Storage + 3x serial ports | http://192.168.1.1/html/switchDebugMode.html | <tt>DEVICE_MODE_DEBUG_MODE = 1\. Called when in HiLink mode. Presents 3 serial ports. port 2 == AT commands, port 3 == QXWORKS OS diagnostic C shell.</tt> |
```

[Source](http://tjworld.net/wiki/Huawei/E3131UsbHspa)

We usually want to opperate in Hi-Link mode `14DB`. However there maybe a time when we need more control over the modem and require AT commands.

## Switch from Hi-Link to Debug Mode

Browse to:

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