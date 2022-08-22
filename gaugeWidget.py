#!/usr/bin/python
#
# Project: Dynamic Power Management of a Wallbox in combination with a Solar Inverter
#          Wallbox: Vestel EVC04-AC22-T2P
#          Inverter: Fronius Symo 10.0-3-M, Data Logger 240.1120670, Smart Meter 63A
#
# Author:  (c) Nihat Kücük (August 2022)
# 
# Widget showing power gauge for wallbox
#

import time
from datetime import datetime
from threading import Thread
from PIL import Image, ImageDraw

import config

from screen import Screen, Widget


# Number of available gauge images
GAUGE_IMAGES=21

# Update inerval for gauge widget. Refresh bill be blocked by a message queue anyways
GAUGE_UPDATE_INTERVAL=5 

#
# A graphical bar showing power budget for wallbox
# 
#
class GaugeWidget(Thread):

    #
    def __init__(self, screen, queue, exitEvent):
      Thread.__init__(self,)
      self.screen = screen
      self.exitEvent = exitEvent
      self.queue = queue
      self.producedPower = 0
      
      self.window = Widget("Gauge", 0, 28, 160, 42)
      self.screen.addWidget(self.window);
      
      # initialize gauge images
      self.gaugeImage = []
      for idx in range(GAUGE_IMAGES):
        img = Image.open("img/gauge/gauge-"+str(idx)+".png")
        self.gaugeImage.append(img)
    
    #
    def run(self):
        config.solarisLogger.debug("+ starting %s", __class__)
        while (not self.exitEvent.is_set()):
            try:
                # wait/read for 3 data points
                self.maxWithdrawel = self.queue.get(block=True, timeout=1)
                self.powerProduced = self.queue.get(block=True, timeout=1)
                self.powerWallbox = self.maxWithdrawel + self.powerProduced
                self.powerMax = self.queue.get(block=True, timeout=1)                
                self.refresh()
                self.exitEvent.wait(GAUGE_UPDATE_INTERVAL)
            except Exception as ex:
              # terminate when interrupt signal CTRL-C received
              if self.exitEvent.is_set():
                break            
        config.solarisLogger.debug("- stopping  %s", __class__)

    def refresh(self):
        imgIdx = int(GAUGE_IMAGES * (self.powerWallbox - self.maxWithdrawel) / (self.powerMax - self.maxWithdrawel))
        # check value range
        if imgIdx >= GAUGE_IMAGES:
            imgIdx = GAUGE_IMAGES-1
        elif imgIdx < 0:
            imgIdx = 0
        self.window.clear()
        # display four labels and the correct gauge image
        self.window.drawText(0, 24, str(self.maxWithdrawel), config.FONT_TINY, config.COLOR_TEXT_DEFAULT)
        self.window.drawText(55, 22, str(self.powerWallbox), config.FONT_MEDIUM, config.COLOR_TEXT_OK)
        self.window.drawText(130, 24, str(self.powerMax), config.FONT_TINY, config.COLOR_TEXT_DEFAULT)
        self.window.drawImage(0, 0, self.gaugeImage[imgIdx])        
        self.window.drawText(2,6,"Wallbox Power Budget", config.FONT_TINY, "BLACK")
        self.screen.refresh()
    #
    def __del__(self):
        config.solarisLogger.debug("destroying %s", __class__)
