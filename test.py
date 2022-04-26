from jetboard import Jetboard

jb = Jetboard()

try:
	while(True):
		print(jb.get_battery_voltage())
except KeyboardInterrupt:
	print('exit')
