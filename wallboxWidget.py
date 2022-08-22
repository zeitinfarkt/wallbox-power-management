#!/bin/python
#
# Project: Solaris
#
#          Dynamic Power Management of a EV Wallbox in combination with a Solar Power Inverter
#          Wallbox: Vestel EVC04-AC22-T2P
#          Inverter: Fronius Symo 10.0-3-M, Data Logger 240.1120670, Smart Meter 63A
#
# Author:  Nihat Kücük (August 2022)

#
# Widget for wallbox status
# 
#

import time

from threading import Thread
from queue import Queue

import config
from config import StatusLevel

from PIL import Image, ImageDraw

from screen import Screen, Widget
from statusWidget import StatusMessage

# Inverter Configuration

WALLBOX_CHECK_INTERVAL=10

#
#
#
class WallboxWidget(Thread):

    # Initializer
    def __init__(self, screen, statusQueue, powerQueue, exitEvent):
      Thread.__init__(self)
      self.screen = screen
      self.exitEvent = exitEvent
      self.statusQueue = statusQueue
      self.powerQueue = powerQueue

      self.window = Widget("Inverter", 0, 70, 160, 40, "darkgray")
      self.screen.addWidget(self.window)

    #
    # Application's main thread
    #
    def run(self):
        config.solarisLogger.debug("+ starting  %s", __class__)
        while (not self.exitEvent.is_set()):
            self.exitEvent.wait(WALLBOX_CHECK_INTERVAL)
        config.solarisLogger.debug("- stopping %s", __class__)

    #
    def __del__(self):
        config.solarisLogger.debug("destroying %s", __class__)
