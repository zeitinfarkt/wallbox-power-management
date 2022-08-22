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
from tkinter import LEFT

from enum import Enum
from PIL import Image, ImageDraw

import config
from config import FONT_MEDIUM, StatusLevel

from screen import Screen, Widget

TICKER_UPDATE_INTERVAL = 0.2
TEXT_MARGIN_Y = 2 
SHIFT_SPEED = 16
MAX_ELEMENTS = 5

#
# Implements a ticker widget to display long test messages
#

#
#  The ticker can either shift to the left (default) or to the right
# 
class TickerDirection(Enum):
    LEFT = 0
    RIGHT = 1
    
#
#  A TickerElement has a draw position (x), it's calculated draw width, and the actual StatusMessage.
# 
class TickerElement():
    
    # Constructor
    def __init__(self, x, width, message):
        self.x1 = x
        self.width = width
        self.x2 = self.x1 + self.width
        self.message = message            
             
    # Two ticker elements are equal when the message is the same, ignoring other fields
    def __eq__(self, other):
      return (self.message == other.message)

    def __le__(self, other):
      return (self.message <= other.message)

    def __gt__(self, other):
      return (self.message > other.message)

    def __lt__(self, other):
      return self.message < other.message 
  
    def __ge__(self, other):
      return self.message >= other.message 

    def __ne__(self, other):
      return (self.message != other.message)


#
# 
# 
class Ticker(Thread):

    #
    def __init__(self, direction, screen, window, font, color, exitEvent):
        Thread.__init__(self)
        
        self.direction = direction
        self.screen = screen
        self.window = window
        self.font = font
        self.defaultColor = color
        self.exitEvent = exitEvent

        config.solarisLogger.debug("Ticker direction is %s ", str(self.direction))
        if (self.direction == TickerDirection.LEFT):
            self.x1 = self.window.width
            self.x2 = self.window.width
        else:
            self.x1 = 0
            self.x2 = 0

        self.elements = []

    #
    def run(self):
        config.solarisLogger.debug("+ started  %s", __class__)
        while (not self.exitEvent.is_set()):
            self.draw()
            self.shift()
            self.exitEvent.wait(TICKER_UPDATE_INTERVAL)
        config.solarisLogger.debug("- stopped %s", __class__)

    # Adds a new status message to the list of ticker elements
    def add(self, newMessage):
        # dont add message if same already exists
        textWidth, textHeight = self.screen.context.textsize(newMessage.text, self.font)
        newElement = TickerElement(self.x2, textWidth, newMessage)
        if (not newElement in self.elements):
            if (len(self.elements) > MAX_ELEMENTS):
                del self.elements[-1]
            else:
                self.x2 = self.x2 + textWidth
                self.elements.append(newElement)
    
    #
    def shift(self):
        for element in self.elements:
            if (self.direction == TickerDirection.LEFT):
                element.x1 -= SHIFT_SPEED
                element.x2 -= SHIFT_SPEED
                if element.x2 < 0:
                    self.elements.remove(element)
                    break
            elif  (self.direction == TickerDirection.RIGHT):
                element.x1 += SHIFT_SPEED
                element.x2 += SHIFT_SPEED
                if element.x1 > self.window.width:
                    self.elements.remove(element)
                    break
        if (len(self.elements) ==0):
            self.window.clear()
        
    #
    def draw(self):
        endX = 0 
        for element in self.elements:
            color = config.COLOR_TEXT_DEFAULT
            if (element.x1 < self.window.width):
                if element.message.level == StatusLevel.ERROR:
                    color = config.COLOR_TEXT_ERROR
                elif element.message.level == StatusLevel.WARNING:
                    color = config.COLOR_TEXT_WARNING
                elif element.message.level == StatusLevel.INFO:
                    color = config.COLOR_TEXT_INFO
                else:
                    color = self.defaultColor
            self.window.clear()
            self.window.drawText(element.x1, TEXT_MARGIN_Y, element.message.text, self.font, color)
            endX = endX + element.width
            if endX > self.window.width:
                break

    #
    def __del__(self):
        config.solarisLogger.debug("destroying %s", __class__)

#
# 
# 
class TickerWidget(Thread):

    #
    def __init__(self, direction, screen, window, exitEvent):
      Thread.__init__(self)
      self.direction = direction
      self.screen = screen
      self.window = window
      self.exitEvent = exitEvent
      self.font = config.FONT_MEDIUM
      self.color = config.COLOR_TEXT_DEFAULT

      # Initialize our text seqeunce
      self.ticker = Ticker(self.direction, self.screen, self.window, self.font, self.color, self.exitEvent)
      self.ticker.start()
      
    # main loop runs until interrupt event has been received
    def run(self):
        config.solarisLogger.debug("+ starting %s", __class__)
        while (not self.exitEvent.is_set()):
            # get next message fro fifo queue
            self.screen.refresh()                
            self.exitEvent.wait(TICKER_UPDATE_INTERVAL)
        config.solarisLogger.debug("- stopping %s", __class__)

    #
    def push(self, message):
        self.ticker.add(message)

    #
    def setDirection(self, direction):
        self.direction = direction

    #
    def setColor(self, color):
        self.color = color
        
    #
    def setFont(self, font):
        self.font = font

    # cleanup
    def __del__(self):
        config.solarisLogger.debug("destroying %s", __class__)
