#!/usr/bin/python

#TEST ROBOT MAIN CODE

# Must run from ROOT (e.g. launch python IDLE from root, "sudo idle")

# Runs both motors through changes in direction
# + measures distance data from ultrasonic sensor
# + pans servo through min, mid, and max positions
# + detects if switch is closed (aka "BUMP")
# + play sounds out the mini plug port

import time
import RPi.GPIO as gpio
import os

# Use BCM gpio references
# instead of physical pin numbers
gpio.setmode(gpio.BCM)

#RUN pigpio daemon, for servo
os.system('sudo pigpiod')
time.sleep(1)

### SWITCH
swBump = 7
gpio.setup(swBump,gpio.IN)


#### U L T R A S O N I C

print "Init Ultrasonic ..." 


# Define gpio to use on Pi
gpio_TRIGGER = 14  #Pin 8
gpio_ECHO    = 15  #Pin 10  - IMPORTANT NOTE: echo must be connected via voltage divider
#SEE http://www.raspberrypi-spy.co.uk/2013/01/ultrasonic-distance-measurement-using-python-part-2/ for details

# Set pins as output and input
gpio.setup(gpio_TRIGGER,gpio.OUT)  # Trigger
gpio.setup(gpio_ECHO,gpio.IN)      # Echo

# Set trigger to False (Low)
gpio.output(gpio_TRIGGER, False)

    
def ultra_dist():
  print "Check distance"
  # This function measures a distance
  gpio.output(gpio_TRIGGER, True)
  time.sleep(0.00001)
  gpio.output(gpio_TRIGGER, False)
  start = time.time()

### CODE MAY BE GETTING STUCK HERE
  while gpio.input(gpio_ECHO)==0:
    start = time.time()

  while gpio.input(gpio_ECHO)==1:
    stop = time.time()

  elapsed = stop-start
  distance = (elapsed * 34300)/2

  return distance

def ultra_average():
  print "Check AVG distance"
  # This function takes 3 measurements and
  # returns the average.
  distance1=ultra_dist()
  time.sleep(0.1)
  distance2=ultra_dist()
  time.sleep(0.1)
  distance3=ultra_dist()
  distance = distance1 + distance2 + distance3
  distance = distance / 3
  return distance
    
#### END -- U L T R A S O N I C

##### H-BRIDGE SETUP ####
print "Init H-Bridge ..."

lFw = 23  #Left forward pin  -- IN1
lRv = 24  #Left reverse pin -- IN2
lSp = 25  #Left speed control pin (PWM) -- ENA

rFw = 17  #Right foward pin -- IN3
rRv = 27  #Right reverse pin -- IN4
rSp = 22  #Right speed control pin (PWM) -- ENB

gpio.setup(lFw,gpio.OUT)    #Set pins to output mode
gpio.setup(lRv,gpio.OUT)
gpio.setup(lSp,gpio.OUT)

gpio.setup(rFw,gpio.OUT)    
gpio.setup(rRv,gpio.OUT)
gpio.setup(rSp,gpio.OUT)

pwmFreq = 50   #Set PWM frequency to x. (Also affects speed?)

lCurrSp = gpio.PWM(lSp, pwmFreq)  #Create speed controls and set to PWM w freq
rCurrSp = gpio.PWM(rSp, pwmFreq)

gpio.output(lFw, False)  #Set all dir pins LOW
gpio.output(lRv, False)
gpio.output(rFw, False)
gpio.output(rRv, False)

lCurrSp.start(0) #Set starting speed to 0%
rCurrSp.start(0)

def setSpeed(speed):
    if speed >=0 and speed <= 100:
        #lCurrSp.ChangeDutyCycle(speed)
        #rCurrSp.ChangeDutyCycle(speed)
        lCurrSp.start(100)
        rCurrSp.start(100)
        
def setDir(thisDir):
    setSpeed(100)   ### FOR COAST TESTING ONLY
    if thisDir == "fwd": #forward
        print ">>> FWD"
        gpio.output(lFw, True)
        gpio.output(rFw, True)
    elif thisDir == "rev": #reverse
        print "<<< REV"
        gpio.output(lRv, True)
        gpio.output(rRv, True)
    elif thisDir == "right": #Fwd left, rev right
        print ">>> RIGHT >>>"
        gpio.output(lFw, True)
        gpio.output(rRv, True)
    elif thisDir == "left": #Fwd right, rev left
        print "<<< LEFT <<<"
        gpio.output(rFw, True)
        gpio.output(lRv, True)

    elif thisDir == "brake": #flip Fw/Rev on both sides true for short period
        gpio.output(lFw, True)
        gpio.output(lRv, True)
        gpio.output(rFw, True)
        gpio.output(rRv, True)
        time.sleep(2) #pause briefly
        gpio.output(lFw, False) #Set all outputs to low - 'coast'
        gpio.output(lRv, False)
        gpio.output(rFw, False)
        gpio.output(rRv, False)
    elif thisDir == "coast": #all false
        lCurrSp.stop()
        rCurrSp.stop()
        gpio.output(lFw, False) #Set all outputs to low - 'coast'
        gpio.output(lRv, False)
        gpio.output(rFw, False)
        gpio.output(rRv, False)
        
    else:
        print "Unknown direction."

    #Check distance
    dist = ultra_dist()
    print "Avg distance : %.1f" % dist

    #Check button
    if  (gpio.input(swBump)):
      print "!! BUMP DETECTED !!"
      os.system('mpg321 "./sounds/Sci Fi Beep 11.mp3" &')
    else:
      print "OK - NO BUMP"

### SERVO SETUP ###
print "Init servo..."

import pigpio   #NOTE! MUST RUN pigpiod as root, pigpio daemon

#Set limits - TEST for different servos!
# For TS-51: 600, 1400, 2200
servMax = 2200
servMid = 1400
servMin = 600

delayTime1 = 0.01
servStep = 20
servPin1 = 18 #GPIO 18

#Reset pigpio
pigpio.stop()
time.sleep(.5)
pigpio.start()

#Initialize PWM values
pigpio.set_PWM_frequency(servPin1, 50)  
pigpio.set_PWM_range(servPin1, servMax)
pigpio.set_servo_pulsewidth(servPin1, servMin) #pulsewidth sets position - start at minimum


### END SERVO SETUP


### MAIN LOOP ###
try:
    
    while True:
        print "Play sound"
        os.system('mpg321 "./sounds/Sci Fi Beep 02.mp3" &')
        
        setDir("fwd")
        pigpio.set_servo_pulsewidth(servPin1, servMin)
        time.sleep(2)
        
        setDir("coast")
        time.sleep(0.5)
        
        setDir("rev")
        pigpio.set_servo_pulsewidth(servPin1, servMid)
        time.sleep(2)
        
        setDir("coast")
        time.sleep(0.5)
        
        print "Play sound"
        os.system('mpg321 "./sounds/Sci Fi Beep 09.mp3" &')
        
        setDir("right")
        pigpio.set_servo_pulsewidth(servPin1, servMax)
        time.sleep(1)
        
        setDir("coast")
        time.sleep(0.5)

        print "Play sound"
        os.system('mpg321 "./sounds/Nuclear Scanner.mp3" &')
        
        setDir("left")
        pigpio.set_servo_pulsewidth(servPin1, servMid)
        time.sleep(1)
        
        setDir("coast")
        time.sleep(0.5)
                        
except KeyboardInterrupt:    #Stop on keyboard interrupt, control-C
    
    print ">>> Stopped <<<"
    gpio.output(lFw, False)  #Set all pins to low
    gpio.output(lRv, False)
    lCurrSp.stop()
    
    gpio.output(rFw, False)
    gpio.output(rRv, False)
    rCurrSp.stop()

finally:
    print ">>> Final Cleanup <<<"
    #MOTOR and ULTRA CLEANUP
    gpio.cleanup()

    #SERVO CLEANUP
    pigpio.set_servo_pulsewidth(servPin1,0) #set to 0 to stop PWM
    pigpio.stop()
    

print "DONE"

    
    
