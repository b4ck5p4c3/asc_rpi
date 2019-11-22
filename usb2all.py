import minimalmodbus
import serial.tools.list_ports
import time
import random

minimalmodbus.BAUDRATE = 9600
minimalmodbus.TIMEOUT = 10
minimalmodbus.PARITY = 'N'

slave_address = 10

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
mb.serial.baudrate = 9600
mb.serial.timeout = 55
mb.handle_local_echo = True
if not mb.serial.is_open:
  mb.serial.open()

GPIO_SIZE = 16

MODE_BASE = 0
WRITE_BASE = MODE_BASE + GPIO_SIZE
PULL_BASE = WRITE_BASE + GPIO_SIZE

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

# test_inputs()
test_outputs()
'''
while(1):
  data = mb.read_registers(REG_INPUT_START, REG_INPUT_SIZE, functioncode=MODBUS_READ_INPUT)

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

  time.sleep(0.08)
'''


