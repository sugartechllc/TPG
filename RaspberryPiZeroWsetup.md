# Raspberry Pi Zero W

## Raspbian install
This worked perfectly:
https://www.losant.com/blog/getting-started-with-the-raspberry-pi-zero-w-without-a-monitor

## Extras
```
ssh pi@raspberrypi.local (raspberry)
# sudo -i
# echo <new_hostname> > /etc/hostname
# sudo apt-get update && sudo apt-get upgrade -y
# apt-get install -y git
# apt-get install -y python3-pip
# apt-get install -y minicom
# pip3 install requests
# pip3 install pyserial
# exit
```

## Source code
The following is for wxflowtochords. Modify appropriately for tpg.
```
> git clone —recursive  https://gitHub.com/sugartechllc/WxflowToChords.git
> cd WxflowToChords
> <create wx.json>
> WxflowToChords wx.json
```

To update source code, must update submodules as well
```
> cd WxflowToChords
> git submodule update --remote pychords
> git pull
```

## Services
To setup service, so that process will run at boot:
```
# sudo -i
# cd /etc/systemd/system
# ln -s /home/pi/WxflowToChords/linux/wxflowtochords.service
# systemctl daemon-reload  —full
# systemctl enable wxflowtochords
# systemctl start wxflowtochords
# journalctl -u wxflowtochords -f
# exit
```

## I2C
```
sudo apt-get install i2c-tools libi2c-dev python-smbus
nano /etc/modprobe.d/raspi-blacklist.conf
```

Add the following to /etc/modules:
```
i2c-dev
i2c-bcm2708
```

The following will enumerate devices on the bus:
```
i2cdetect -y 1
```

Add the following to /boot/config.txt:
```
# Enable I2C
dtparam=i2c_arm=on
dtparam=i2cl=on
```

## SMBUS
Setup smbus
```
pip3 install smbus
pip3 install python3-smbus
```

## INA219
Use this python library: https://github.com/chrisb2/pi_ina219. Install with:
```
sudo pip3 uninstall pi-ina219
sudo pip3 install pi-ina219
```

Then use his example code (may need to fix print statements for pyton3)

## BME280
Use the Adafruit python library, as described here: https://github.com/adafruit/Adafruit_Python_BME280. You may need to edit the print statements in the examples for python3.

```
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
cd Adafruit_Python_GPIO
sudo cd …
cd ..
git clone https://github.com/adafruit/Adafruit_Python_BME280.git
cd. Adafruit_Python_BME280
sudo python3 setup.py install
python3 Adafruit_Python_BME280/Adafruit_BME280_Example.py
```

## WiFi
Configure/monitor wireless using wpa_client:
```
# pi@raspberrypi:~/WxflowToChords $ wpa_cli -i wlan0
wpa_cli v2.4
Copyright (c) 2004-2015, Jouni Malinen <j@w1.fi> and contributors
This software may be distributed under the terms of the BSD license.
See README for more details.
Interactive mode
> scan
OK
<3>CTRL-EVENT-SCAN-STARTED 
<3>CTRL-EVENT-SCAN-RESULTS 
> scan_results 
bssid / frequency / signal level / flags / ssid
0a:a1:51:9e:fe:a8	2417	-68	[WPA2-PSK-CCMP][WPS][ESS]	Cave
04:bf:6d:30:78:63	2437	-82	[WPA-PSK-CCMP+TKIP][WPA2-PSK-CCMP+TKIP][WPS][ESS]	CenturyLink9841
e0:91:f5:02:5f:e9	2417	-84	[WPA2-PSK-CCMP][WPS][ESS]	Hobby
28:c6:8e:76:5b:70	2417	-88	[WPA2-PSK-CCMP][WPS][ESS]	Kitchen
48:f8:b3:69:de:56	2442	-94	[WPA-PSK-TKIP][WPA2-PSK-CCMP][WPS][ESS]	Lost Angel Linksys
be:51:0c:1b:46:56	2462	-40	[IBSS]	SonicAdHoc
00:27:22:3e:68:e1	2462	-73	[ESS]	MRIC-Labelle-11b-1
> 
```

To setup network choices, place this file in boot/wpa_supplicant.conf (if boot card is mounted on iMac) or in /etc/wpa_suplicant/wpa_supplicant.conf. The system will connect to 5he network with the strongest signal. Edit the psk keys.

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
network={
	ssid="Hobby"
	psk=“XXXXXXXX”
	key_mgmt=WPA-PSK
}
network={
	ssid="Kitchen"
	psk="XXXXXXXX"
	key_mgmt=WPA-PSK
}
network={
	ssid="Cave"
	psk="XXXXXXXX"
	key_mgmt=WPA-PSK
}
```
