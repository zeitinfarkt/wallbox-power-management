#!/usr/bin/python
#
# Project: Dynamic Power Management of a Wallbox in combination with a Solar Inverter
#          Wallbox: Vestel EVC04-AC22-T2P
#          Inverter: Fronius Symo 10.0-3-M, Data Logger 240.1120670, Smart Meter 63A
#
# Author:  Nihat Kücük (August 2022)
# 
# Solaris Main App
#

import time
from datetime import datetime
from threading import Thread
from PIL import Image, ImageDraw
from queue import PriorityQueue, Queue

import config

from timeWidget import TimeWidget
from statusWidget import StatusWidget
from gaugeWidget import GaugeWidget
from wallboxWidget import WallboxWidget
from inverterWidget import InverterWidget
from screen import Screen, Widget

# Queue for sending / receiving interver data
powerQueue=Queue()

# Queue for sending and receiving varios system status messages
statusQueue=PriorityQueue()

#
#
#
class SolarisApp(Thread):

    def __init__(self,exitEvent):
      Thread.__init__(self)
      self.exitEvent = exitEvent
      
      config.solarisLogger.debug("initializing %s ", __class__)
      
      # Initialize screen / display
      self.screen = Screen ('BLACK');

      # Widget showing status inverter status
      self.froniusWidget = Widget("Inverter", 0, 0, 80, 32)
      self.screen.addWidget(self.froniusWidget);

      # Widget showing the current time
      self.timeWidget=TimeWidget(self.screen, exitEvent)      
      self.timeWidget.start()

      # Start Inverter Monitor
      self.inverterWidget=InverterWidget(self.screen, statusQueue, powerQueue, exitEvent)      
      self.inverterWidget.start()

      # Start Wallbox Monitor
      self.wallboxWidget=WallboxWidget(self.screen, statusQueue, powerQueue, exitEvent)      
      self.wallboxWidget.start()

      # Widget showing available power budget for wallbox
      self.gaugeWidget=GaugeWidget(self.screen, powerQueue, exitEvent)      
      self.gaugeWidget.start()
      
      # Widget for status and error messages
      self.statusWidget=StatusWidget(self.screen, statusQueue, exitEvent)
      self.statusWidget.start()
        
    # main loop terminates when interrupt signal has been received
    def run(self):
        config.solarisLogger.debug("+ starting %s", __class__)
        while (not self.exitEvent.is_set()):
            # Wait
            self.exitEvent.wait(1)
        config.solarisLogger.debug("- stopping %s", __class__)

    # cleanup
    def __del__(self):
        config.solarisLogger.debug("destroying %s", __class__)
