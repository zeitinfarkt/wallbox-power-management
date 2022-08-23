
# Wallbox Power Management


## Motivation
Unfortunately, my local electricity provider did not approve the installation of a 22kW charging station (wallbox). I was allowed to draw a maximum grid power of 11kW, not 22kW. Since I've a photovoltaic system installed providing a peak power of up to 9,900 Watts I wanted to dynmacially increase the maximum wallbox power by the amount of energy produced my the photovoltaic system. For example, when my PV system produces 5,600 Watts I want to allow my wallbox to charge with 15,500 Watts (11,000 + 5,600) instaed of onl 11,000 Watts.
## The Challenge
By default my Fronius inverter only support a few wall box charger. And of course it does not not support my Vestel wallbox at all. Therefore, I decided to start this project to build my ownsimple power balancing device. It is a straight-forward hands-on power management which I've implemented using a Raspberry Pi Zero W single board computer and some peripherals.

## Photovoltaic System
My photovoltaic system consists of 28 pioeces Hanwa Q-Cells solar modules which produce a maximum peak power (Wp) of 9,900 Watts at full sunlight.
## The Inverter
The inverter device is a Fronius Symo 10.0-3-M. My wallbox is a Vestel EVC04-AC22-T2P eMobility charging device.

 

![Fronius Symo 10.0-3-M](https://www.fronius.com/~/protected-media/imported-media/07/17/m-71784.png?q=70&iw=770&ih=433&crop=1&imgtype=JPG =500x300)

![Fronius Symo 10.0-3-M](
# Wallbox Power Management


## Motivation
Unfortunately, my local electricity provider did not approve the installation of a 22kW charging station (wallbox). I was allowed to draw a maximum grid power of 11kW, not 22kW. Since I've a photovoltaic system installed providing a peak power of up to 9,900 Watts I wanted to dynmacially increase the maximum wallbox power by the amount of energy produced my the photovoltaic system. For example, when my PV system produces 5,600 Watts I want to allow my wallbox to charge with 15,500 Watts (11,000 + 5,600) instaed of onl 11,000 Watts.
## The Challenge
By default my Fronius inverter only support a few wall box charger. And of course it does not not support my Vestel wallbox at all. Therefore, I decided to start this project to build my ownsimple power balancing device. It is a straight-forward hands-on power management which I've implemented using a Raspberry Pi Zero W single board computer and some peripherals.

## Photovoltaic System
My photovoltaic system consists of 28 pioeces Hanwa Q-Cells solar modules which produce a maximum peak power (Wp) of 9,900 Watts at full sunlight.
## The Inverter
The inverter device is a Fronius Symo 10.0-3-M. My wallbox is a Vestel EVC04-AC22-T2P eMobility charging device.

 

![Fronius Symo 10.0-3-M](https://www.fronius.com/~/protected-media/imported-media/07/17/m-71784.png?q=70&iw=770&ih=433&crop=1&imgtype=JPG =500x300)


![On Image](https://github.com/zeitinfarkt/wallbox-power-management/blob/main/img/on.png)

| Wallbox |  |
| -- | -- |
| Fronius Symo 10.0-3-M | Fronius Symo 10.0-3-M |

The transformerless Fronius Symo 10.0-3-M is a 3-phase inverter in the power category of 10kW.

It features a Wifi and Ethernet internet connection and makes it easier to integrate third-party components.

The Fronius device features the following interface:

 - WLAN / Ethernet LAN: Fronius Solar.web, Modbus TCP SunSpec, Fronius Solar API (JSON)
 - 6 inputs and 4 digital inputs/outputs: Interface to ripple control receiver
 - USB (type A socket) 4): Data logging, inverter update via USB flash drive
 - 2x RS422 (RJ45 socket): Fronius Solar Net
 - Signalling output: Energy management (floating relay output)
 - Datalogger and web server: Integrated
 - External input: S0 meter connection / Evaluation of overvoltage protection
 - RS485: Modbus RTU SunSpec or meter connection 

### Fronius Solar API

The Fronius Solar API was designed to allow 3rd party software to request system data from various Fronius devices (e.g., inverters) providing a well-defined data API and data structures. In this project we read the following JSON reply we would get in respone to the Solari API call "GetPowerFlowRealtimeData"

  ```
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
  

However, we utilize the bilt-in Fronius Push Service available in the Settings Web Interface (Settings -> Push). We ask our Fronius inverter to push current power flow via FTP Upload (ftp://user@password:raspi0:21:/home/fronius/push/powerFlow.json) to our Raspberry Pi every 10 seconds.
 
Our application is only interested in the JSOB object Body/Inverters/1/P that holds the current power provided by the Fronius inverter.

# The Wallbox
The Vestel EVC04-AC22-T2P eMobility Wallbox is a 3-phase electic charger allowing a mximum charging power of 22kW (3x 32A @ 400V). It includes a 5m 3-phase TYPE 2 charging cable. The wallbox has an integrated DC protection circuit and features RFID card support.

Moost importantly, this vestel wallbox supports a Modbus TCP/RS-485 interface. Apparently there is a mobile app for Android and iOS to control the the wallbox,

like setting charging time, manually start/stop charging, and so on.

  

# Hardware

  

## Raspberry PI
- Raspberry Pi Zero W (small single-board computer)
- DIN Rail power Supply (e.g. MeanWell HDR-15-5 5V/2.4A)
- USB to RS-485 Converter
- LCD 1.8" color TFT display (Waveshare 0.96″ 160×80 pixels IPS HD LCD Display Modul, SPI Interface)

## Display

Since I would like to see the status of the entire system I have decided to connect a small 1.8" LCD display to the Raspberry Pi Zero.

#### LCD Display

|  | Waveshare 1.8" LCD Display | 
| :---         |     :---      |   
| ![Waveshare 1.8" LCD Display](https://www.waveshare.com/media/catalog/product/cache/1/image/560x560/9df78eab33525d08d6e5fb8d27136e95/1/_/1.8inch-lcd-module-1.jpg ) | The Waveshare 1.8" LCD display is connected to the Raspberry Pi using a standard SPI cable. Thedisplay uses a ST7735 driver chip and support a resolution of 160 by 128 pixels. |        

#### Pin Connections

The pins need to be connected like this:

| LCD  | PIN Raspberry Pi | GPIO |
| :---   | :---  | :---  | 
| VCC |	Pin 1 3,3V| 
| GND | Pin 6  GND| 
| SCL | Pin 23 SPI-CLK|   11| 
| SDA | Pin 19 SPI-MOSI|  10| 
| DC  | Pin 18 | 24| 
| RES | Pin 22 | 25| 
| CS  | Pin 24 SPI-CS0 PWM0 | 8| 



Display | Raspberry Pin Head

## Software
 
### Required Python Modules

You need to install the following python packages on your system (using "pip install <package>")
 - requests
 - pillow
 - simple-namespace
 - pytz
- python3-pil)

| Wallbox |  |
| -- | -- |
| Fronius Symo 10.0-3-M | Fronius Symo 10.0-3-M |

The transformerless Fronius Symo 10.0-3-M is a 3-phase inverter in the power category of 10kW.

It features a Wifi and Ethernet internet connection and makes it easier to integrate third-party components.

The Fronius device features the following interface:

 - WLAN / Ethernet LAN: Fronius Solar.web, Modbus TCP SunSpec, Fronius Solar API (JSON)
 - 6 inputs and 4 digital inputs/outputs: Interface to ripple control receiver
 - USB (type A socket) 4): Data logging, inverter update via USB flash drive
 - 2x RS422 (RJ45 socket): Fronius Solar Net
 - Signalling output: Energy management (floating relay output)
 - Datalogger and web server: Integrated
 - External input: S0 meter connection / Evaluation of overvoltage protection
 - RS485: Modbus RTU SunSpec or meter connection 

### Fronius Solar API

The Fronius Solar API was designed to allow 3rd party software to request system data from various Fronius devices (e.g., inverters) providing a well-defined data API and data structures. In this project we read the following JSON reply we would get in respone to the Solari API call "GetPowerFlowRealtimeData"

  ```
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
  

However, we utilize the bilt-in Fronius Push Service available in the Settings Web Interface (Settings -> Push). We ask our Fronius inverter to push current power flow via FTP Upload (ftp://user@password:raspi0:21:/home/fronius/push/powerFlow.json) to our Raspberry Pi every 10 seconds.
 
Our application is only interested in the JSOB object Body/Inverters/1/P that holds the current power provided by the Fronius inverter.

# The Wallbox
The Vestel EVC04-AC22-T2P eMobility Wallbox is a 3-phase electic charger allowing a mximum charging power of 22kW (3x 32A @ 400V). It includes a 5m 3-phase TYPE 2 charging cable. The wallbox has an integrated DC protection circuit and features RFID card support.

Moost importantly, this vestel wallbox supports a Modbus TCP/RS-485 interface. Apparently there is a mobile app for Android and iOS to control the the wallbox,

like setting charging time, manually start/stop charging, and so on.

  

# Hardware

  

## Raspberry PI
- Raspberry Pi Zero W (small single-board computer)
- DIN Rail power Supply (e.g. MeanWell HDR-15-5 5V/2.4A)
- USB to RS-485 Converter
- LCD 1.8" color TFT display (Waveshare 0.96″ 160×80 pixels IPS HD LCD Display Modul, SPI Interface)

## Display

Since I would like to see the status of the entire system I have decided to connect a small 1.8" LCD display to the Raspberry Pi Zero.

#### LCD Display

|  | Waveshare 1.8" LCD Display | 
| :---         |     :---      |   
| ![Waveshare 1.8" LCD Display](https://www.waveshare.com/media/catalog/product/cache/1/image/560x560/9df78eab33525d08d6e5fb8d27136e95/1/_/1.8inch-lcd-module-1.jpg ) | The Waveshare 1.8" LCD display is connected to the Raspberry Pi using a standard SPI cable. Thedisplay uses a ST7735 driver chip and support a resolution of 160 by 128 pixels. |        

#### Pin Connections

The pins need to be connected like this:

| LCD  | PIN Raspberry Pi | GPIO |
| :---   | :---  | :---  | 
| VCC |	Pin 1 3,3V| 
| GND | Pin 6  GND| 
| SCL | Pin 23 SPI-CLK|   11| 
| SDA | Pin 19 SPI-MOSI|  10| 
| DC  | Pin 18 | 24| 
| RES | Pin 22 | 25| 
| CS  | Pin 24 SPI-CS0 PWM0 | 8| 



Display | Raspberry Pin Head

## Software
 
### Required Python Modules

You need to install the following python packages on your system (using "pip install <package>")
 - requests
 - pillow
 - simple-namespace
 - pytz
- python3-pil