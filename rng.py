# Guy Zyskind
# MIT Media Lab, 2014-11-11
# A sensor-based RNG
# Developed FOR 'HOW TO MAKE' class
# Based on Neil's Gershenfeld code:
# ---------------------------------
# hello.light.45.py
#
# receive and display light level
# hello.light.45.py serial_port
#
# Neil Gershenfeld
# CBA MIT 10/24/09
#
# (c) Massachusetts Institute of Technology 2009
# Permission granted for experimental and personal use;
# license for commercial sale available from MIT
#

import serial
import sys
import math

WINDOW = 600 # window size
eps = 0.5 # filter time constant
filter = 0.0 # filtered value
rand_val = 0

def get_rand(v, n):
   return int((v - math.floor(v)) * 100) % n

def read_rand(n):
   global filter, eps
   #
   # idle routine
   #
   # print "Starting idle routine"
   byte2 = 0
   byte3 = 0
   byte4 = 0
   ser.flush()
   while 1:
      #
      # find framing 
      #
      byte1 = byte2
      byte2 = byte3
      byte3 = byte4
      byte4 = ord(ser.read())
      if ((byte1 == 1) & (byte2 == 2) & (byte3 == 3) & (byte4 == 4)):
         break
   low = ord(ser.read())
   high = ord(ser.read())
   value = 256*high + low
   filter = (1-eps)*filter + eps*value
   x = int(.2*WINDOW + (.9-.2)*WINDOW*filter/1024.0)
   return get_rand(filter, n)

#
#  check command line arguments
#
if (len(sys.argv) != 3):
   print "command line: rng.py serial_port modulus"
   sys.exit()
port = sys.argv[1]

n = 65
try:
   n = int(sys.argv[2])
except:
   pass

#
# open serial port
#
ser = serial.Serial(port,9600)
ser.setDTR()

r = 0
for i in range(10):
   r = read_rand(n)

print r
