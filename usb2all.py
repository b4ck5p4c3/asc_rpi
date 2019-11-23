import minimalmodbus
import serial.tools.list_ports
import time
import random

# minimalmodbus.BAUDRATE = 9600
minimalmodbus.TIMEOUT = 10
minimalmodbus.PARITY = 'N'

slave_address = 11
# slave_address = 1

MODBUS_READ_INPUT = 0x4

REG_INPUT_START = 0x300
REG_INPUT_TEMP_L  = 0
REG_INPUT_TEMP_H  = 1
REG_INPUT_HUMI_L  = 2
REG_INPUT_HUMI_H  = 3
REG_INPUT_PRES_L  = 4
REG_INPUT_PRES_H  = 5
REG_INPUT_GAS_L   = 6
REG_INPUT_GAS_H   = 7
REG_INPUT_SIZE = 8

mb = minimalmodbus.Instrument('/dev/ttyS0', slave_address, mode='rtu', debug = False)
mb.serial.baudrate = 115200
mb.serial.timeout = 0.5
mb.handle_local_echo = True

if not mb.serial.is_open:
  mb.serial.open()

GPIO_SIZE = 16

MODE_BASE = 0
WRITE_BASE = MODE_BASE + GPIO_SIZE
PULL_BASE = WRITE_BASE + GPIO_SIZE

RELAY_1 = GPIO_SIZE * 3 + 0
RELAY_2 = GPIO_SIZE * 3 + 1
RELAY_3 = GPIO_SIZE * 3 + 2

READ_EN_BASE = 0x100
READ_DIS_BASE = READ_EN_BASE + GPIO_SIZE


# mb.write_bit(PULL_BASE + 7, 1, functioncode=0x05)

def test_outputs():
  #for pin in xrange(0, 16):
  #  mb.write_bit(MODE_BASE + pin, 1, functioncode=0x05)
  mb.write_bits(MODE_BASE, [1] * 16)
  pins = [1] * 16
  while(1):
    #for pin in xrange(0, 16):
    #  mb.write_bit(WRITE_BASE + pin, 1, functioncode=0x05)
    for i in xrange(16):
      pins[i] ^= 1
      mb.write_bits(WRITE_BASE, pins)
      
    time.sleep(0.25)

def test_inputs():
  for pin in xrange(0, 16):
    mb.write_bit(MODE_BASE + pin, 0, functioncode=0x05)
    mb.write_bit(PULL_BASE + pin, 1, functioncode=0x05)

  while(1):
    en = mb.read_bits(READ_EN_BASE, 16, functioncode=0x02)
    dis = mb.read_bits(READ_DIS_BASE, 16, functioncode=0x02)

    print zip(en, dis)
    #for pin in xrange(0, 16):
    #  print "%d%d" % (mb.read_bit(READ_EN_BASE + pin, functioncode=0x02), mb.read_bit(READ_DIS_BASE + pin, functioncode=0x02)), 

    # print
    # mb.write_bits(WRITE_BASE, [1, 1, 1, 1, 1])
    
    time.sleep(0.25)

blue = 8
white = 9
red = 10
green = 11
yellow = 12
led1 = 14
led2 = 15
on  = 1
off = 0

def random_flashing(delay):
  mb.write_bit(blue,random.getrandbits(1), functioncode=0x05)
  time.sleep(delay)
  mb.write_bit(white,random.getrandbits(1), functioncode=0x05)
  time.sleep(delay)
  mb.write_bit(red,random.getrandbits(1), functioncode=0x05)
  time.sleep(delay)
  mb.write_bit(green,random.getrandbits(1), functioncode=0x05)
  time.sleep(delay)
  mb.write_bit(yellow,random.getrandbits(1), functioncode=0x05)
  time.sleep(delay)

DOOR_3 = 15
DOOR_2 = 14

DOOR_KEY = 0

pin_modes = [1] * 16
pin_modes[DOOR_2] = 0
pin_modes[DOOR_3] = 0
door_state_3 = False
door_state_2 = False
pins = [1] * 16

def pauk_init():
  mb.write_bit(0,1, functioncode=0x05)
  mb.write_bit(1,1, functioncode=0x05)
  mb.write_bit(2,1, functioncode=0x05)
  mb.write_bit(3,1, functioncode=0x05)
  mb.write_bit(4,1, functioncode=0x05)
  mb.write_bit(5,0, functioncode=0x05)
  mb.write_bit(6,1, functioncode=0x05)
  mb.write_bit(7,1, functioncode=0x05)


RETRIES = 5
RETRY_TIMEOUT = 0.05

def safe_writes(mb, address, data):
  for i in xrange(RETRIES):
    try:
      if i > 0:
        print "retry write", i
      mb.write_bits(address, data)
      time.sleep(0.1)
      return
    except Exception:
      print "except"
      time.sleep(RETRY_TIMEOUT)

  print "modbus TIMEOUT"

def safe_reads(mb, address, size):
  for i in xrange(RETRIES):
    try:
      if i > 0:
        print "retry read", i
      return mb.read_bits(address, size, functioncode=0x02)
      time.sleep(0.1)
    except Exception:
      print "except"
      time.sleep(RETRY_TIMEOUT)

  print "modbus TIMEOUT"


def intro_init():
  safe_writes(mb, MODE_BASE, pin_modes)
  time.sleep(0.1)
  safe_writes(mb, PULL_BASE, [1 - x for x in pin_modes])

relay_time = time.time()
RELAY_TIMEOUT = 5

light = 0

def intro_poll():
  global door_state_3
  global door_state_2
  global relay_time
  global light

  for i in xrange(16):
    if i != DOOR_KEY:
      pins[i] ^= 1

    pin_modes[DOOR_3] = 0

    en = safe_reads(mb, READ_EN_BASE, 16)

    # print "door:", en[DOOR_3]

    if en[DOOR_3] and (not door_state_3):
      door_state_3 = True
      print "door open"
    
    if not en[DOOR_3] and door_state_3:
      door_state_3 = False
      print "door closed"

    if en[DOOR_2] and (not door_state_2):
      door_state_2 = True
      print "door open"
      safe_writes(mb, RELAY_1, [1])
      pins[DOOR_KEY] = 1
    
    if not en[DOOR_2] and door_state_2:
      door_state_2 = False
      print "door closed"
      safe_writes(mb, RELAY_1, [0])
      pins[DOOR_KEY] = 0

    if (not door_state_2) and (not door_state_3):
      safe_writes(mb, RELAY_2, [0])
    else:
      safe_writes(mb, RELAY_2, [1])

    safe_writes(mb, WRITE_BASE, pins)

    '''
    if time.time() - relay_time > RELAY_TIMEOUT:
      relay_time = time.time()

      print "set light", light

      safe_writes(mb, RELAY_2, [light])

      light = 1 - light
    '''

    time.sleep(0.05)

mb.slave_address = 11
intro_init()
# mb.slave_address = 1
# pauk_init()

while(1):
  # mb.slave_address = 1
  # random_flashing(0.01)

  mb.slave_address = 10
  intro_poll()


'''
# test_inputs()
# test_outputs()











while(1):
  for i in xrange(16):
    pins[i] ^= 1

    pin_modes[DOOR_3] = 0

    mb.write_bits(WRITE_BASE, pins)

    # time.sleep(0.01)

    en = mb.read_bits(READ_EN_BASE, 16, functioncode=0x02)

    if en[DOOR_3] and (not door_state_3):
      door_state_3 = True
      print "door open"
    
    if not en[DOOR_3] and door_state_3:
      door_state_3 = False
      print "door closed"
'''

