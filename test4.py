from jetboard import Jetboard
import time
from motor import CalibratedMotor

jb = Jetboard()

#motor = CalibratedMotor(jb.PORT_1)
#motor.calibrate()

jb.set_motor_steps(jb.PORT_1, -100, 80)
