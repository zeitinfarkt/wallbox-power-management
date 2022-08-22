#!/bin/python
#
# Project: Dynamic Power Management of a Wallbox in combination with a Solar Inverter
#          Wallbox: Vestel EVC04-AC22-T2P
#          Inverter: Fronius Symo 10.0-3-M, Data Logger 240.1120670, Smart Meter 63A
#
# Author:  Nihat Kücük (August 2022)
# 
# Main Module
# 


from threading import Thread, Event
import signal
import time

import config
from solarisApp import SolarisApp

# Create and event to terminate all threads and exit application
exitEvent = Event()

# Define handlers
def signalHandler(sig, frame):
    config.solarisLogger.info('Interrupted CTRL-C received. Terminating application...')
    exitEvent.set()

# Set signal handler for cathcing CTRL-C interrupt
signal.signal(signal.SIGINT, signalHandler)

#
def main():
    # Create main app/thread
    config.solarisLogger.info('Started Solaris.')
    solarisApp=SolarisApp(exitEvent)
    
    # start the thread
    solarisApp.start()
    
#
if __name__ == '__main__':
    main()
   