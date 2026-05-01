import time
import cv2
from motor_control import MotorController
from vision       import VisionSystem
from rl_agent     import QLearningAgent
from symbol_map   import SYMBOL_MAP

def state_from_position(x, y, heading):
    return f"{x},{y},{heading}"

def main():
    motors = MotorController()
    vision = VisionSystem(use_tflite=False)  # swap to True with TFLite model
    agent  = QLearningAgent()

    x, y, heading = 0, 0, "N"   # simple grid position tracker
    step = 0

    try:
        while True:
            # 1. See
            label, confidence, frame = vision.capture_and_detect()
            print(f"[Step {step}] Detected: {label} ({confidence:.2f})")

            # Optional: show camera feed on a connected display
            if frame is not None:
                cv2.imshow("Robot Vision", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # 2. Interpret symbol
            suggested_action, reward = SYMBOL_MAP.get(label, (None, 0))

            # 3. Decide
            state  = state_from_position(x, y, heading)
            action = agent.choose_action(state, suggested_action)
            print(f"  Action: {action} | Reward: {reward}")

            # 4. Act
            if action == "forward":
                motors.move_forward()
            elif action == "left":
                motors.turn_left()
            elif action == "right":
                motors.turn_right()
            elif action == "backward":
                motors.turn_around()
                motors.move_forward()
            elif action == "stop":
                print("Goal reached!")
                break

            # 5. Update position (simplified — use encoders or SLAM for accuracy)
            if action == "forward":
                if heading == "N": y += 1
                elif heading == "S": y -= 1
                elif heading == "E": x += 1
                elif heading == "W": x -= 1
            elif action == "left":
                heading = {"N":"W","W":"S","S":"E","E":"N"}[heading]
            elif action == "right":
                heading = {"N":"E","E":"S","S":"W","W":"N"}[heading]

            # 6. Learn
            next_state = state_from_position(x, y, heading)
            agent.update(state, action, reward, next_state)

            step += 1
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Interrupted. Saving Q-table...")
    finally:
        agent.save()
        motors.cleanup()
        vision.cleanup()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
