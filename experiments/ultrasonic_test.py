#! /usr/bin/python

import sys
import time
import pigpio

GPIO_TRIGGER = 14
GPIO_ECHO = 15

LAST_ECHO = 0
ECHO_DURATION = 0

class Ultrasonic(object):
    GPIO_TRIGGER = 14
    GPIO_ECHO = 15

    def __init__(self, decay=0.5):
        self.decay = decay
        self.tick_up = 0
        self.distance = None
        self.echo_cb = None

    def start(self):
        pigpio.set_mode(self.GPIO_TRIGGER, pigpio.OUTPUT)
        pigpio.set_mode(self.GPIO_ECHO, pigpio.INPUT)
        pigpio.write(self.GPIO_TRIGGER, 0)
        self.echo_cb = pigpio.callback(
            self.GPIO_ECHO, pigpio.EITHER_EDGE, self.on_echo)
        pigpio.set_watchdog(self.GPIO_ECHO, 100)

    def stop(self):
        if self.echo_cb is None: return
        pigpio.set_watchdog(self.GPIO_ECHO, 0)
        self.echo_cb.cancel()
        self.echo_cb = None

    def update_distance(self, d1):
        if self.distance is None:
            self.distance = d1
            return
        d = self.distance
        alpha = self.decay
        self.distance = (alpha * d) + ((1 - alpha) * d1)

    def on_echo(self, _, level, tick):
        if level == 2:
            pigpio.gpio_trigger(self.GPIO_TRIGGER)
        if level == 1:
            self.tick_up = tick
        elif level == 0:
            delta = pigpio.tickDiff(self.tick_up, tick)
            self.update_distance(delta * 0.017)

def main(argv=sys.argv):
    pigpio.stop()
    time.sleep(0.5)
    pigpio.start()

    us = Ultrasonic()
    us.start()

    while True:
        time.sleep(1)
        print "Distance : %.1f" % (us.distance,)

    pigpio.stop()
    return 0

if __name__ == '__main__':
    sys.exit(main())
