# test_motors.py
from motor_control import MotorController
import time

m = MotorController()

print("Forward"); m.move_forward(1.0); time.sleep(0.5)
print("Left");    m.turn_left();       time.sleep(0.5)
print("Right");   m.turn_right();      time.sleep(0.5)

m.cleanup()
