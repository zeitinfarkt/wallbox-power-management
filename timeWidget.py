#!/usr/bin/python
#
# Project: Dynamic Power Management of a Wallbox in combination with a Solar Inverter
#          Wallbox: Vestel EVC04-AC22-T2P
#          Inverter: Fronius Symo 10.0-3-M, Data Logger 240.1120670, Smart Meter 63A
#
# Author:  (c) Nihat Kücük (August 2022)
# 
# Widget showing current time
#

import time
from datetime import datetime
from threading import Thread
from PIL import Image, ImageDraw

import config

from screen import Screen, Widget

TIME_UPDATE_INTERVAL=1

#
# Display current time in a sperate thread and widget
#
class TimeWidget(Thread):

    #
    def __init__(self, screen, exitEvent):
      Thread.__init__(self)
      self.screen = screen
      self.exitEvent = exitEvent
      self.window = Widget("Time", 80, 0, 80, 32)
      self.screen.addWidget(self.window);

    #
    def run(self):
        config.solarisLogger.debug("+ starting %s", __class__)
        while (not self.exitEvent.is_set()):
            # render current time
            currentTime = datetime.now().strftime('%H:%M:%S')
            self.window.clear()
            self.window.drawText(2, 4, currentTime, config.FONT_MEDIUM)
            self.screen.refresh()
            self.exitEvent.wait(TIME_UPDATE_INTERVAL)
        config.solarisLogger.debug("- stopping %s", __class__)

    # clean up
    def __del__(self):
        config.solarisLogger.debug("destroying %s", __class__)


