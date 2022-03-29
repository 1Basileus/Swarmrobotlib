from .motor import CalibratedMotor, Motor
import cv2

class SwarmRobot:
    def __init__(self):
        self._drive_motor = Motor(Motor._bp.PORT_B)
        self._steer_motor = CalibratedMotor(Motor._bp.PORT_D, calpow=40)
        self._fork_lift_motor = CalibratedMotor(Motor._bp.PORT_C, calpow=50)
        self._fork_tilt_motor = CalibratedMotor(Motor._bp.PORT_A, calpow=40)
        with open('/etc/hostname', 'r') as hostname:
            self._name = hostname.read().strip()

    def __del__(self):
        self._steer_motor.to_init_position()
        self.stop_all()

    def name(self):
        return self._name

    def change_drive_power(self, pnew):
        self._drive_motor.change_power(pnew)

    def set_drive_power(self, pnew):
        self._drive_motor.set_power(pnew)

    def set_drive_steer(self, pnew):
        pos = self._steer_motor.position_from_factor(pnew)
        self._steer_motor.set_position(pos)

    def calibrate(self, calibrate_forklift=False, verbose=False):
        print('Calibrating steering')
        self._steer_motor.calibrate(verbose)
        if(calibrate_forklift):
            print('Calibrating forklift lift motor')
            self._fork_lift_motor.calibrate(verbose)
            print('Calibrating forklift tilt motor')
            self._fork_tilt_motor.calibrate_offset(53000,verbose)

    def stop_all(self):
        self._drive_motor.stop()
        self._steer_motor.stop()
