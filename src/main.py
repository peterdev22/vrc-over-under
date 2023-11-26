# Library imports
from vex import *
import urandom

# ------------------------
# Code by Eric & Peter (mostly Eric)
# Team 75477M 'Frij'
# Over Under 2023-2024
# ------------------------

# Wiring Guide
# - drivetrain: left a: #1;  left b: #11;  left c: #12;  right a: #10;  right b: #19  right c: #21;
# - puncher: #4, #14
# - inertial sensor: #3
# - gps sensor: #8
# - optial sensor: #7
# - wings: a; blocker: c


# Brain
brain = Brain()

# Controllers
controller_1 = Controller(PRIMARY)

# Motors (A front, C back)
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_6_1, True)
left_motor_b = Motor(Ports.PORT11, GearSetting.RATIO_6_1, True)
left_motor_c = Motor(Ports.PORT12, GearSetting.RATIO_6_1, True)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b, left_motor_c)

right_motor_a = Motor(Ports.PORT18, GearSetting.RATIO_6_1, False)
right_motor_b = Motor(Ports.PORT21, GearSetting.RATIO_6_1, False)
right_motor_c = Motor(Ports.PORT19, GearSetting.RATIO_6_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

puncher_a = Motor(Ports.PORT4, GearSetting.RATIO_36_1, True)
puncher_b = Motor(Ports.PORT14, GearSetting.RATIO_36_1, False)
puncher = MotorGroup(puncher_a, puncher_b)

# Sensor
inertial = Inertial(Ports.PORT2)
gps = Gps(Ports.PORT8, -120.00, -125.00, MM, -95) #- x-offset, y-offset, angle offset
optical = Optical(Ports.PORT7)

# Drivetrain
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 299.24, 260, 230, MM, 0.6)

# Pneumatics
wings = DigitalOut(brain.three_wire_port.a)
blocker = DigitalOut(brain.three_wire_port.c)
# Pre-set variables
left_drive_smart_stopped = 0
right_drive_smart_stopped = 0
left_drive_smart_speed = 0
right_drive_smart_speed = 0

puncher.set_position(0,DEGREES)
puncher.set_velocity(100, PERCENT)
inertial.calibrate()
gps.calibrate()
inertial.set_heading(0, DEGREES)
sensor_status = 0
matchload = 0
wings_status = 0
blocker_status = 0

wings.set(False)
blocker.set(blocker_status)

brain.screen.draw_image_from_file("begin.png", 0, 4)
team_position = " "

# team and side choosing
def team_choosing():
    team = ""
    position = ""
    while True:
        if controller_1.buttonL1.pressing():
            brain.screen.draw_image_from_file( "red_offence_confirmed.png", 0, 4)
            while controller_1.buttonL1.pressing():
                wait(5, MSEC)
            return "red_offence"
        elif controller_1.buttonL2.pressing():
            brain.screen.draw_image_from_file( "red_defence_confirmed.png", 0, 4)
            while controller_1.buttonL2.pressing():
                wait(5, MSEC)
            return "red_defence"
        elif controller_1.buttonR1.pressing():
            brain.screen.draw_image_from_file( "blue_offence_confirmed.png", 0, 4)
            while controller_1.buttonR1.pressing():
                wait(5, MSEC)
            return "blue_offence"
        elif controller_1.buttonR2.pressing():
            brain.screen.draw_image_from_file( "blue_defence_confirmed.png", 0, 4)
            while controller_1.buttonR2.pressing():
                wait(5, MSEC)
            return "blue_defence"
        if brain.screen.pressing() and 8 <= brain.screen.y_position() <= 26:
            # Team choosing
            if 139 <= brain.screen.x_position() <= 240:
                # Red
                team = "red"
                brain.screen.draw_image_from_file( "red_begin.png", 0, 4)
                position = ""
            elif 249 <= brain.screen.x_position() <= 351:
                # Blue
                team = "blue"
                brain.screen.draw_image_from_file("blue_begin.png", 0, 0)
                position = ""
            elif 358 <= brain.screen.x_position() <= 461:
                # Skill
                team = "skill"
                brain.screen.draw_image_from_file( "skill_begin.png", 0, 0)
                position = ""
        elif brain.screen.pressing() and 19 <= brain.screen.x_position() <= 138 and not team == "":
            # Position sellction
            if brain.screen.y_position() > 52 and brain.screen.y_position() < 73:
                if team == "red":
                    # Red offence
                    brain.screen.draw_image_from_file( "red_offence.png", 0, 4)
                elif team == "blue":
                    # Blue offence
                    brain.screen.draw_image_from_file( "blue_offence.png", 0, 0)
                elif team == "skill":
                    # Skill confirm
                    brain.screen.draw_image_from_file( "skill_confirmed.png", 0, 0)
                    return "skill"
                position = "offence"
            elif brain.screen.pressing() and 85 <= brain.screen.y_position() <= 107 and not team == "":
                if team == "red":
                    # Red defence
                    brain.screen.draw_image_from_file( "red_defence.png", 0, 4)
                elif team == "blue":
                    # Blue defence
                    brain.screen.draw_image_from_file( "blue_defence.png", 0, 0)
                position = "defence"
            elif brain.screen.pressing() and 120 <= brain.screen.y_position() <= 142 and not team == "":
                if team == "red":
                    # Red confirm
                    if position == "offence":
                        # Red offence confirm
                        brain.screen.draw_image_from_file( "red_offence_confirmed.png", 0, 4)
                    elif position == "defence":
                        # Red defence confirm
                        brain.screen.draw_image_from_file( "red_defence_confirmed.png", 0, 4)
                elif team == "blue":
                    # Blue confirm
                    if position == "offence":
                        # Blue offence confirm
                        brain.screen.draw_image_from_file( "blue_offence_confirmed.png", 0, 0)
                    elif position == "defence":
                        # Blue defence confirm
                        brain.screen.draw_image_from_file( "blue_defence_confirmed.png", 0, 0)
                return team + "_" + position
            while brain.screen.pressing():
                wait(5, MSEC)
        wait(5, MSEC)

#def pid turning
def drivetrain_turn(target_angle):
    kp = 0.18
    ki = 0.139
    kd = 0.05
    previous_error = 0
    integral = 0
    inertial.set_heading(0.5, DEGREES)
    drivetrain.turn(RIGHT)
    drivetrain.set_stopping(HOLD)
    current_angle = inertial.heading(DEGREES)
    while not (target_angle - 0.5 < current_angle < target_angle + 0.5):
        error = target_angle - current_angle
        integral += error
        integral = max(min(integral, 30), -30)
        derivative = error - previous_error
        pid_output = (kp * error) + (ki * integral) + (kd * derivative)
        previous_error = error
        pid_output = max(min(pid_output, 100), -100)
        drivetrain.set_turn_velocity(pid_output, PERCENT)
        current_angle = inertial.heading(DEGREES)
    drivetrain.stop()


# gps sensor def
def goto(x_cord, y_cord, speed, wait):
    b = x_cord - gps.x_position(MM)
    c = y_cord - gps.y_position(MM)
    if abs(b) < 1 and abs(c) < 1:
        pass
    else:
        a = math.sqrt(b**2 + c**2)
        angle = math.asin((math.sin(90 / 180.0 * math.pi) * b) / a) / math.pi * 180
        if c < 0:
            angle = 180 - angle
            drivetrain.turn_to_heading(angle, DEGREES)
            drivetrain.drive_for(FORWARD, a, MM, speed, PERCENT, wait = wait)
          
# Autonomous def
def autonomous():
    #defencive
    # - start at the RIGHT SIDE of the Alliance station!!!!!!
    drivetrain.set_stopping(BRAKE)
    if team_position == "red_defence" or team_position == "blue_defence":
        drivetrain.set_timeout(1, SECONDS)
        drivetrain.drive_for(REVERSE, 300, MM, 30, PERCENT, wait = True)
        wings.set(True)
        drivetrain.drive_for(FORWARD, 450, MM, 20, PERCENT, wait = True)
        right_drive_smart.spin_for(FORWARD, 7, TURNS)
        right_drive_smart.spin_for(FORWARD, 3, TURNS)
        right_drive_smart.spin_for(REVERSE, 1, TURNS)
        drivetrain.drive_for(FORWARD, 350, MM, 30, PERCENT)
        blocker.set(True)
        
    elif team_position == "red_offence" or team_position == "blue_offence":
        drivetrain.set_timeout(1, SECONDS)
        wings.set(True)
        drivetrain.drive_for(FORWARD, 450, MM, 20, PERCENT, wait = True)
        right_drive_smart.spin_for(FORWARD, 7, TURNS)
        right_drive_smart.spin_for(FORWARD, 3, TURNS)
        wings.set(False)
        right_drive_smart.spin_for(REVERSE, 1.6, TURNS)
        drivetrain.drive_for(FORWARD, 1000, MM, 50, PERCENT, wait = True)
        drivetrain.drive_for(REVERSE, 700, MM, 30, PERCENT, wait = True)
        wait(1, SECONDS)
        drivetrain.drive_for(FORWARD, 700, MM, 50, PERCENT, wait = True)
        drivetrain.drive_for(REVERSE, 700, MM, 30, PERCENT, wait = True)
        
    elif team_position == "skill":
        time = 0
        sensor_status = 1
        wings.set(True)
        wait(450, MSEC)
        wings.set(False)
        left_drive_smart.spin_for(FORWARD, 1.5, TURNS, 20, PERCENT)
        drivetrain.drive_for(FORWARD, 280, MM, 40, PERCENT, wait = True)
        left_drive_smart.spin_for(FORWARD, 1, TURNS, 20, PERCENT)
        drivetrain.drive_for(FORWARD, 450, MM, 70, PERCENT, wait = True)
        drivetrain.drive_for(REVERSE, 400, MM, 30, PERCENT, wait = True)
        right_drive_smart.spin_for(REVERSE, 2.15, TURNS, 20, PERCENT)
        left_drive_smart.spin_for(REVERSE, 0.1, TURNS, 20, PERCENT)
        puncher.spin_for(REVERSE, 80, DEGREES, wait = False)
        puncher.set_stopping(HOLD)
        time = brain.timer.time(SECONDS)
        while brain.timer.time(SECONDS) < time +27:
            if optical.is_near_object():
                puncher.spin_for(REVERSE, 180, DEGREES, wait = True)
        puncher.spin_for(REVERSE, 180, DEGREES, wait = False)
        drivetrain.drive_for(FORWARD, 200, MM, 20, PERCENT, wait = True)
        left_drive_smart.spin_for(FORWARD, 2, TURNS, 20, PERCENT)
        drivetrain.drive_for(FORWARD, 750, MM, 50, PERCENT, wait = True)
        right_drive_smart.spin_for(FORWARD, 1.15, TURNS, 20, PERCENT)
        puncher.set_stopping(COAST)
        drivetrain.drive_for(FORWARD, 1950, MM, 70, PERCENT, wait = True)
        drivetrain_turn(225)
        drivetrain.drive_for(FORWARD, 1400, MM, 40, PERCENT, wait = True)
        right_drive_smart.spin_for(REVERSE, 1.8, TURNS, 20, PERCENT, wait = False)
        left_drive_smart.spin_for(FORWARD, 2, TURNS, 20, PERCENT, wait = True)
        for i in range(2):
            wings.set(True)
            drivetrain.drive_for(FORWARD, 900, MM, 70, PERCENT, wait = True)
            wings.set(False)
            drivetrain.drive_for(REVERSE, 900, MM, 40, PERCENT, wait = True)
            right_drive_smart.spin_for(FORWARD, 0.5, TURNS, 20, PERCENT, wait = False)
            wait(500, MSEC)
        left_drive_smart.spin_for(REVERSE, 1.5, TURNS, 20, PERCENT, wait = False)
        drivetrain.drive_for(FORWARD, 500, MM, 20, PERCENT, wait = True)
        left_drive_smart.spin_for(FORWARD, 2.5, TURNS, 20, PERCENT, wait = False)
        drivetrain.drive_for(FORWARD, 300, MM, 20, PERCENT, wait = True)
        left_drive_smart.spin_for(FORWARD, 1, TURNS, 20, PERCENT, wait = False)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
        
    else:
        controller_1.screen.print("team position not selected")

#  Driver Control def
# - controller map: left joystick: moving, L1 trigger: wings(hold)
# - R1 trigger: puncher, R2 trigger: change puncher status(switch)
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped, sensor_status, wings_status, matchload, blocker_status
    drivetrain.set_stopping(COAST)
    time = brain.timer.time(SECONDS)
    if team_position == "red_defence" or team_position == "blue_defence":
        sensor_status = 1
        blocker_status = 0
        wings_status = 0
        puncher.spin_for(REVERSE, 80, DEGREES, wait = False)
        puncher.set_stopping(HOLD)
    elif team_position == "red_offence" or team_position == "blue_offence":
        sensor_status = 0
    elif team_position == "skill":
        sensor_status = 1
        wings.set(True)
        wait(450, MSEC)
        wings.set(False)
        left_drive_smart.spin_for(FORWARD, 1.5, TURNS, 20, PERCENT)
        drivetrain.drive_for(FORWARD, 280, MM, 40, PERCENT, wait = True)
        left_drive_smart.spin_for(FORWARD, 1, TURNS, 20, PERCENT)
        drivetrain.drive_for(FORWARD, 450, MM, 70, PERCENT, wait = True)
        drivetrain.drive_for(REVERSE, 400, MM, 30, PERCENT, wait = True)
        right_drive_smart.spin_for(REVERSE, 2.15, TURNS, 20, PERCENT)
        left_drive_smart.spin_for(REVERSE, 0.1, TURNS, 20, PERCENT)
        puncher.spin_for(REVERSE, 80, DEGREES, wait = False)
        puncher.set_stopping(HOLD)
        time = brain.timer.time(SECONDS)
        while brain.timer.time(SECONDS) < time +27:
            if optical.is_near_object():
                puncher.spin_for(REVERSE, 180, DEGREES, wait = True)
        puncher.spin_for(REVERSE, 180, DEGREES, wait = False)
        drivetrain.drive_for(FORWARD, 200, MM, 20, PERCENT, wait = True)
        puncher.set_stopping(COAST)
    # Process every 20 milliseconds
    while True:
    # Drive Train
        rotate = 55*math.sin(0.007*controller_1.axis4.position())
        if blocker_status == 0 and controller_1.axis3.position() < -85:
            forward = -85
        elif blocker_status == 0 and controller_1.axis3.position() > 90:
            forward = 90
        elif blocker_status == 1 and controller_1.axis3.position() < -65:
            forward = -65
        elif blocker_status == 1 and controller_1.axis3.position() > 65:
            forward = 65
        else:
            forward = controller_1.axis3.position()
            
        left_drive_smart_speed = forward + rotate
        right_drive_smart_speed = forward - rotate

        if left_drive_smart_speed < 3 and left_drive_smart_speed > -3:
            if left_drive_smart_stopped:
                left_drive_smart.stop()
                left_drive_smart_stopped = 0
        else:
            left_drive_smart_stopped = 1
        if right_drive_smart_speed < 3 and right_drive_smart_speed > -3:
            if right_drive_smart_stopped:
                right_drive_smart.stop()
                right_drive_smart_stopped = 0
        else:
            right_drive_smart_stopped = 1

        if left_drive_smart_stopped:
            left_drive_smart.set_velocity(left_drive_smart_speed, PERCENT)
            left_drive_smart.spin(FORWARD)
        if right_drive_smart_stopped:
            right_drive_smart.set_velocity(right_drive_smart_speed, PERCENT)
            right_drive_smart.spin(FORWARD)
    # puncher control 
        if controller_1.buttonL1.pressing():
            puncher.set_velocity(100, PERCENT)
            puncher.spin_for(REVERSE, 180, DEGREES, wait = True)
        elif controller_1.buttonL2.pressing():
            sensor_status = not sensor_status
            if sensor_status:
                controller_1.rumble(".")
            else:
                controller_1.rumble("-")
            while controller_1.buttonL2.pressing():
                wait(20, MSEC)
        elif optical.is_near_object() and sensor_status:
            puncher.set_velocity(100, PERCENT)
            puncher.spin_for(REVERSE, 180, DEGREES, wait = True)
        elif controller_1.buttonX.pressing():
            if not matchload:
                puncher.spin_for(REVERSE, 80, DEGREES, wait = True)
                puncher.set_stopping(HOLD)
                sensor_status = True
            elif matchload:
                puncher.set_stopping(COAST)
            matchload = not matchload
            while controller_1.buttonX.pressing():
                wait(20, MSEC)
        else:
            puncher.stop()
    # wings control
        if controller_1.buttonR1.pressing():
            wings.set(not wings_status)
        elif controller_1.buttonR2.pressing():
            wings_status = not wings_status
            while controller_1.buttonR2.pressing():
                wait(20, MSEC)
        else:
            wings.set(wings_status)
    #blocker control        
        if controller_1.buttonY.pressing():
            blocker_status = not blocker_status
            while controller_1.buttonY.pressing():
                wait(20, MSEC)
        else:
            blocker.set(blocker_status)
    #driving mode change
        if controller_1.buttonUp.pressing():
            drivetrain.set_stopping(BRAKE)
        if controller_1.buttonDown.pressing():
            drivetrain.set_stopping(COAST)
        
        if controller_1.buttonA.pressing():
            drivetrain_turn(45)
            while controller_1.buttonA.pressing():
                wait(20, MSEC)
    # Wait before repeating the controller input process
    wait(20, MSEC)

#choose team
team_position = team_choosing()
# Competition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)