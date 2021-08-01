import pycom
from machine import I2C
from machine import UART
from machine import ADC
from machine import deepsleep
from machine import Pin
from network import Sigfox

from micropyGPS import MicropyGPS
import adxl345

import binascii
import time
import struct
import socket
import statistics

#Turn off heartbeat
pycom.heartbeat(False)

#Setup I2C for ADXL
i2c = I2C(0, I2C.MASTER, baudrate=100000)
adxl345_sensor = adxl345.ADXL345(i2c)
adxl345_sensor.data_rate = adxl345.DataRate.RATE_100_HZ
adxl345_sensor.range = adxl345.Range.RANGE_4_G

#Setup Uart for GPS
com = UART(1, baudrate=9600, pins=('P21', 'P22')) #P21 TX / P22 RX
gps_parser = MicropyGPS(0, 'dd') #DD format with 0 timezone offset

#Setup ADC
adc = ADC()
adcP16 = adc.channel(pin='P16', attn=ADC.ATTN_11DB) #Setup battery pin
adcP15 = adc.channel(pin='P15') #Setup temperature pin
NUM_ADC_READINGS = 50 #Number of voltage measurments

#TODO format in temperature
#Get an "average" battery measurement
def get_parsed_battmV():
    samples_voltage = [0]*NUM_ADC_READINGS
    for i in range(50):
        samples_voltage[i] = (2*adcP16.voltage())//1
    batt_mV = round(statistics.mean(samples_voltage))

    print("Battery mV:" + str(batt_mV))
    return int(batt_mV/100).to_bytes(2,"little")

def get_parsed_temperature():
    samples_voltage = [0]*NUM_ADC_READINGS
    for i in range(50):
       samples_voltage[i] = ((adcP15.voltage() - 500.0) / 10.0)
    degC = round(statistics.mean(samples_voltage))
    #For the sake of data compression temperatures can only be +100C or -100C. The device more than likely woudlnt function at those temperatures
    if(degC > 100):
       degC = 100
    if(degC < -100):
       degC = -100

    print("Temperature: " + str(degC))

    degC = int(degC).to_bytes(2,"little")
    return degC

def get_parsed_gps_data():
    while(gps_parser.fix_stat == 0):
        print("Waiting for FIX")
        if com.any():
            sentence = com.readline()
            for x in sentence:
                gps_parser.update(chr(x))

    print("Latitude: " + str(gps_parser.latitude[0]))
    print("Longitude: " + str(gps_parser.longitude[0]))
    print("Altitude: " + str(gps_parser.altitude))
    print("Speed: " + str(gps_parser.speed[2]))

    latitude = bytearray(struct.pack(">f", gps_parser.latitude[0]))
    longitude = bytearray(struct.pack(">f", gps_parser.longitude[0]))
    altitude = bytearray(struct.pack(">f", gps_parser.altitude))
    speed = gps_parser.speed[2]

    if(int(speed) > 200):
        speed = 200
    if(int(speed) < 0):
        speed = 0
    speed = int(speed).to_bytes(2,'little')

    return latitude, longitude, altitude, speed

#Gets Accell data in bytes
def get_parsed_accel_data():
   axes = adxl345_sensor.acceleration

   print("x: " + str(axes[0]))
   print("y: " + str(axes[1]))
   print("z: " + str(axes[2]))

   x = bytearray(struct.pack(">f", axes[0]))
   y = bytearray(struct.pack(">f", axes[1]))
   z = bytearray(struct.pack(">f", axes[2]))
   return x,y,z

#Forms the byte array that is sent via SigFox
def format_lat_lon_speed_data(latitude, longitude, speed):
    byteobject = struct.pack(">B", 1) + latitude + longitude + speed
    return byteobject
#Forms the byte array that is sent via SigFox
def format_xy_temp_data(x, y, temperature):
    byteobject = struct.pack(">B", 2) + x + y + temperature
    return byteobject

def format_z_batt_alt(z,alt, battmV):
    byteobject = struct.pack(">B", 3) + z + alt + battmV
    return byteobject

#Variables that hold values to be sent
latitude, longitude, altitude, speed = get_parsed_gps_data()
x, y, z = get_parsed_accel_data()
battmV = get_parsed_battmV()
temperature  = get_parsed_temperature()

packetOne = format_lat_lon_speed_data(latitude, longitude, speed)
print("Packet one: " + str(binascii.hexlify(bytearray(packetOne))))
packetTwo = format_xy_temp_data(x, y, temperature)
print("Packet two: " + str(binascii.hexlify(bytearray(packetTwo))))
packetThree = format_z_batt_alt(z,altitude, battmV)
print("Packet three: " + str(binascii.hexlify(bytearray(packetThree))))
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
sigfox_socket = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
sigfox_socket.setblocking(True)
sigfox_socket.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)
sigfox_socket.send(packetOne)
time.sleep(1)
sigfox_socket.send(packetTwo)
time.sleep(1)
sigfox_socket.send(packetThree)

pycom.rgbled(0xFF0000)
time.sleep(5)
pycom.rgbled(0x00FF00)
deepsleep(600000)