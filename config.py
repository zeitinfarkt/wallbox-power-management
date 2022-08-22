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
# Main Configuration 
# 

import logging

from threading import Event
from enum import Enum

from PIL import ImageFont

# Create and event to terminate all threads and exit application
exitEvent = Event()

# Raspberry Pi pin configuration:
RASPBERRY_PIN_RST = 27
RASPBERRY_PIN_DC = 25
RASPBERRY_PIN_BL = 18
RASPBERRY_PIN_BUS = 0
RASPBERRY_PIN_DEVICE = 0

# Predefined fonts and sizes

FONT_FILE="font/FreeSans.ttf"

FONT_SIZE_TINY=10
FONT_SIZE_SMALL=16
FONT_SIZE_MEDIUM=18
FONT_SIZE_LARGE=18

FONT_TINY = ImageFont.truetype(FONT_FILE, FONT_SIZE_TINY)
FONT_SMALL = ImageFont.truetype(FONT_FILE, FONT_SIZE_SMALL)
FONT_MEDIUM = ImageFont.truetype(FONT_FILE, FONT_SIZE_MEDIUM)

# Colors
COLOR_TEXT_DEFAULT="white"

COLOR_TEXT_ERROR="red"
COLOR_TEXT_WARNING="yellow"
COLOR_TEXT_INFO="white"
COLOR_TEXT_OK="green"

WINDOW_DEFAULT_BACKGROUND="black"
WINDOW_DEFAULT_BORDER=0
WINDOW_DEFAULT_FOREGROUND="white"

# Priority of differen status message for status widget
class StatusLevel(Enum):
    CRITICAL = 0
    ERROR = 1
    WARNING = 2
    INFO = 3

# Initialize logging

solarisLogger = logging.getLogger('Solaris')
solarisLogger.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler("solaris.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)
solarisLogger.addHandler(fileHandler)

