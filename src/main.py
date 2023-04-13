# Library imports
from vex import *

# Brain
brain = Brain()

# Controllers
controller_1 = Controller(PRIMARY)
controller_2 = Controller(PARTNER)

# Motors
left_motor_a = Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)
left_motor_b = Motor(Ports.PORT5, GearSetting.RATIO_18_1, True)
left_motor_c = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b, left_motor_c)

right_motor_a = Motor(Ports.PORT20, GearSetting.RATIO_18_1, True)
right_motor_b = Motor(Ports.PORT15, GearSetting.RATIO_18_1, True)
right_motor_c = Motor(Ports.PORT11, GearSetting.RATIO_18_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, left_motor_c)

# Drivetrain
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 319.19, 320, 255, MM, 1)

# Pre-set variables
left_motor_a_needs_to_be_stoped_controller = False
right_motor_a_needs_to_be_stoped_controller = False
left_motor_b_needs_to_be_stoped_controller = False
right_motor_b_needs_to_be_stoped_controller = False
left_motor_c_needs_to_be_stoped_controller = False
right_motor_c_needs_to_be_stoped_controller = False

left_motor_a_speed = 0
left_motor_b_speed = 0
left_motor_c_speed = 0
right_motor_a_speed = 0
right_motor_b_speed = 0
right_motor_c_speed = 0

brain.screen.clear_screen()
brain.screen.set_cursor(1, 1)

""" ------------------------ Autonomous Start ------------------------------- """
# Define a function that will be called when the autonomous period starts
def autonomous():




""" -------------- Autonomous End & Driver Control Start --------------------- """
# Define a task that will handle monitoring inputs from controller_1 and controller_2
def driver_control():
    global left_motor_a_needs_to_be_stoped_controller, right_motor_a_needs_to_be_stoped_controller, left_motor_b_needs_to_be_stoped_controller, right_motor_b_needs_to_be_stoped_controller, right_motor_c_needs_to_be_stoped_controller, left_motor_c_needs_to_be_stoped_controller
    
    # Process the controller input every 20 milliseconds
    while True:
        forward = controller_1.axis3.position() * 1 # adjust speed of forward and rotate 
        rotate = controller_1.axis1.position() * 1

        left_drive_smart_speed = (forward - rotate)
        right_drive_smart_speed = (forward + rotate)

            
        # Check if the value is inside of the deadband range
        if right_drive_smart_speed < 2 and right_drive_smart_speed > -2:
            if right_drive_smart_needs_to_be_stoped_controller:
                right_drive_smart.stop()
                right_drive_smart_needs_to_be_stoped_controller = False
        else:
            right_drive_smart_needs_to_be_stoped_controller = True

        if left_drive_smart_speed < 2 and left_drive_smart_speed > -2:
            if left_drive_smart_needs_to_be_stoped_controller:
                left_drive_smart.stop()
                left_drive_smart_needs_to_be_stoped_controller = False
        else:
            left_drive_smart_needs_to_be_stoped_controller = True
        

        # Tell the motor to spin if the values are not in the deadband range
        if right_drive_smart_needs_to_be_stoped_controller:
            right_drive_smart.set_velocity(right_drive_smart_speed, PERCENT)
            right_drive_smart.spin(FORWARD)
        if left_drive_smart_needs_to_be_stoped_controller:
            left_drive_smart.set_velocity(left_drive_smart_speed, PERCENT)
            left_drive_smart.spin(FORWARD)


        # Functions
        if controller_1.buttonA.pressing():
            pass
        elif controller_1.buttonA.pressing():
            pass
        else:
            pass

    # Wait before repeating the controller input process
    wait(20, MSEC)

""" ---------------------- Driver Control End ------------------------------- """

# Competition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)