from .motor import CalibratedMotor, Motor
from .pidcontroller import PIDController
from .line_tracking import LineTracker
from threading import Thread
import cv2

class SwarmRobot:
    def __init__(self):
        self._drive_motor = Motor(Motor._bp.PORT_B)
        self._steer_motor = CalibratedMotor(Motor._bp.PORT_D, calpow=40)
        self._fork_lift_motor = CalibratedMotor(Motor._bp.PORT_C, calpow=50)
        self._fork_tilt_motor = CalibratedMotor(Motor._bp.PORT_A, calpow=40)

        # Camera
        self._camera = cv2.VideoCapture(0)

        # Linetracking
        self._track_process = None
        self._track_active = False
        self._pid_controller = PIDController(verbose=False)
        self._line_tracker = LineTracker(self._camera.get(cv2.CAP_PROP_FRAME_WIDTH), self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT), preview=False, debug=False)

    def __del__(self):
        self._steer_motor.to_init_position()
        self.stop_all()

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

    def _setup_autopilot(self):
        from time import sleep

        def follow():
            try:
                while True:
                    if not self._track_active:
                        sleep(0.5)

                    if self._track_active:
                        _,frame = self._camera.read()
                        pos = self._line_tracker.track_line(frame)
                        if pos != None:
                            steer = self._pid_controller.pid(pos)
                            self.set_drive_steer(steer)
            except KeyboardInterrupt:
                self._bot.stop_all()
            finally:
                self._bot.stop_all()

        self._track_process = Thread(group=None, target=follow, daemon=True)
        self._track_process.start()

    def get_autopilot_state(self):
        return self._track_active

    def set_autopilot_state(self, active:bool):
        self._track_active = active
        if(active and self._track_process == None):
            self._setup_autopilot()

    def _setup_classifier(self):
        from .classifier import Classifier
