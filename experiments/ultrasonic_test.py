#! /usr/bin/python

import sys
import time
import pigpio

GPIO_TRIGGER = 14
GPIO_ECHO = 15

def read_ultrasonic():
    pigpio.gpio_trigger(GPIO_TRIGGER)
    stop = start = time.time()
    while pigpio.read(GPIO_ECHO) == 0:
        start = time.time()
    while pigpio.read(GPIO_ECHO) == 1:
        stop = time.time()
    elapsed = stop - start
    distance = elapsed * 34000
    distance = distance / 2
    return distance    

def main(argv=sys.argv):
    pigpio.stop()
    time.sleep(0.5)
    pigpio.start()

    pigpio.set_mode(GPIO_TRIGGER, pigpio.OUTPUT)
    pigpio.set_mode(GPIO_ECHO, pigpio.INPUT)
    pigpio.write(GPIO_TRIGGER, 0)
    time.sleep(0.5)

    distance = read_ultrasonic()
    print "Distance : %.1f" % (distance,)

    pigpio.stop()
    return 0

if __name__ == '__main__':
    sys.exit(main())
