#!/usr/bin/python3
#used to monitor the depth of the creek,includes the creek temp
import sqlite3
import hcsr04sensor.sensor as sensor
import os, glob, time, sys, datetime

# global variables
dbname='/var/www/creek/creeklog.db'

#initiate the temperature sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#set up the location of the sensor in the system
device_folder = glob.glob('/sys/bus/w1/devices/28*')
device_file = [device_folder[0] + '/w1_slave', device_folder[1] + '/w1_slave']

# store the air temp, water temp and depth in the database
def log_depth(airtemp, watertemp, depth):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("INSERT INTO creek VALUES(datetime('now','localtime'),(?),(?),(?))",(airtemp, watertemp, depth,))
    # commit the changes
    conn.commit()
    conn.close()

def read_temp_raw(): #a function that grabs the raw temperature data from the s$
    f_1 = open(device_file[0], 'r')
    lines_1 = f_1.readlines()
    f_1.close()
    f_2 = open(device_file[1], 'r')
    lines_2 = f_2.readlines()
    f_2.close()
    return lines_1 + lines_2

def read_temp(): #a function that checks that the connection was good and strip$
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES' or lines[2].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t='), lines[3].find('t=')
    temp = float(lines[1][equals_pos[0]+2:])/1000*9.0/5.0+32.0, float(lines[3][equals_pos[1]+2:])/1000*9.0/5.0+32.0
    return temp

def read_depth(airtemp):
# '''Example script using hcsr04sensor module for Raspberry Pi'''
    trig_pin = 23
    echo_pin = 24
    unit = 'imperial'  # choices (metric or imperial)
    temperature = airtemp  # Fahrenheit
    round_to = 1
    hole_depth = 35.1  # inches
  #  Create a distance reading with the hcsr04 sensor module
    print "depth here"
    value = sensor.Measurement(trig_pin, echo_pin, temperature, unit, round_to)
    raw_measurement = value.raw_distance()
    print "depth done"
    # Calculate the liquid depth, in inches, of a hole filled
    # with liquid
    liquid_depth = value.depth_imperial(raw_measurement, hole_depth)
    depth = liquid_depth
    return depth

def main():
    temp = read_temp() #get the temp
    depth = read_depth (temp [0])
    watertemp = temp[1]
    airtemp = temp [0]

    print airtemp, "F Outside Temp"
    print watertemp,"F Water Temp"
#   print "Depth = {} inches".format (depth)

    log_depth (airtemp, watertemp, depth)
if __name__ == "__main__":
    main()