import RPi.GPIO as GPIO
import time

# --- Pin Definitions ---
AIN1 = 20   # right motor
AIN2 = 21
PWMA = 19  # right motor speed

BIN1 = 7   # left motor direction
BIN2 = 8
PWMB = 13   # left motor speed


SPEED = 20  # Default PWM duty cycle (0-100)
TURN_TIME  = 0.45  # Tune until turns are ~90 degrees
STEP_TIME  = 0.3   # One forward step duration

class MotorController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        for pin in [AIN1, AIN2, PWMA, BIN1, BIN2, PWMB]:
            GPIO.setup(pin, GPIO.OUT)


        # Set up PWM on speed pins
        self.pwm_a = GPIO.PWM(PWMA, 1000)  # 1kHz
        self.pwm_b = GPIO.PWM(PWMB, 1000)
        self.pwm_a.start(0)
        self.pwm_b.start(0)

    def _left(self, forward: bool, speed: int):
        GPIO.output(BIN1, GPIO.HIGH if forward else GPIO.LOW)
        GPIO.output(BIN2, GPIO.LOW  if forward else GPIO.HIGH)
        self.pwm_b.ChangeDutyCycle(speed)

    def _right(self, forward: bool, speed: int):
        GPIO.output(AIN1, GPIO.HIGH if forward else GPIO.LOW)
        GPIO.output(AIN2, GPIO.LOW  if forward else GPIO.HIGH)
        self.pwm_a.ChangeDutyCycle(speed)

    def move_forward(self, duration=STEP_TIME):
        self._left(True,  SPEED)
        self._right(True, SPEED)
        time.sleep(duration)
        self.stop()

    def turn_left(self, duration=TURN_TIME):
        self._left(False, SPEED)   # Left wheel backward
        self._right(True, SPEED)   # Right wheel forward
        time.sleep(duration)
        self.stop()

    def turn_right(self, duration=TURN_TIME):
        self._left(True,  SPEED)   # Left wheel forward
        self._right(False, SPEED)  # Right wheel backward
        time.sleep(duration)
        self.stop()

    def turn_around(self):
        self.turn_right()
        self.turn_right()

    def stop(self):
        self.pwm_a.ChangeDutyCycle(0)
        self.pwm_b.ChangeDutyCycle(0)
        GPIO.output(AIN1, GPIO.LOW)
        GPIO.output(AIN2, GPIO.LOW)
        GPIO.output(BIN1, GPIO.LOW)
        GPIO.output(BIN2, GPIO.LOW)

    def cleanup(self):
        self.stop()
        self.pwm_a.stop()
        self.pwm_b.stop()
        GPIO.cleanup()
