
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
| ![Vestel Wallbox EVC04 AC22](https://raw.githubusercontent.com/zeitinfarkt/wallbox-power-management/main/doc/img/Vestel-EVC04-AC22.png =250x)| The [Vestel EVC04-AC22-T2P eMobility](https://www.vestel-echarger.com/downloads/VESTEL_EVC04_Produktinformation_HomePlus22kW.pdf) wallbox is a 3-phase electic charger allowing a mximum charging power of 22kW (3 x 32A @ 400V). It includes a 5m 3-phase TYPE 2 charging cable. The wallbox has an integrated DC protection circuit and features RFID card support.

Most importantly, the Vestel wallbox supports a **Modbus TCP/RS-485** interface. Apparently, there is also a mobile app for Android and iOS to control the wallbox's charging process,

#### Modbus TPC/IP
The Vestel EVC04 charging station acts as a slave device in a Modbus TCP/IPnetwork.
The charging station needs to be in the same network as the master device, or a proper routing rule has been applied. The router needs to assign a unique IP address to each charging station. The Modbus TCP communication port number for Vestel EVC04 charging station is **502**, the Modbus Unit ID is **255**. There can be only one active Modbus master connection at any time.

The Modbus cables need to be connected like this:

| Cable | Cable Color | Decription |
| :--- | :--- | :--- |
| 6 (CN20-2)| white - blue | A (COM) |
| 5 (CN20-1)| blue | B (COM) |

![Vestel Wallbox EVC04 AC22](https://raw.githubusercontent.com/zeitinfarkt/wallbox-power-management/main/doc/img/Vestel-Modbus-Connector.jpg)

https://www.raspberry-pi-geek.de/ausgaben/rpg/2022/06/modbus-rtu-komponenten-per-io-broker-einbinden/

#### Slave Register Map

The following table shows the Modbux registers of the Verstel EVC04 charging station.

| Key | Register Address | Number of Registers | R/W | Data Type | Description | Unit |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| Serial Number | [100,124] | 25 | R | String | Serial Number, Currently 16 Digit | |
| Chargepoint ID | [130,179] | 50 | R | String | Chargepoint ID |  |
| Brand | [190,199] | 10 | R | String | Chargepoint Brand |  |
| Model | [210,214] | 5 | R | String | Chargepoint Model |  |
| Firmware Version | [230,279] | 50 | R | String | Firmware version |  |
| Date | [290,291] | 2 | R | uint32 | Current date of CP | yymmdd |
| Time | [294,295] | 2 | R | uint32 | Current time of CP | hhmmss |
| Chargepoint Power | [400,401] | 2 | R | uint32 | Max power of Chargepoint | W |
| Number of Phases | 404 | 1 | R | uint16 | 0: 1-phase , 1: 3-phase | |
| Chargepoint State |  1000 |  1 | R | uint16 | 0: "Available", 1: "Preparing", 2: "Charging", 3: "SuspendedEVSE", 4: "SuspendedEV", 5: "Finishing", 6: "Reserved", 7: "Unavailable", 8: "Faulted" | |
| Charging State | 1001 | 1 | R | uint16 | 0: Not Charging, State Ax, Bx, Dx or C1, 1: Charging, state C2 | |
| Equipment State | 1002 | 1 | R | uint16 | 0: Initializing, 1: Running, 2: Fault, 3: Disabled, 4: Updating | |
| Cable State | 1004 | 1 | R |  uint16 | 0: Cable not connected, 1: Cable connected, vehicle not connected, 2: Cable connected, vehicle connected, 3: Cable connected, vehicle connected, cable locked | |
|EVSE Fault Code | 1006 | 1 | R | uint32 | 0: No fault, Other: Fault code | |
| Current L1 | 1008 | 1 | R | uint16 | L1 Instantaneous Current | mA | 
| Current L2 | 1010 | 1 | R | uint16 | L2 Instantaneous Current | mA |
| Current L3 | 1012 | 1 | R | uint16 | L3 Instantaneous Current | mA |
| Voltage L1 | 1014 | 1 | R | uint16 | L1 Voltage | V |
| Voltage L2 | 1016 | 1 | R | uint16 | L2 Voltage | V |
| Voltage L3 | 1018 | 1 | R | uint16 | L3 Voltage | V |
| Active Power Total | [1020,1021] | 2 | R | uint32 | Total Active Power | W |
| Active Power L1 | [1024,1025] | 2 | R | uint32 | L1 Active Power | W |
| Active Power L2 | [1028,1029] | 2 | R | uint32 | L2 Active Power | W |
| Active Power L3 | [1032,1033] | 2 | R | uint32 | L3 Active Power | W |
| Meter Reading | [1036,1037] | 2 | R | uint32 | Meter Reading | 0.1 kWh |
| Session Max Current | 1100 | 1 | R | uint16 | Max possible charging current for active session | A |
| EVSE Min Current | 1102 | 1 | R | uint16 | Min possible charging current for EVSE | A |
| EVSE Max Current | 1104 | 1 | R | uint16 | Max possible charging current for EVSE | A |
| Cable Max Current | 1106 | 1 | R | uint16 | Max possible charging current for charging cable | A |
| Session Energy | [1502,1503] | 2 | R | uint32 | Total Energy for current charging session | Wh |
| Session Start Time | [1504,1505] | 2 | R | uint32 | Session start time | hhmmss | 
| Session Duration | [1508,1509] | 2 | R | uint32 | Session duration | s | 
| Session End Time | [1512,1513] | 2 | R | uint32 | Session end time | hhmmss | 
| Failsafe Current | 2000 | 1 | R/W | uint16 | Failsafe charging current during communication failure | A |  
| Failsafe Timeout | 2002 | 1 | R/W | uint16 | Communication timeout for switching to Failsafe charging current. If the timeout has occurred and the TCP socket is still active, TCP socket restarts. If set, Failsafe period is timeout/2, otherwise 20 sec. | s |
Charging Current | 5004 | 1 | R/W | uint16 | Dynamic charging current | A
| Alive Register | 6000 | 1 | R/W | uint16 | EMS (Master) writes 1 EVSE (Slave) writes 0, (EVSE checks this register at a period of (Failsafe Timeout)/2 for a value of 1, and sets it to 0. Period cannot go less than 3 seconds) | |

 
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

  
## DIN Housing

I have been designing a DIN Rail Mount housing embedding the Pi Zero and LCD Display. The model consists of six parts that can be 3D printed individually.

DIN Rail Mount Case
[Base](https://raw.githubusercontent.com/zeitinfarkt/wallbox-power-management/main/doc/cad/DIN Rail Mount PI-LCD\snapshots\base.jpg)
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

