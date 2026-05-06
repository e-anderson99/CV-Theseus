# Motor GPIO pins (assumes L298N or similar H-bridge)
LEFT_FORWARD   = 7
LEFT_BACKWARD  = 8
RIGHT_FORWARD  = 20
RIGHT_BACKWARD  = 21
LEFT_PWM_PIN   = 13
RIGHT_PWM_PIN  = 12

MOTOR_SPEED    = 70   # PWM duty cycle (0-100)
TURN_DURATION  = 0.45 # seconds for a 90° turn (tune this!)
STEP_DURATION  = 0.3  # seconds for one forward step

# Camera
FRAME_WIDTH    = 640
FRAME_HEIGHT   = 480
CAMERA_INDEX   = 0

# Symbol detection
CONFIDENCE_THRESHOLD = 0.75

# RL
LEARNING_RATE  = 0.1
DISCOUNT       = 0.9
EPSILON        = 0.2  # exploration rate
