#
# Project: Dynamic Power Management of a Wallbox in combination with a Solar Inverter
#          Wallbox: Vestel EVC04-AC22-T2P
#          Inverter: Fronius Symo 10.0-3-M, Data Logger 240.1120670, Smart Meter 63A
#
# Author:  (c) Nihat Kücük (August 2022)
# 
# A simple screen and windows utility class
# 

import os
import sys
import time
import datetime
import logging
import threading

import config

import spidev as SPI


from threading import Thread

from lib import LCD_1inch8
from PIL import Image,ImageDraw

# Set screen brightness to 100%
SCREEN_BRIGHTNESS = 100
SCREEN_REFESH_RATE = .5


#
# This class manages the display screen and holds one or more windows
#
class Screen:
    def __init__ (self, bgColor):
        config.solarisLogger.debug("initializing screen")
        
        self.bgColor = bgColor
        self.brightness = SCREEN_BRIGHTNESS
        self.windows = []
        self.splash = True
        
        # Initialize display
        self.display = LCD_1inch8.LCD_1inch8()
        self.display.Init()
        
        #Set the backlight
        self.display.bl_DutyCycle(self.brightness)
        
        # set dimensions
        self.width = self.display.width
        self.height = self.display.height
        config.solarisLogger.info('Display LCD 1.8": %s x %s', self.width, self.height)
        
        # Set default background image
        self.bgImage = Image.new("RGB", (self.width, self.height), bgColor)

        # Get drawing context
        self.context = ImageDraw.Draw(self.bgImage)
        config.solarisLogger.info("Initalized screen: %s x %s", self.width, self.height)

        self.semaphore = threading.Semaphore()
        
        splashTimer = Thread(target=self.showSplash)
        splashTimer.start()
        
        # start screen refresh thread
        self.refresh()


    # set splash screen
    def showSplash(self):
        image = Image.open("img/on.png")
        self.display.ShowImage(image)
        time.sleep(3)
        self.splash = False        

    # 
    def refresh(self):
        if (self.splash == True):
            return
        for window in self.windows:
            self.bgImage.paste(window.bgImage, window.offset)
        self.semaphore.acquire()
        self.display.ShowImage(self.bgImage)
        self.semaphore.release()

    def setWallpaper(self, image):
        self.bgImage = image

    def addWidget(self, window):
        config.solarisLogger.debug("adding window %s to screen", window.name)
        self.windows.append(window)

    def clear(self):
        offImage=Image.open("img/off.png");
        self.display.ShowImage(offImage)

    def __del__(self):
        config.solarisLogger.debug("exiting display")
        self.clear()
        self.display.module_exit()


#
# This class represents a very simple window
#
class Widget:

    def __init__ (self, name, x, y, width, height, bgColor=config.WINDOW_DEFAULT_BACKGROUND, fgColor=config.WINDOW_DEFAULT_FOREGROUND, border=config.WINDOW_DEFAULT_BORDER):
        config.solarisLogger.debug("initializing window %s", name)
        self.name = name
        self.offset = (x, y)
        self.border = border
        # set dimensions
        self.width = width
        self.height = height
        #set colors
        self.bgColor = bgColor
        self.fgColor = fgColor
        # Drawing context
        self.bgImage = Image.new("RGB", (self.width, self.height), bgColor)
        self.context = ImageDraw.Draw(self.bgImage)
        self.setBackgroundColor(bgColor);
        # Draw border
        self.clear()
    
    def setBackgroundColor(self, bgColor):
        self.bgColor = bgColor;
        self.clear()
        
    def drawBorder(self):
        if self.border:
            self.context.rectangle((0, 0, self.width-self.border, self.height-self.border), outline=self.fgColor, width = self.border)
    
    def drawText(self, x, y, msg, f, c=config.COLOR_TEXT_DEFAULT):
        self.context.text((x, y), msg, font = f, fill = c)
        self.drawBorder()

    def drawImage(self, x, y, img):
        self.bgImage.paste(img, (x, y))
        self.drawBorder()

    def drawTriangle(self, x1, y1, x2, y2, x3, y3, color):
        self.context.polygon([(x1,y1), (x2, y2), (x3,y3)], fill = color)
        self.drawBorder()
    
    def clear(self):
        self.context.rectangle((0, 0, self.width, self.height), fill = self.bgColor)
        self.drawBorder()
    
    def __del__(self):
        config.solarisLogger.debug("clearing window %s", self.name)
        self.clear()
