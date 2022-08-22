#!/usr/bin/python
#
# Project: Dynamic Power Management of a Wallbox in combination with a Solar Inverter
#          Wallbox: Vestel EVC04-AC22-T2P
#          Inverter: Fronius Symo 10.0-3-M, Data Logger 240.1120670, Smart Meter 63A
#
# Author:  (c) Nihat Kücük (August 2022)
#
# Widget shoing current time
#

import time
import json
import requests
import pytz

from datetime import datetime
from datetime import timedelta
from threading import Thread
from queue import Queue

import config

from config import StatusLevel

from PIL import Image, ImageDraw


from screen import Screen, Widget
from statusWidget import StatusMessage

# Inverter Configuration

# This is the URL (HTTP Web Interface) of the local power inverter
INVERTER_HTTP_ACCESS_URL = "http://fronius.fritz.box"

# Location of the power flow push file updated by the inverter using a FTP Upload
INVERTER_POWER_PRODUCTION_FILE="/home/fronius/push/powerflow.json"

# Time interval to check accessibility of inverter
INVERTER_CHECK_ACCESS_TIMEOUT = 10

# Time interval we want fresh power flow data
INVERTER_READOUT_INTERVAL = 10

# Maximum delay in seconds for a power flow upload
INVERTER_POWER_TOLERATED_DELAY=60

# maximum peak power our inverter is able to produce
INVERTER_MAX_POWER_SUPPLY=9900
ELECTRICITY_PROVDER_MAX_WITHDRAWL=11000
WALLBOX_POWER_MAX=ELECTRICITY_PROVDER_MAX_WITHDRAWL+INVERTER_MAX_POWER_SUPPLY 

# Status and error messages

STATUSR_INVERTER_OK=0
ERROR_INVERTER_POWER_OUTDATED=-110
ERROR_INVERTER_POWER_INVALID_VALUE=-111
ERROR_INVERTER_POWER_FILE_NOT_FOUND=-112
ERROR_INVERTER_POWER_FILE_CURRUPTED=-113

#
#
#
class InverterWidget(Thread):

    # Initializer
    def __init__(self, screen, statusQueue, powerQueue, exitEvent):
      Thread.__init__(self)
      self.screen = screen
      self.exitEvent = exitEvent
      self.statusQueue = statusQueue
      self.powerQueue = powerQueue

      self.reachable = False
      # Current power production reported by inverter
      self.producedPower = 0
      
      self.window = Widget("Inverter", 0, 0, 80, 30)
      self.screen.addWidget(self.window)

      self.statusImage = [
          Image.open("img/inverterLogo.png"),     # inverter ok
          Image.open("img/inverterLogoOff.png"),  # inverted not reachable
          Image.open("img/inverterDataOk.png") ,  # inverter pushed bad data
          Image.open("img/inverterBadData.png"),  # inverter pushed bad data
          Image.open("img/inverterOutdated.png"), # inverter has not updated intime
          Image.open("img/sunshine.png")          # inverter produces prower
      ]

    # Main thread
    def run(self):
        config.solarisLogger.debug("+ starting %s", __class__)
        imgIdx = 0
        while (not self.exitEvent.is_set()):
            self.window.clear()
            if self.isReachable():
                self.readPower()       
                self.powerQueue.put(ELECTRICITY_PROVDER_MAX_WITHDRAWL)
                self.powerQueue.put(self.producedPower)
                self.powerQueue.put(WALLBOX_POWER_MAX)
                self.screen.refresh()
            self.exitEvent.wait(INVERTER_READOUT_INTERVAL)
        config.solarisLogger.debug("- stopping %s", __class__)

    # checks whether inverter is reachable in local network
    def isReachable(self):
        try:
            urlRequest = requests.get(INVERTER_HTTP_ACCESS_URL, timeout=INVERTER_CHECK_ACCESS_TIMEOUT)
            self.reachable = True
        except (requests.exceptions.ConnectionError) as exception:
            errorMsg = "Inverter %s not reachable!" % INVERTER_HTTP_ACCESS_URL
            config.solarisLogger.error(errorMsg)
            self.statusQueue.put(StatusMessage(StatusLevel.ERROR, errorMsg))
            imgIdx=1
            self.reachable = False
        except (urlRequest.ConnectionError, urlRequest.Timeout) as exception:
            errorMsg = "Error connecting to %s" % INVERTER_HTTP_ACCESS_URL
            config.solarisLogger.error(errorMsg)
            self.statusQueue.put(StatusMessage(StatusLevel.ERROR, errorMsg))
            self.reachable = False
        self.window.drawImage(0, 0, self.statusImage[not self.reachable])
        return self.reachable

    def readPower(self): 
        imgIdx=0            
        try: 
            config.solarisLogger.debug("reading power flow file " + INVERTER_POWER_PRODUCTION_FILE)
            self.file = open(INVERTER_POWER_PRODUCTION_FILE)
            self.data = json.load(self.file)
            self.lastPushTime =  datetime.strptime(self.data["Head"]["Timestamp"], '%Y-%m-%dT%H:%M:%S%z')
            # read power floe element
            now = datetime.now(pytz.timezone('CET'))
            elapsedSeconds=(int)((now - self.lastPushTime).total_seconds())
            config.solarisLogger.debug("file has been updated %s seconds ago", elapsedSeconds)
            # check if file hasn't been updated for a while
            if elapsedSeconds > INVERTER_POWER_TOLERATED_DELAY:
                self.statusCode = ERROR_INVERTER_POWER_OUTDATED
                td_str = str(timedelta(seconds=elapsedSeconds))
                warningMsg = "Outdated powerflow (last update %s ago)" % td_str
                config.solarisLogger.warning(warningMsg)
                self.statusQueue.put(StatusMessage(StatusLevel.WARNING, warningMsg))
                imgIdx=4
                self.producedPower=0
            else:
                try:
                    self.producedPower=self.data["Body"]["Inverters"]["1"]["P"]
                    if (self.producedPower < 0) or (self.producedPower > WALLBOX_POWER_MAX):
                        self.statusCode = ERROR_INVERTER_POWER_INVALID_VALUE
                        imgIdx=3
                        warningMsg = "Read invalid power flow: ", str(self.producedPower)
                        config.solarisLogger.warning(warningMsg)
                        self.statusQueue.put(StatusMessage(StatusLevel.WARNING, warningMsg))

                    else:
                        self.statusCode = STATUSR_INVERTER_OK               
                        imgIdx=2
                        self.window.drawImage(50, 1, self.statusImage[5])
                        config.solarisLogger.debug("Last power reading: %s", str(self.producedPower))
                        statusMsg = "Prodction: %s W" % str(self.producedPower)
                        self.statusQueue.put(StatusMessage(StatusLevel.INFO, statusMsg))

                except (AttributeError, KeyError) as error:
                    self.statusCode = ERROR_INVERTER_POWER_FILE_NOT_FOUND
                    errorMsg = "Corrupted powerflow file: %s " % repr(error)
                    config.solarisLogger.warning(errorMsg)
                    self.statusQueue.put(StatusMessage(StatusLevel.ERROR, errorMsg))
                    imgIdx=2

        except FileNotFoundError as error:
            self.statusCode = ERROR_INVERTER_POWER_FILE_CURRUPTED
            config.solarisLogger.error(repr(error))
            imgIdx=3
            errorMsg="Missing powerflow file %s " % INVERTER_POWER_PRODUCTION_FILE
            config.solarisLogger.error(errorMsg)
            self.statusQueue.put(StatusMessage(StatusLevel.ERROR, errorMsg))

        self.window.drawImage(0, 0, self.statusImage[0])
        self.window.drawImage(28, 0, self.statusImage[imgIdx])
        
    def __del__(self):
        config.solarisLogger.debug("destroying %s", __class__)
