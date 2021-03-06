import minimalmodbus
import serial.tools.list_ports
import time
import random

# slave_address = 11
slave_address = 1

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

MODBUS_TIMEOUT = 0.05

mb_intro = minimalmodbus.Instrument('/dev/ttyS0', 11, mode='rtu', debug = False)
mb_intro.serial.baudrate = 115200
mb_intro.serial.timeout = MODBUS_TIMEOUT
# mb_intro.handle_local_echo = True

if not mb_intro.serial.is_open:
  mb_intro.serial.open()

mb_pauk = minimalmodbus.Instrument('/dev/ttyS0', 1, mode='rtu', debug = False)
mb_pauk.serial.baudrate = 115200
mb_pauk.serial.timeout = MODBUS_TIMEOUT
# mb_pauk.handle_local_echo = True

if not mb_pauk.serial.is_open:
  mb_pauk.serial.open()

mb_sensor = minimalmodbus.Instrument('/dev/ttyS0', 10, mode='rtu', debug = False)
mb_sensor.serial.baudrate = 115200
mb_sensor.serial.timeout = MODBUS_TIMEOUT
# mb_sensor.handle_local_echo = True

if not mb_sensor.serial.is_open:
  mb_sensor.serial.open()

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

def test_outputs(mb):
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

def test_inputs(mb):
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

DOOR_3 = 15
DOOR_2 = 14
DOOR_1 = 13

SIGN = 4

DOOR_KEY = 0

pin_modes = [1] * 16
pin_modes[DOOR_1] = 0
pin_modes[DOOR_2] = 0
pin_modes[DOOR_3] = 0
pin_modes[SIGN] = 1

door_state_1 = False
door_state_2 = False
door_state_3 = False

pins = [1] * 16

device_pins = [0] * 16

pins[DOOR_KEY] = 0
pins[SIGN] = 1



RETRIES = 7
RETRY_TIMEOUT = 0.005
SAFE_TIMEOUT = 0.005

def safe_write(mb, address, data):
  for i in xrange(RETRIES):
    try:
      if i > 1:
        print "retry write", i
      mb.write_bit(address, data, functioncode=0x05)
      time.sleep(SAFE_TIMEOUT)
      return
    except Exception:
      # print "except"
      time.sleep(RETRY_TIMEOUT)

  print "modbus TIMEOUT"

def safe_writes(mb, address, data):
  for i in xrange(RETRIES):
    try:
      if i > 1:
        print "retry write", i
      mb.write_bits(address, data)
      time.sleep(SAFE_TIMEOUT)
      return
    except Exception:
      # print "except"
      time.sleep(RETRY_TIMEOUT)

  print "modbus TIMEOUT"

def safe_reads(mb, address, size):
  for i in xrange(RETRIES):
    try:
      if i > 1:
        print "retry read", i
      time.sleep(SAFE_TIMEOUT)
      return mb.read_bits(address, size)
    except Exception:
      # print "except"
      time.sleep(RETRY_TIMEOUT)

  print "modbus TIMEOUT"

def safe_read_registers(mb, address, size):
  for i in xrange(RETRIES):
    try:
      if i > 1:
        print "retry read", i
      time.sleep(SAFE_TIMEOUT)
      return mb.read_registers(address, size, functioncode=0x4)
    except Exception:
      # print "except"
      time.sleep(RETRY_TIMEOUT)

  print "modbus TIMEOUT"

# PAUK

blue = 8
white = 9
red = 10
green = 11
yellow = 12
led1 = 14
led2 = 15
on  = 1
off = 0

def pauk_init(mb):
  safe_write(mb, 0, 1)
  safe_write(mb, 1, 1)
  safe_write(mb, 2, 1)
  safe_write(mb, 3, 1)
  safe_write(mb, 4, 1)
  safe_write(mb, 5, 0)
  safe_write(mb, 6, 1)
  safe_write(mb, 7, 1)

def Get_BTN(mb):
  btn = mb.read_register(12293, functioncode=0x04)
  mb.write_bit(22,1, functioncode=0x05)
  return btn

def random_flashing(mb, delay):
  safe_write(mb, blue, 1 if door_state_1 else 0)
  time.sleep(delay)
  safe_write(mb, white, 1 if door_state_2 else 0)
  time.sleep(delay)
  safe_write(mb, red, 1 if door_state_3 else 0 )
  time.sleep(delay)
  safe_write(mb, green, random.getrandbits(1))
  time.sleep(delay)
  safe_write(mb, yellow, random.getrandbits(1))
  time.sleep(delay)
  safe_write(mb, yellow, random.getrandbits(1))
  time.sleep(delay)
  safe_write(mb, led2, random.getrandbits(1))
  time.sleep(delay)

def intro_init(mb):
  safe_writes(mb, MODE_BASE, pin_modes)
  time.sleep(0.1)
  safe_writes(mb, PULL_BASE, [1 - x for x in pin_modes])

  safe_writes(mb, RELAY_2, [0])

  safe_writes(mb, RELAY_3, [1])

relay_time = time.time()
RELAY_TIMEOUT = 5

light = 0

aux_button = False

def intro_poll(mb):
  global aux_button

  global door_state_1
  global door_state_2
  global door_state_3
  global relay_time
  global light
  global device_pins

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
    # safe_writes(mb, RELAY_1, [1])
    # pins[DOOR_KEY] = 1
  
  if not en[DOOR_2] and door_state_2:
    door_state_2 = False
    print "door closed"
    # safe_writes(mb, RELAY_1, [0])
    # pins[DOOR_KEY] = 0

  if en[DOOR_1] and (not door_state_1):
    door_state_1 = True
    print "door 1 open"
  
  if not en[DOOR_1] and door_state_1:
    door_state_1 = False
    print "door 1 closed"

  # print "btn:", aux_button

  pins[DOOR_KEY] = aux_button
  # print pins[DOOR_KEY]

  if (not door_state_2) and (not door_state_3):
    safe_writes(mb, RELAY_2, [0])
  else:
    safe_writes(mb, RELAY_2, [1])


  # print "door 1:", door_state_1, "door 2:", door_state_2
  if (not door_state_1) and (not door_state_2):
    safe_writes(mb, RELAY_1, [0])
  else:
    safe_writes(mb, RELAY_1, [1])

  if device_pins != pins:
    safe_writes(mb, WRITE_BASE, pins)
    device_pins = pins[:]

  '''
  if time.time() - relay_time > RELAY_TIMEOUT:
    relay_time = time.time()

    print "set light", light

    safe_writes(mb, RELAY_2, [light])

    light = 1 - light
  '''

def sensor_poll(mb):
  data = safe_read_registers(mb, REG_INPUT_START, REG_INPUT_SIZE)

  raw_temp = (data[REG_INPUT_TEMP_H] << 16) | data[REG_INPUT_TEMP_L]
  raw_humi = (data[REG_INPUT_HUMI_H] << 16) | data[REG_INPUT_HUMI_L]
  raw_pres = (data[REG_INPUT_PRES_H] << 16) | data[REG_INPUT_PRES_L]
  raw_gas  = (data[REG_INPUT_GAS_H]  << 16) | data[REG_INPUT_GAS_L]

  temp = raw_temp / 100.0
  humi = raw_humi / 1000.0
  pres = raw_pres / 100.0
  gas = raw_gas

  #print('T: {0}, P: {1}, H: {2}, G: {3}'.format(raw_temp, raw_pres, raw_humi, raw_gas))
  print('T: {0} degC, P: {1} hPa, H: {2} %%rH, G: {3} ohms'.format(temp, pres, humi, gas))

intro_init(mb_intro)
# pauk_init(mb_pauk)

while(1):
  aux_button = Get_BTN(mb_pauk)
  # print "btn:", aux_button
  random_flashing(mb_pauk, 0.0)
  intro_poll(mb_intro)
  # sensor_poll(mb_sensor)

  # print safe_reads(mb_intro, READ_EN_BASE + 15, 1)
  # time.sleep(1)
