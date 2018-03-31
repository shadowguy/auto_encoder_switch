#!/usr/bin/env python
# Scott Stubbs - code to allow pnCCD encoders to turn on and off automatically.
# Based on SXR scanning scripts by A. Mitra et al.

import pyca
from Pv import Pv

import sys
import time
import random
import threading

import argparse

class donemoving(Pv):
  def __init__(self, name):
    Pv.__init__(self, name)
    self.monitor_cb = self.monitor_handler
    self.__sem = threading.Event()

  def wait_for_done(self):
    moving = False
    while not moving:
      self.__sem.wait(0.1)
      if self.__sem.isSet():
        self.__sem.clear()
        if self.value == 0:
          moving = True
      else:
        print 'timedout while waiting for moving'
        break
    while moving:
      self.__sem.wait(1500)
      if self.__sem.isSet():
        self.__sem.clear()
        if self.value == 1:
          moving = False
      else:
        print 'timedout while waiting for done'
        break

  def monitor_handler(self, exception=None):
    try:
      if exception is None:
        print 'pv %s is %d' %(self.name, self.value)
        self.__sem.set()
      else:
        print "%-30s " %(self.name), exception
    except Exception, e:
      print e

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='pnCCD encoder automation, will turn encoder on, move motor in specified direction and turn back off again')
  parser.add_argument('motor', metavar='motor', help='PV of motor name')
  parser.add_argument('encoder', metavar='encoder', help='PV of encoder')
  parser.add_argument('move_direction', metavar='move_direction', help='+ for positive move, - for negative')
  try:
      args=parser.parse_args()
  except:
     sys.exit("Check arguments!")  #Likely no arguments passed in

  motor_prefix = args.motor
  encoderpv = Pv(args.encoder)
  evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
  print args
  try:
    "SETTING TWEAK PV"
    if args.move_direction == '+':
	print "Positive tweak"
    	motorpv = Pv(motor_prefix + '.TWF')
    elif args.move_direction == '-':
	print "Negative tweak"
    	motorpv = Pv(motor_prefix + '.TWR')
    else:
        sys.exit("Check options, no direction found!")
# Connect motor, proc, dmov and encoder PVs - proc needed to tell IOC encoder is on
    motorpv.connect(1.0)
    motor_statpv = Pv(motor_prefix + ':UPDATE_STATUS.PROC')
    motor_statpv.connect(1.0)
    dmovpv = donemoving(motor_prefix + '.DMOV')
    dmovpv.connect(1.0)
    dmovpv.monitor(evtmask, ctrl=False)
    encoderpv.connect(1.0)
    pyca.flush_io()
#  Put to encoder PV to turn it on, wait briefly
    encoderpv.put('1', 2.0)
    time.sleep(0.5)
#  Tell IOC to update status
    motor_statpv.put(1, 2.0)
    time.sleep(0.5)
#  Put to motor tweak PV
    motorpv.put(1, 2.0)
    dmovpv.wait_for_done()
#  Once motor is done moving, turn encoder back off!
    encoderpv.put('0', 2.0)
# Verify
    encoderpv.get(False, 1.0) # Don't need control values
    if encoderpv.value == 0:
        print "Encoder off!"
    else:
        print "Encoder may not be off. Try manually."
# Cleanup
    dmovpv.disconnect()
    motorpv.disconnect()
    encoderpv.disconnect()
    motor_statpv.disconnect()

  except pyca.pyexc, e:
      print 'pyca exception: %s' %(e)
  except pyca.caexc, e:
      print 'channel access exception: %s' %(e)

