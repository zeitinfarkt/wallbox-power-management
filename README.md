# Wallbox Power Management

## Motivation

Unfortunately, my local electricity provider did not approvee the installation of a 22kW charging station (wallbox). Only a maximum grid draw of 11kW was granted for my residence. Since I have installed a photovoltaic system with a peak power of 9,900 Watts I want to adjust (dynamically) the maximum wallbox charge power by the energy production by my PV system. For example, if the photovoltaic system produces 5,600 Watts I would like to allow the wallbix to charge with 15,500 Watts (11,000 + 5,600) .5kW to the wallbox.

By default my Fronius inverter does not support the Vestel wallbox I have. Therefore I have decided to start this project to build my own very simple power balancing device. It is a straight-forward hands-on power management which I have implemented using a Raspberry Pi Zero W single board computer and some peripherals.

## The Challenge

By default my Fronius inverter does not support any Vestel wallboxes.


# The Photovoltaic System

## Solar Modules

My photovoltaic system consists of Hanwa 28 Q-Cells solar modules which can produce a maximum peak power (Wp) of 9900 Watts at full sunlight. 
The inverter device is a Fronius Symo 10.0-3-M. My wallbox is a Vestel  EVC04-AC22-T2P eMobility charging device.

## The Inverter

The transformerless Fronius Symo 10.0-3-M is a 3-phase inverter in the power category of 10kW.
It features a Wifi and Ethernet internet connection and makes it easier to integrate third-party components.
The Fronius device features the following interface:

- WLAN / Ethernet LAN:  Fronius Solar.web, Modbus TCP SunSpec, Fronius Solar API (JSON)
- 6 inputs and 4 digital inputs/outputs:    Interface to ripple control receiver
- USB (type A socket) 4): Data logging, inverter update via USB flash drive
- 2x RS422 (RJ45 socket):   Fronius Solar Net
- Signalling output:    Energy management (floating relay output)
- Datalogger and web server:    Integrated
- External input:  S0 meter connection / Evaluation of overvoltage protection
- RS485:    Modbus RTU SunSpec or meter connection

### Fronius Solar API

The Fronius Solar API was designed to allow 3rd party software to request system data from various Fronius devices (e.g., inverters) providing a well-defined data API and data structures. In this project we read the following JSON reply we would get in respone to the Solari API call "GetPowerFlowRealtimeData"

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

However, we utilize the bilt-in Fronius Push Service available in the Settings Web Interface (Settings -> Push). We ask our Fronius inverter to push current power flow via FTP Upload (ftp://user@password:raspi0:21:/home/fronius/push/powerFlow.json) to our Raspberry Pi every 10 seconds. 

Our application is only interested in the JSOB object Body/Inverters/1/P that holds the current power provided by the Fronius inverter.

# The Wallbox

The Vestel EVC04-AC22-T2P eMobility Wallbox is a 3-phase electic charger allowing a mximum charging power of 22kW (3x 32A @ 400V). It includes a 5m 3-phase TYPE 2 charging cable. The wallbox has an integrated DC protection circuit and features RFID card support.
Moost importantly, this vestel wallbox supports a Modbus TCP/RS-485 interface. Apparently there is a mobile app for Android and iOS to control the the wallbox,
like setting charging time, manually start/stop charging, and so on.

# Hardware

## Raspberry PI small single-board computer

- Raspberry Pi Zero W
- DIN Rail power Supply (e.g. MeanWell HDR-15-5 5V/2.4A)
- A USB to RS-485 Converter
- An LCD 1.8" color TFT display (Waveshare 0.96″ 160×80 pixels IPS HD LCD Display Modul, SPI Interface)

## LCD Display


The Waveshare 1." LCD display is connected to the Raspberry Pi using a standard SPI cable.
The LCD display uses a ST7735 driver chip and support a resolution of 160 by 128 pixels.
The pins need to be connected like this:

  Pin Connection
   Display | Raspberry Pin Head
  -----------------------------------------
  VCC      | Pin 1: 3,3V
  GND      | Pin 6: GND
  SCL      | Pin 23: SPI-CLK (GPIO 11)
  SDA      | Pin 19: SPI-MOSI (GPIO 10)
  DC       | Pin 18: (GPIO 24)
  RES      | Pin 22: (GPIO 25)
  CS       | Pin 24: SPI-CS0, PWM0 (GPIO 8)

## Software

### Required Python Modules

Install the following python packages with pip install

 - requests
 - pillow
 - simple-namespace
 - pytz
 - python3-pil  






