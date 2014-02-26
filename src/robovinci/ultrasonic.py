import eventlet
from eventlet.green import threading
pigpio = eventlet.import_patched('pigpio')
import robovinci.pins as pins

class Ultrasonic(object):
    STATE_QUIET = 0
    STATE_ACTIVE = 1

    def __init__(self):
        self._cv = threading.Condition()
        self._state = self.STATE_QUIET
        self._tick_up = 0
        self._distance = 0.0
        self._echo_cb = None
        self._start()

    def _start(self):
        pigpio.set_mode(pins.ULTRASONIC_TRIGGER, pigpio.OUTPUT)
        pigpio.set_mode(pins.ULTRASONIC_ECHO, pigpio.INPUT)
        pigpio.write(pins.ULTRASONIC_TRIGGER, 0)
        self._echo_cb = pigpio.callback(
            pins.ULTRASONIC_ECHO, pigpio.EITHER_EDGE, self._on_echo)

    def __del__(self):
        cb = self._echo_cb
        if cb is not None:
            cb.cancel()

    def _on_echo(self, _, level, tick):
        if self._state != self.STATE_ACTIVE:
            return
        elif level == 2:
            self._finish_echo(-1.0)
        elif level == 1:
            self._tick_up = tick
        elif level == 0:
            delta = pigpio.tickDiff(self._tick_up, tick)
            self._finish_echo(delta * 0.017)

    def _finish_echo(self, distance):
        try:
            pigpio.set_watchdog(pins.ULTRASONIC_ECHO, 0)
            self._cv.acquire()
            self._state = self.STATE_QUIET
            self._distance = distance
            self._cv.notifyAll()
        finally:
            self._cv.release()

    def _activate(self):
        self._state = self.STATE_ACTIVE
        pigpio.gpio_trigger(pins.ULTRASONIC_TRIGGER)

    def measure(self):
        distance = -1.0
        try:
            self._cv.acquire()
            if self._state == self.STATE_QUIET:
                self._activate()
            self._cv.wait()
            distance = self._distance
        finally:
            self._cv.release()
        return distance

    def __call__(self):
        return self.measure()
