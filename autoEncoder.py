#!/usr/bin/env python
# Scott Stubbs - code to allow pnCCD encoders to turn on and off automatically.
# Based on SXR scanning scripts by A. Mitra et al.

import pyca
from Pv import Pv

import sys
import time
import random
import threading

from options import Options

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
  options = Options(['motor', 'encoder', 'move_positive', 'move_negative'])
  try:
    options.parse()
  except Exception, msg:
    options.usage(str(msg))
    sys.exit()

  motor_prefix = options.motor
  encoderpv = Pv(options.encoder)
  evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
 
  try:
    "SETTING TWEAK PV"
    if options.opts['move_positive'] == 1:
        if options.opts['move_negative'] == 1:
            sys.exit("Check options, can only move motor in one direction!")
	print "Positive tweak"
    	motorpv = Pv(motor_prefix + '.TWK_POS')
    elif options.opts['move_negative'] == 1:
	print "Negative tweak"
    	motorpv = Pv(motor_prefix + '.TWK_NEG')
    else:
        sys.exit("Check options, nothing to move!")
# Connect motor, proc, dmov and encoder PVs
    motorpv.connect(1.0)
    motor_statpv = Pv(motor_prefix + ':UPDATE_STATUS.PROC')
    motor_statpv.connect
    dmovpv = donemoving(motor_prefix + '.DMOV')
    dmovpv.connect(1.0)
    dmovpv.monitor(evtmask, ctrl=False)
    encoderpv.connect(1.0)
    pyca.flush_io()
#  Put to encoder PV to turn it on, wait briefly
    encoderpv.put('1', 2.0)
    self.__sem.wait(50)
#  Put to motor tweak PV
    motorpv.put('1', 2.0)
    dmovpv.wait_for_done()
#  Once motor is done moving, turn encoder back off!
    encoderpv.put('0', 2.0)
# Verify
    if encoderpv.get(2.0) == 0:
        print "Encoder off!"
    else:
        print "Encoder may not be off. Try manually."
# Cleanup
    dmovpv.disconnect()
    motorpv.disconnect()
    encoderpv.disconnect()

  except pyca.pyexc, e:
      print 'pyca exception: %s' %(e)
  except pyca.caexc, e:
      print 'channel access exception: %s' %(e)

