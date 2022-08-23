
# Wallbox Power Management

## Motivation

### Charging Station Limitations
Unfortunately, my local electricity provider [SWLB](https://www.swlb.de/) did not approve the installation of a private 22kW charging station (wallbox) onmy property. I was only allowed to draw a maximum power of 11kW from the network, but not 22kW. Since it really makes a difference whether you charge an electric vehicle with 11kW or 22kW I had to find a solution for this.

Mid 2020 I had installed a photovoltaic power system capable of providng a peak power of 9,900 Watts. My idea was to increase the maximum wallbox power dynmacially by the amount of energy produced by the photovoltaic system. For example, when my PV system produces 5,600 Watts I want to allow my the wallbox to charge with 15,600 Watts (11,000 + 5,600) instaed of only 11,000 Watts.

###  The Challenge

By default, my power inverter only supports a few "exotic" wallboxes, like the Keba KeConteact P30, or the eCharge cPH1 Wallbox. Of course, my Vestel wallbox is not on the list of supported ones. Therefore, I decided to start this project to build my own simple power management or balancing device. It's a straight-forward hands-on project which I've realized using a Raspberry Pi Zero W single board computer together with some peripherals.

## Infrastructure

### Photovoltaic System
![Fronius Symo 10.0-3-M](https://raw.githubusercontent.com/zeitinfarkt/wallbox-power-management/main/doc/img/Hanwa-Q-Cells-28.jpg)
My photovoltaic system consists of 28 **Hanwha Q CELLS Q.Peak Duo G6 355Wp** solar modules which can deliver a maximum total peak power of 9,900 Watts.

### The Inverter

My power inverter is a **Fronius Symo 10.0-3-M**. 

| Fronius Symo 10.0-3-M | Description |
|  :---  |  :--  |
| ![Fronius Symo 10.0-3-M](https://raw.githubusercontent.com/zeitinfarkt/wallbox-power-management/main/doc/img/Fronius%20Symo%2010.0-3-M.png) | The transformerless Fronius Symo 10.0-3-M is a 3-phase inverter in the power category of 10kW. It features a Wifi and Ethernet internet connection and makes it easier to integrate third-party components. |

#### Inverter Interfaces

The Fronius inverter features the following communication interfaces:

- WLAN / Ethernet LAN: Fronius Solar.web, Modbus TCP SunSpec, Fronius Solar API (JSON)
- 6 inputs and 4 digital inputs/outputs: Interface to ripple control receiver
- USB (type A socket) 4): Data logging, inverter update via USB flash drive
- 2x RS422 (RJ45 socket): Fronius Solar Net
- Signalling output: Energy management (floating relay output)
- Datalogger and web server: Integrated
- External input: S0 meter connection / Evaluation of overvoltage protection
- RS485: Modbus RTU SunSpec or meter connection

#### Fronius Solar API

The Fronius Solar API was designed to allow 3rd party software to request system data from various Fronius devices (e.g., inverters) providing a well-defined data API and data structures. In this project we read the following JSON reply we would get in respone to the Solari API call "GetPowerFlowRealtimeData"

```json
{
	"Body" : {
		"Inverters" : {
			"1" : {
			"DT" : 232,
			"E_Day" : 20093,
			"E_Total" : 21245430,
			"E_Year" : 8322468,
			"P" : 886
			}
		},
		"Site" : {
		"E_Day" : 20093,
		"E_Total" : 21245430,
		"E_Year" : 8322468,
		"Meter_Location" : "grid",
		"Mode" : "meter",
		"P_Akku" : null,
		"P_Grid" : -308.54000000000002,
		"P_Load" : -577.46000000000004,
		"P_PV" : 886,
		"rel_Autonomy" : 100,
		"rel_SelfConsumption" : 65.176072234762984
	},
	"Version" : "12"
	},
	"Head" : {
		"RequestArguments" : {},
		"Status" : {
		"Code" : 0,
		"Reason" : "",
		"UserMessage" : ""
	},
	"Timestamp" : "2022-08-20T17:22:22+02:00"
	}
}
```
However, we utilize the built-in Fronius Push Service available through the Web Interface (Settings -> Push). We configure our inverter to push the current power flow via FTP Upload (ftp://user@password:raspi0:21:/home/fronius/push/powerFlow.json) to the Raspberry Pi every 10 seconds.

Our application is only interested in the JSOB object **Body/Inverters/1/P** that holds the current power produced by the inverter.

### The Wallbox

| Wallbox| Vestel Wallbox EVC04 AC22|
| :---: | :--- |
| ![Vestel Wallbox EVC04 AC22 ](https://raw.githubusercontent.com/zeitinfarkt/wallbox-power-management/main/doc/img/Vestel-EVC04-AC22.png =250x)| The [Vestel EVC04-AC22-T2P eMobility](https://www.vestel-echarger.com/downloads/VESTEL_EVC04_Produktinformation_HomePlus22kW.pdf) wallbox is a 3-phase electic charger allowing a mximum charging power of 22kW (3 x 32A @ 400V). It includes a 5m 3-phase TYPE 2 charging cable. The wallbox has an integrated DC protection circuit and features RFID card support.

|

Most importantly, the Vestel wallbox supports a **Modbus TCP/RS-485** interface. Apparently, there is also a mobile app for Android and iOS to control the wallbox's charging process,

 
# Hardware

## Raspberry PI

- [Raspberry Pi Zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/), a small single-board computer
- DIN Rail power Supply (e.g. a [MeanWell HDR-15-5 5V/2.4A](https://www.meanwell-web.com/en-gb/ac-dc-ultra-slim-din-rail-power-supply-input-range-hdr--15--5))
- USB to RS-485 Converter (e.g., from [BerryBase ](https://www.berrybase.de/en/usb-rs485-konverter))
- Display: LCD 1.8" color TFT display (e.g., [Waveshare 1.8″](https://www.waveshare.com/wiki/1.8inch_LCD_Module) 160×128 pixels IPS HD LCD Display Modul, SPI Interface)

  

## Display

  

Since I would like to see the status of the entire system I've decided to connect it to a small 1.8" LCD display.

  

#### Color LCD Display

  

| | Waveshare 1.8" LCD Display |
| :--- | :--- |
| ![Waveshare 1.8" LCD Display](https://raw.githubusercontent.com/zeitinfarkt/wallbox-power-management/main/doc/img/1.8inch-lcd-module-1.jpg ) | The Waveshare 1.8" LCD display is connected to the Raspberry Pi using a standard 8-pin SPI cable. The display uses a ST7735 driver chip and support a resolution of 160 by 128 pixels. The driver ship is a ST7735S. The physical module size 57mm by 34mm, the display size is 35mm by 28mm. |

  

#### Pin Connections

 The 1.8inch LCD uses the PH2.0 8PIN interface, which can be connected to the Raspberry Pi according to the table below.![Raspberry Pi Wiring](https://www.waveshare.com/w/upload/f/fa/1.8-rpi.jpg)

| LCD | BCM2835 | Board |
| :---: | :---: | :---: |
| VCC | 3.3V | 3.3V|
| GND | GND | GND |
| DIN | MOSI | 19 |
| CLK | SCLK | 23 |
| CS | CEO | 24 |
| DS | 25 | 22 |
| RST | 27 | 13 |
| BL | 18 | 12 |

  

## Software

### Raspberry Pi

#### System Configuration

Activate the onboard SPI interface of your Raspberry Pi by running raspi-config

  ```´bash
sudo raspi-config
  ```
and select "Interfacing Options" -> "P4 SPI" -> "Yes" to enable the SPI interface.

You need to **reboot** your Raspberry Pi to enable the changes made. Please make sure that no other device occupies the SPI nterface.

#### BCM2835 libraries

You need to install the BCM2835 libraries. Open a terminal on your Raspberry Pi and run the folloging commands:

```bash
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.68.tar.gz
tar zxvf bcm2835-1.68.tar.gz
cd bcm2835-1.68/
sudo ./configure && sudo make && sudo make check && sudo make install
```

For more information refer to their official [website](http://www.airspayce.com/mikem/bcm2835/).

#### wiringPi libraries
  
Open a Raspberry Pi terminal and run the following commands

```bash
sudo apt-get install wiringpi
```
or a install manually :

```bash
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
```
Run the command

```bash
gpio -v
```
You should see the version number **2.52**. Otherwise your installation did not succeed.
We need to install the Bullseye branch system running the following command:

```bash
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
gpio -v
```
You should see the version number **2.60**. Otherwise your installation did not succeed.

### Python Modules
 
#### LCD Module

You need to install the following python modules to drive the Waveshare LCD display through the Raspberry's SPI interface

```bash
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install RPi.GPIO
sudo pip3 install spidev```

#### Application

The application requires the following Python packages to be installed:

```bash
sudo pip3 install requests
sudo pip3 install python3-pil
sudo pip3 install pillow
sudo pip3 install simple-namespace
sudo pip3 install pytz
```
