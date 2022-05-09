import spiv2 as spi
import Jetson.GPIO as GPIO
import time

from crccheck.crc import Crc16

#reload(spi)

DEVICE_ADDRESS = 0x01

SET_MOTOR_POWER = 0x01
SET_MOTOR_POS_DEG = 0x02
SET_MOTOR_POS_STEP = 0x03
SET_STATUS_LEDS = 0x04

GET_HW_SW_INFO = 0x81
GET_MOTOR_POS = 0x82
GET_MOTOR_CURRENT = 0x83
GET_BATTERY_VOLTAGE = 0x84

class Jetboard(object):
	PORT_1 = 0x01
	PORT_2 = 0x02
	PORT_3 = 0x03
	PORT_4 = 0x04

	LED_RED = 0x01
	LED_BLUE = 0x02
	LED_GREEN = 0x03

	LED_ON = 0xFF
	LED_OFF = 0x00

	def __init__(self):
		self.spi_start()

	def __del__(self):
		self.spi_close()

	def spi_start(self):
		"""
		Starts the SPI communcation and sets up the CS pin.
		"""
		global device	
		device = spi.openSPI(device="/dev/spidev0.0",
	                         mode=0,
	                         speed=1000000,
				             bits = 8)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(24, GPIO.OUT)

	def spi_close(self):
		"""
		Closes the SPI communcation and clears the GPIOs.
		"""
		spi.closeSPI(device)
		GPIO.cleanup()

	def set_motor_speed(self, motor, value):
		"""
		Sets the power ratio of a specific motor.

		The power value ranges from -32768 (CCW, 100%) to +32768 (CW, 100%).
		"""

		if(value > 100 or value < -100):
			raise Exception('Speed out of range.')

		speed = (32767 / 100) * value
		self.spi_send(SET_MOTOR_POWER, motor, speed, 0xff)

	def set_motor_steps(self, motor, steps, speed):
		"""
		Moves a specific motor by an amount of steps.

		The step value ranges from -32768 (CCW) to +32767 (CW) whereas the power level is 0-100.
		"""

		if(steps > 32767 or steps < -32768):
			raise Exception('Steps out of range.')

		if(speed > 100 or speed < 0):
			raise Exception('Speed out of range.')


		speedBinary = (255 / 100) * speed
		self.spi_send(SET_MOTOR_POS_STEP, motor, steps, speedBinary)

	def set_motor_position(self, motor, position):
		"""
		Moves a specific motor to the specified position.
		"""
		steps = self.get_motor_position(motor) - position
		print("pos: ",self.get_motor_position(motor))
		print("wanted: ",position)
		print("steps to go: ",steps)
		self.set_motor_steps(motor, steps, 80)

	def get_motor_position(self, motor):
		"""
		Gets the current position of a specific motor.
		"""
		result = self.spi_transfer(GET_MOTOR_POS, motor, 0x00, 0x00)
		return result[0] << 8 | result[1]

	def get_motor_current(self, motor):
		"""
		Gets the drawn current of a specific motor.
		"""
		result = self.spi_transfer(GET_MOTOR_CURRENT, motor, 0x00, 0x00)
		return result[0] << 8 | result[1]

	def get_battery_voltage(self):
		"""
		Gets the current input voltage (of the battery).
		"""
		result = self.spi_transfer(GET_BATTERY_VOLTAGE, 0x00, 0x00, 0x00)
		return result[0] << 8 | result[1]

	def set_led(self, color, value):
		"""
		Turns a specific led on or off.
		"""
		self.spi_send(SET_STATUS_LEDS, color, value, 0xff)

	def spi_transfer(self, message, target, value, option):
		"""
		This function performs a bidirectional transmission.
		"""

		# Construct the data stream
		data_out = [DEVICE_ADDRESS, message, target, value >> 8, value & 0xff, option]

		# Calculate the CRC checksum of the command
		crc = Crc16.calc(data_out)
		data_out.append(crc >> 8)
		data_out.append(crc & 0xff)

		data_tuple = tuple(data_out)

		# Deassert the CS pin
		GPIO.output(24, GPIO.LOW)

		# Send the data
		spi.transfer(device, data_tuple)

		# Reassert the CS pin
		GPIO.output(24, GPIO.HIGH)

		# Give the Jetboard driver some time to process the comamand (bug in the spidev driver!)
		time.sleep(0.05)

		# Deassert the CS pin again
		GPIO.output(24, GPIO.LOW)

		# Send 8 dummy bytes in order to receive the answer of the Jetboard (normal SPI behaviour)
		result = spi.transfer(device, (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))

		# Reassert the CS pin finally
		GPIO.output(24, GPIO.HIGH)
		time.sleep(0.05)	

		return result;

	def spi_send(self, message, target, value, option):
		"""
		This function sends commands without receiving an answer.
		"""

		# Construct the data stream
		print(value)
		print(option)
		value = int(value)
		option = int(option)
		print(value)
		print(option)
		print()
		data_out = [DEVICE_ADDRESS, message, target, value >> 8, value & 0xff, option]

		# Calculate the CRC checksum of the command
		crc = Crc16.calc(data_out)
		data_out.append(crc >> 8)
		data_out.append(crc & 0xff)

		data_tuple = tuple(data_out)

		# Deassert the CS pin
		GPIO.output(24, GPIO.LOW)

		# Send the data
		spi.transfer(device, data_tuple)

		# Reassert the CS pin
		GPIO.output(24, GPIO.HIGH)
		time.sleep(0.05)
	    
