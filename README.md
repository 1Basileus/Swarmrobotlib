# Jetboard library
This document describes the Python library for the JetBoard rev.2 (Firmware `0.9.0`).

## Setup
First of all, build the C extension for Python:

``python setup.py build``
   
 After each restart, make sure to load the spidev module (or add it to `/etc/modules`):

 ``sudo modprobe spidev``
 
That's it.

## Usage (JetBoard FW 0.9.0)
The Jetboard class has various functions pretty similar to the BrickPi3 library (with slight modifcations).

All motors are defined portwise.
* `PORT_1`
* `PORT_2`
* `PORT_3`
* `PORT_4`

### Notes


### Set methods
Currently, the library supports the following set methods:
*	`set_motor_speed(motor, value)`
*	`set_motor_position(motor, steps, speed)`
*	`set_led(led, value)`

### Get methods
Following get methods are supported:
*	`get_motor_position(motor)`
*	`get_motor_current(motor)`
*	`get_battery_voltage()`

## Examples
Set motor speed on Port 1 to 80% power.
```python
from jetboard import Jetboard

jb = Jetboard()
jb.set_motor_speed(jb.PORT_1, 80)
```

Move motor on Port 1 for 360 steps at 50% power.
```python
from jetboard import Jetboard

jb = Jetboard()
jb.set_motor_steps(jb.PORT_1, 360, 50)
```

Get the current position of motor on Port 1.
```python
from jetboard import Jetboard

jb = Jetboard()
print(jb.get_motor_position(jb.PORT_1)
```
