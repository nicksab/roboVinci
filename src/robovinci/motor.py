import eventlet
pigpio = eventlet.import_patched('pigpio')
import robovinci.pins as pins

LEFT = 0
RIGHT = 1

_PINS = {
    LEFT: [
        pins.MOTOR_LEFT_FORWARD,
        pins.MOTOR_LEFT_REVERSE,
        pins.MOTOR_LEFT_PWM,
        ],
    RIGHT: [
        pins.MOTOR_RIGHT_FORWARD,
        pins.MOTOR_RIGHT_REVERSE,
        pins.MOTOR_RIGHT_PWM,
        ],
    }

class _Updater(object):
    def __init__(self, side, ttime=2):
        forward, reverse, pwm = _PINS[side]
        self._pin_forward = forward
        self._pin_reverse = reverse
        self._pin_pwm = pwm
        self._current = 0
        self._target = 0
        self._delay = ttime / 200.0
        self._step = 200.0 / ttime
        self._thread = eventlet.spawn_n(self._update)
        self._finished = False
        self._start()

    def _start(self):
        pigpio.set_mode(self._pin_forward, pigpio.OUTPUT)
        pigpio.write(self._pin_forward, 0)
        pigpio.set_mode(self._pin_reverse, pigpio.OUTPUT)
        pigpio.write(self._pin_reverse, 0)
        pigpio.set_mode(self._pin_pwm, pigpio.OUTPUT)
        pigpio.set_PWM_range(self._pin_pwm, 100)
        pigpio.set_PWM_dutycycle(self._pin_pwm, 0)
        self._thread.start()

    def _sign(self, x):
        if x == 0:
            return 0
        elif x < 0:
            return -1
        else:
            return 1

    def _update(self):
        last = time.time()
        current = 0
        while not self._finished:
            eventlet.sleep(self._delay)
            target = self._target
            if current == target:
                last = time.time()
                continue
            now = time.time()
            diff = target - current
            sign = self._sign(diff)
            step = int(min(abs(diff), (now - last) * self._step))
            step = sign * max(1, step)
            current = current + step
            if sign != self._sign(current):
                pigpio.write(self._pin_forward, 0)
                pigpio.write(self._pin_reverse, 0)
            pigpio.set_PWM_dutycycle(self._pin_pwm, abs(current))
            if current == 0:
                pigpio.write(self._pin_forward, 0)
                pigpio.write(self._pin_reverse, 0)
            elif current < 0:
                pigpio.write(self._pin_forward, 0)
                pigpio.write(self._pin_reverse, 1)
            else:
                pigpio.write(self._pin_forward, 1)
                pigpio.write(self._pin_reverse, 0)
            last = now
            self._current = current

    def stop(self):
        self._finished = True

    def get(self):
        return self._current

    def set(self, speed):
        sign = self._sign(speed)
        speed = speed if abs(speed) <= 100 else (sign * 100)
        self._target = speed

class Motor(object):
    def __init__(self, side, ttime=2):
        self._updater = _Updater(side, ttime)

    def get(self):
        return self._updater.get()

    def set(self, speed):
        self._updater.set(speed)

    def __del__(self):
        self._updater.stop()
