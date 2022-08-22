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
from queue import Queue
from PIL import Image, ImageDraw

import config

from screen import Screen, Widget
from tickerWidget import TickerWidget, TickerDirection

TIME_UPDATE_INTERVAL=1


#
# Display current time in a sperate thread
#
class StatusMessage():
    def __init__(self, level, text):
      self.level = level
      self.text = text
      
    def __lt__(self, other):
      return self.level < other.level 
  
    def __le__(self, other):
      return self.level <= other.level 

    def __ge__(self, other):
      return self.level >= other.level 

    def __eq__(self, other):
      return (self.level == other.level) and (self.text == other.text)

    def __ne__(self, other):
      return (self.level != other.level) or (self.text != other.text)


#
# Display current time in a sperate thread
#
class StatusWidget(Thread):

    #
    def __init__(self, screen, queue, exitEvent):
      Thread.__init__(self)
      self.screen = screen
      self.queue = queue
      self.exitEvent = exitEvent
      
      self.window = Widget("Status", 0, 110, 160, 18, "black", "white")
      self.screen.addWidget(self.window)
      self.window.clear()

      # create and start ticker
      self.ticker = TickerWidget(TickerDirection.LEFT, self.screen, self.window, self.exitEvent)
      
    # worker on status message in equq
    def run(self):
        config.solarisLogger.debug("+ starting %s", __class__)
        self.ticker.start()                        
        while (not self.exitEvent.is_set()):
            try:
              statusMessage = self.queue.get(block=True, timeout=1)
              self.ticker.push(statusMessage)
              self.queue.task_done()
              self.screen.refresh()
              self.exitEvent.wait(1)
            except Exception as ex:
              # terminate if interrupt signal CTRL-C received
              if self.exitEvent.is_set():
                break
        config.solarisLogger.debug("- stopping %s", __class__)

    # cleanup
    def __del__(self):
        config.solarisLogger.debug("destroying %s", __class__)


