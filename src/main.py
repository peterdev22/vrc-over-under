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
# - wings: a


# Brain
brain = Brain()

# Controllers
controller_1 = Controller(PRIMARY)

# Motors (A front, C back)
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_6_1, True)
left_motor_b = Motor(Ports.PORT11, GearSetting.RATIO_6_1, True)
left_motor_c = Motor(Ports.PORT12, GearSetting.RATIO_6_1, True)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b, left_motor_c)

right_motor_a = Motor(Ports.PORT10, GearSetting.RATIO_6_1, False)
right_motor_b = Motor(Ports.PORT21, GearSetting.RATIO_6_1, False)
right_motor_c = Motor(Ports.PORT19, GearSetting.RATIO_6_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

puncher_a = Motor(Ports.PORT4, GearSetting.RATIO_36_1, True)
puncher_b = Motor(Ports.PORT14, GearSetting.RATIO_36_1, False)
puncher = MotorGroup(puncher_a, puncher_b)

# Drivetrain
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 299.24, 260, 230, MM, 0.6)


# Sensor
inertial = Inertial(Ports.PORT3)
gps = Gps(Ports.PORT8, -110, -150, MM, 180) #- x-offset, y-offset, angle offset
optical = Optical(Ports.PORT7)

# Pneumatics
wings = DigitalOut(brain.three_wire_port.a)

# Pre-set variables
left_drive_smart_stopped = 0
right_drive_smart_stopped = 0
left_drive_smart_speed = 0
right_drive_smart_speed = 0

puncher.set_position(0,DEGREES)
inertial.calibrate()
gps.calibrate()
inertial.set_heading(0, DEGREES)
sensor_status = 0
matchload = 0
wings_status = 0

wings.set(False)

brain.screen.draw_image_from_file("begin.png", 0, 4)
team_position = " "

# team and side choosing
def team_choosing():
    team = ""
    position = ""
    while True:
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

# turing def
# - Direction = RIGHT or LEFT
def drivetrain_turn(target_angle, Direction):
    inertial.set_heading(0.0, DEGREES)
    drivetrain.turn(Direction)
    current_angle = inertial.heading(DEGREES)
    if Direction == LEFT:
            target_angle = 360 - target_angle
    while not (target_angle + 0.5 > current_angle > target_angle - 0.5):
        if Direction == LEFT:
            turn_angle = current_angle - target_angle
        else:
            turn_angle = target_angle - current_angle
        if turn_angle < 0:
            turn_angle += 360
        current_angle = inertial.heading(DEGREES)
        drivetrain.set_turn_velocity(turn_angle*0.7+5, RPM)
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
            drivetrain.turn_for(RIGHT, angle, DEGREES)
            drivetrain.drive_for(FORWARD, a, MM, speed, PERCENT, wait = wait)
          
# Autonomous def
def autonomous():
    #defencive
    # - start at the RIGHT SIDE of the Alliance station!!!!!!
    # - left back wheel on the second connection of the foam tile, "r" on the front ramp lined up with the connection line, 
    # - preload triball line up with the right edge of the robot(skill: red defence position, alliance triball on the middle left of the left side of the goal)
    if team_position == "red_defence" or team_position == "blue_defence":
        drivetrain.set_timeout(1, SECONDS)
        drivetrain.drive_for(FORWARD, 1300, MM, 100, PERCENT, wait = True)
        drivetrain.drive_for(REVERSE, 400, MM, 30, PERCENT, wait = True)
        drivetrain.turn_for(RIGHT, 180, DEGREES)
        drivetrain.drive_for(REVERSE, 130, MM, 10, PERCENT, wait = True)
        
    elif team_position == "red_offence" or team_position == "blue_offence":
        drivetrain.drive_for(FORWARD, 1300, MM, 100, PERCENT, wait = True)
        drivetrain.drive_for(REVERSE, 400, MM, 30, PERCENT, wait = True)
        
    elif team_position == "skill":
        time = 0
        '''
        puncher.spin_for(REVERSE, 80, DEGREES, wait = False)
        puncher.set_stopping(HOLD)
        drivetrain.drive_for(Reverse, 300, MM, 70, PERCENT, wait = True)
        drivetrain.turn_for(LEFT, 75, DEGREES)
        drivetrain.drive_for(Reverse, 100, MM, 70, PERCENT, wait = True)
        puncher.spin(REVERSE)
        '''
        drivetrain.set_timeout(1, SECONDS)
        drivetrain.drive_for(FORWARD, 1300, MM, 100, PERCENT, wait = True)
        puncher.spin_for(REVERSE, 80, DEGREES, wait = False)
        puncher.set_stopping(HOLD)
        drivetrain.drive_for(REVERSE, 400, MM, 30, PERCENT, wait = True)
        drivetrain.turn_for(RIGHT, 180, DEGREES)
        drivetrain.drive_for(REVERSE, 130, MM, 10, PERCENT, wait = True)
        '''
        for i in range(34):
            puncher.spin_for(REVERSE, 180, DEGREES, wait = True)'''
        time = brain.timer.time(SECONDS)
        while brain.timer.time(SECONDS) < time +30:
            if optical.is_near_object():
                puncher.spin_for(REVERSE, 180, DEGREES, wait = True)
        puncher.set_stopping(COAST)
        puncher.spin_for(REVERSE, 180, DEGREES, wait = False)
        drivetrain.drive_for(FORWARD, 400, MM, 80, PERCENT)
        drivetrain.set_drive_velocity(70, PERCENT)
        drivetrain.turn_for(RIGHT, 70, DEGREES)
        drivetrain.drive_for(FORWARD, 950, MM)
        drivetrain.turn_for(LEFT, 35, DEGREES)
        drivetrain.drive_for(FORWARD, 5000, MM)
        drivetrain.drive_for(FORWARD, 900, MM, 40, PERCENT)
        drivetrain.turn_for(RIGHT, 20, DEGREES)
        drivetrain.drive_for(REVERSE, 5000, MM, 20, PERCENT)
        drivetrain.drive_for(REVERSE, 5000, MM, 20, PERCENT)
        drivetrain.turn_for(LEFT, 165, DEGREES)
        wings.set(True)
        for i in range(3):
            drivetrain.drive_for(FORWARD, 1000, MM, 100, PERCENT)
            drivetrain.drive_for(REVERSE, 700,MM, 30, PERCENT)
            drivetrain.turn_for(LEFT, 15, DEGREES)
        
    else:
        controller_1.screen.print("team position not selected")

#  Driver Control def
# - controller map: left joystick: moving, L1 trigger: wings(hold)
# - R1 trigger: puncher, R2 trigger: change puncher status(switch), 
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped, sensor_status, wings_status, matchload
    drivetrain.set_stopping(BRAKE)
    if team_position == "red_defence" or team_position == "blue_defence":
        sensor_status = 1
        puncher.spin_for(REVERSE, 80, DEGREES, wait = True)
        puncher.set_stopping(HOLD)
    elif team_position == "red_offence" or team_position == "blue_offence":
        sensor_status = 0
    elif team_position == "skill":
        sensor_status = 1
        puncher.spin_for(REVERSE, 80, DEGREES, wait = True)
        puncher.set_stopping(HOLD)
    # Process every 20 milliseconds
    while True:
    # Drive Train
        forward = controller_1.axis3.position()
        rotate = (170/(1+2.72**(-0.018*controller_1.axis4.position())))-85
        
        left_drive_smart_speed = forward + rotate
        right_drive_smart_speed = forward - rotate

        if left_drive_smart_speed < 2 and left_drive_smart_speed > -2:
            if left_drive_smart_stopped:
                left_drive_smart.stop()
                left_drive_smart_stopped = 0
        else:
            left_drive_smart_stopped = 1
        if right_drive_smart_speed < 2 and right_drive_smart_speed > -2:
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
        if controller_1.buttonR1.pressing():
            puncher.spin_for(REVERSE, 180, DEGREES, wait = True)
            puncher.spin_to_position(0,DEGREES, wait = False)
        elif controller_1.buttonR2.pressing():
            sensor_status = not sensor_status
            if sensor_status:
                controller_1.rumble(".")
            else:
                controller_1.rumble("-")
            while controller_1.buttonR2.pressing():
                wait(50, MSEC)
        elif optical.is_near_object() and sensor_status:
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
                wait(50, MSEC)
        else:
            puncher.stop()
    # wings control
        if controller_1.buttonL1.pressing():
            wings.set(not wings_status)
        elif controller_1.buttonL2.pressing():
            wings_status = not wings_status
            while controller_1.buttonL2.pressing():
                wait(50, MSEC)
        else:
            wings.set(wings_status)
    
    # skill auto
        if team_position == "skill" and controller_1.buttonUp.pressing():
            drivetrain.drive_for(FORWARD, 1300, MM, 100, PERCENT, wait = True)
            drivetrain.drive_for(Reverse, 530, MM, 70, PERCENT, wait = True)
            drivetrain_turn(60, RIGHT)
            drivetrain.drive_for(REVERSE, 200, MM, 20, PERCENT, wait = True)
            for i in range(38):
                puncher.spin_for(REVERSE, 180, DEGREES, wait = True)
            goto(1450, 900, 80, True)
            goto(1450, -900, 80, True)
            goto(1000, -900, 80, True)
            goto(0, -300, 80, True)
            drivetrain.turn_to_heading(0, DEGREES)
            wings.set(True)
            drivetrain.turn_for(RIGHT, 10, DEGREES)
            drivetrain.turn_for(LEFT, 10, DEGREES)
            for i in range(3):
                drivetrain.drive_for(FORWARD, 1000, 100, PERCENT)
                drivetrain.drive_for(REVERSE, 700, 60, PERCENT)
    # Wait before repeating the controller input process
    wait(20, MSEC)

#choose team
team_position = team_choosing()
inertial.calibrate()
# Competition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)