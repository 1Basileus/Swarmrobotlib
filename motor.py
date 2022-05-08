class Motor:
    _board = BrickPi3()
    STATUS_POWER = 1

    def __init__(self, port, legacy = False):
        self._port = port
        self._legacy = legacy

        if self._legacy:
            from brickpi3 import BrickPi3
            self._board = BrickPi3()
            self._board.set_motor_limits(self._port, 85)
        else:
            from jetboard import Jetboard
            self._board = Jetboard()

    def set_power(self, pnew):
        if 100< abs(pnew):
            return
        
        if self._legacy:
            self._board.set_motor_power(self._port, pnew)
        else:
            self._board.set_motor_speed(self._port, pnew)

    def stop(self):
        if self._legacy:
            self._board.set_motor_power(self._port, 0)
        else:
            self._board.set_motor_speed(self._port, 0)

class CalibratedMotor(Motor):
    def __init__(self, port, pmin=None, pmax=None, calpow=20, legacy = False):
        super().__init__(port, legacy)

        # calibration power
        self._calpow = calpow
        # minimum position
        self._pmin = pmin
        # maximum position
        self._pmax = pmax

        # if min and max were given, calculate initial position
        if self._pmin and self._pmax:
            self._pinit = (self._pmax + self._pmin) * 0.5
        else:
            # initial position for this motor. will be determined in `calibrate`
            self._pinit = None

    def calibrate(self, verbose=False):
        import time

        CALIBRATE_SLEEP = 0.75

        if verbose: print('Moving to pmin')
        self.set_power(-self._calpow)
        encprev, encnow = 0, None
        while encprev != encnow:
            encprev = encnow
            time.sleep(CALIBRATE_SLEEP)
            if self._legacy:
                encnow = self._board.get_motor_encoder(self._port)
            else:
                encnow = self._board.get_motorposition(self._port)
        self._pmin = encnow
        self.set_power(0)
        if verbose: print('pmin = {}', self._pmin)
        if verbose: print('Moving to pmax')
        self.set_power(self._calpow)
        encprev, encnow = 0, None
        while encprev != encnow:
            encprev = encnow
            time.sleep(CALIBRATE_SLEEP)
            if self._legacy:
                encnow = self._board.get_motor_encoder(self._port)
            else:
                encnow = self._board.get_motor_position(self._port)
        self._pmax = encnow
        self.set_power(0)
        if verbose: print('pmax = {}', self._pmax)

        if self._pmax == self._pmin:
            raise Exception('motor {} does not move'.format(self._port))

        self._pinit = (self._pmax + self._pmin) * 0.5
        if verbose: print('pinit = {}', self._pinit)
        time.sleep(0.5)
        self.to_init_position()

    def calibrate_offset(self, offset, verbose=False):
        import time

        CALIBRATE_SLEEP = 0.75

        if verbose: print('Moving to pmin')
        self.set_power(-self._calpow)
        encprev, encnow = 0, None
        while encprev != encnow:
            encprev = encnow
            time.sleep(CALIBRATE_SLEEP)
            if self._legacy:
                encnow = self._board.get_motor_encoder(self._port)
            else:
                encnow = self._board.get_motor_position(self._port)
        self._pmin = encnow
        self.set_power(0)
        if verbose: print('pmin = {}', self._pmin)
        self._pmax = self._pmin + offset
        if verbose: print('pmax = {}', self._pmax)

        self._pinit = (self._pmax + self._pmin) * 0.5
        if verbose: print('pinit = {}', self._pinit)
        time.sleep(0.5)
        self.to_init_position()


    def set_position(self, pnew):
        if (self._pmin and self._pmax) and not (self._pmin <= pnew <= self._pmax):
            raise Exception('position ({} < {} < {}) is invalid for motor {}'.format(self._pmin, pnew, self._pmax, self._port))
        self._board.set_motor_position(self._port, pnew)

    def to_init_position(self):
        if self._pinit == None:
            raise Exception('initial position for motor {} not known'.format(self._port))
        self.set_position(self._pinit)

    def position_from_factor(self, factor):
        assert self._pinit and self._pmin and self._pmax
        if 0 == factor:
            return self._pinit
        if 0 < factor:
            return self._pinit + (self._pmax - self._pinit) * factor
        return self._pinit - (self._pinit - self._pmin) * abs(factor)
