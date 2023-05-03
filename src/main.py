# Library imports
from vex import *

# Brain
brain = Brain()

# Controllers
controller_1 = Controller(PRIMARY)

# Motors (A front, C back)
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
left_motor_b = Motor(Ports.PORT5, GearSetting.RATIO_18_1, False)
left_motor_c = Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b, left_motor_c)

right_motor_a = Motor(Ports.PORT20, GearSetting.RATIO_18_1, False)
right_motor_b = Motor(Ports.PORT15, GearSetting.RATIO_18_1, False)
right_motor_c = Motor(Ports.PORT11, GearSetting.RATIO_18_1, True)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, left_motor_c)

# Drivetrain
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 319.19, 320, 255, MM, 1)

# Pre-set variables
left_drive_smart_stopped = False
right_drive_smart_stopped = False

left_drive_smart_speed = 0
right_drive_smart_speed = 0

# ------------------------ Autonomous Start -------------------------------
def autonomous():
    pass


# -------------- Autonomous End & Driver Control Start ---------------------
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped
    
    # Process every 20 milliseconds
    while True:
        forward = controller_1.axis3.position()
        rotate = controller_1.axis1.position()

        left_drive_smart_speed = forward + rotate
        right_drive_smart_speed = forward - rotate

        
        if left_drive_smart_speed < 5 and left_drive_smart_speed > -5:
            if left_drive_smart_stopped:
                left_drive_smart.stop()
                left_drive_smart_stopped = False
        else:
            left_drive_smart_stopped = True

        if right_drive_smart_speed < 5 and right_drive_smart_speed > -5:
            if right_drive_smart_stopped:
                right_drive_smart.stop()
                right_drive_smart_stopped = False
        else:
            right_drive_smart_stopped = True

        
        if left_drive_smart_stopped:
            left_drive_smart.set_velocity(left_drive_smart, PERCENT)
            left_drive_smart.spin(FORWARD)
        if right_drive_smart_stopped:
            right_drive_smart.set_velocity(right_drive_smart, PERCENT)
            right_drive_smart.spin(FORWARD)

# ---------------------- Driver Control End -------------------------------

    # Wait before repeating the controller input process
    wait(20, MSEC)

# Competition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)