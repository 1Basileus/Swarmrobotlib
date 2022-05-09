from jetboard import Jetboard
import time

jb = Jetboard()

try:
	while(True):
		jb.set_motor_speed(jb.PORT_1, 80)
		time.sleep(3)
		jb.set_motor_speed(jb.PORT_1, 0)
		time.sleep(3)
except KeyboardInterrupt:
	print('exit')
