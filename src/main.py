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

right_motor_a = Motor(Ports.PORT18, GearSetting.RATIO_6_1, False)
right_motor_b = Motor(Ports.PORT21, GearSetting.RATIO_6_1, False)
right_motor_c = Motor(Ports.PORT19, GearSetting.RATIO_6_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

puncher_a = Motor(Ports.PORT4, GearSetting.RATIO_36_1, True)
puncher_b = Motor(Ports.PORT14, GearSetting.RATIO_36_1, False)
puncher = MotorGroup(puncher_a, puncher_b)


# Sensor
inertial = Inertial(Ports.PORT3)
gps = Gps(Ports.PORT8, -120.00, -125.00, MM, -95) #- x-offset, y-offset, angle offset
optical = Optical(Ports.PORT7)

# Drivetrain
drivetrain = SmartDrive(left_drive_smart, right_drive_smart,gps, 299.24, 260, 230, MM, 0.6)

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

wings.set(False)
blocker.set(True)

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

# turing def
# - Direction = RIGHT or LEFT
def drivetrain_turn(target_angle, Direction):
    inertial.set_heading(0.0, DEGREES)
    drivetrain.turn(Direction)
    current_angle = inertial.heading(DEGREES)
    total_angle = 0
    if Direction == LEFT:
            target_angle = 360 - target_angle
    while not (target_angle + 0.5 > current_angle > target_angle - 0.5):
        if Direction == LEFT:
            turn_angle = current_angle - target_angle
        else:
            turn_angle = target_angle - current_angle
        if turn_angle < 0:
            turn_angle += 360
        total_angle += turn_angle
        current_angle = inertial.heading(DEGREES)
        drivetrain.set_turn_velocity(turn_angle*0.7 + total_angle*0.005, RPM)
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
    # - 
    if team_position == "red_defence" or team_position == "blue_defence":
        drivetrain.set_timeout(1, SECONDS)
        drivetrain.drive_for(REVERSE, 400, MM, 20, PERCENT, wait = True)
        right_drive_smart.spin_for(REVERSE, 5.8, TURNS)
        drivetrain.drive_for(REVERSE, 500, MM, 50, PERCENT, wait = True)
        drivetrain.drive_for(FORWARD, 650, MM, 20, PERCENT, wait = True)
        right_drive_smart.spin_for(FORWARD, 6, TURNS)
        wings.set(True)
        drivetrain.drive_for(FORWARD, 320, MM, 20, PERCENT, wait = True)
        right_drive_smart.spin_for(FORWARD, 5.7, TURNS)
        right_drive_smart.spin_for(FORWARD, 3, TURNS)
        wings.set(False)
        right_drive_smart.spin_for(REVERSE, 1, TURNS)
        drivetrain.drive_for(FORWARD, 1000, MM, 50, PERCENT, wait = True)
        
        
    elif team_position == "red_offence" or team_position == "blue_offence":
        drivetrain.set_timeout(1, SECONDS)
        wings.set(True)
        drivetrain.drive_for(FORWARD, 450, MM, 20, PERCENT, wait = True)
        right_drive_smart.spin_for(FORWARD, 7, TURNS)
        right_drive_smart.spin_for(FORWARD, 3, TURNS)
        wings.set(False)
        right_drive_smart.spin_for(REVERSE, 1.5, TURNS)
        drivetrain.drive_for(FORWARD, 1000, MM, 50, PERCENT, wait = True)
        drivetrain.drive_for(REVERSE, 230, MM, 30, PERCENT, wait = True)
        left_drive_smart.turn_for(REVERSE, 10, TURNS)
        
    elif team_position == "skill":
        time = 0
        drivetrain.set_timeout(1, SECONDS)
        drivetrain.drive_for(FORWARD, 340, MM, 10, PERCENT, wait = True)
        left_drive_smart.spin_for(FORWARD, 5.5, TURNS)
        drivetrain.turn_for(RIGHT, 20, DEGREES)
        drivetrain.drive_for(FORWARD, 450, MM, 70, PERCENT, wait = True)
        drivetrain.drive_for(REVERSE, 530, MM, 25, PERCENT, wait = True)
        drivetrain.turn_to_heading(65, DEGREES, 10, PERCENT, wait = True)
        puncher.spin_for(REVERSE, 80, DEGREES, wait = False)
        puncher.set_stopping(HOLD)
        drivetrain.drive_for(REVERSE, 100, MM, 10, PERCENT, wait = True)
        time = brain.timer.time(SECONDS)
        while brain.timer.time(SECONDS) < time +25:
            if optical.is_near_object():
                puncher.spin_for(REVERSE, 180, DEGREES, wait = True)
        puncher.spin_for(REVERSE, 180, DEGREES, wait = False)
        puncher.set_stopping(COAST)
        drivetrain.drive_for(FORWARD, 200, MM, 20, PERCENT, wait = True)
        drivetrain.turn_to_heading(120, DEGREES, 10, PERCENT, wait = True)
        drivetrain.drive_for(FORWARD, 400, MM, 20, PERCENT, wait = True)
        drivetrain.turn_to_heading(90, DEGREES, 10, PERCENT, wait = True)
        #! have not finished
        
    else:
        controller_1.screen.print("team position not selected")

#  Driver Control def
# - controller map: left joystick: moving, L1 trigger: wings(hold)
# - R1 trigger: puncher, R2 trigger: change puncher status(switch)
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped, sensor_status, wings_status, matchload
    drivetrain.set_stopping(BRAKE)
    if team_position == "red_defence" or team_position == "blue_defence":
        sensor_status = 1
        puncher.spin_for(REVERSE, 80, DEGREES, wait = False)
        puncher.set_stopping(HOLD)
    elif team_position == "red_offence" or team_position == "blue_offence":
        sensor_status = 0
    elif team_position == "skill":
        sensor_status = 1
        wings.set(True)
        wait(500, MSEC)
        wings.set(False)
        left_drive_smart.turn_for(FORWARD, 5.5, TURNS)
        drivetrain.drive_for(FORWARD, 340, MM, 40, PERCENT, wait = True)
        left_drive_smart.turn_for(FORWARD, 5.5, TURNS)
        drivetrain.drive_for(FORWARD, 450, MM, 70, PERCENT, wait = True)
        drivetrain.drive_for(REVERSE, 530, MM, 25, PERCENT, wait = True)
        drivetrain.turn_to_heading(65, DEGREES, 10, PERCENT, wait = True)
        puncher.spin_for(REVERSE, 80, DEGREES, wait = False)
        puncher.set_stopping(HOLD)
        drivetrain.drive_for(REVERSE, 100, MM, 10, PERCENT, wait = True)
        time = brain.timer.time(SECONDS)
        while brain.timer.time(SECONDS) < time +25:
            if optical.is_near_object():
                puncher.spin_for(REVERSE, 180, DEGREES, wait = True)
        puncher.spin_for(REVERSE, 180, DEGREES, wait = False)
        puncher.set_stopping(COAST)
        drivetrain.drive_for(FORWARD, 300, MM, 50, PERCENT, wait = True)
    # Process every 20 milliseconds
    while True:
    # Drive Train
        rotate = 60*math.sin(0.007*controller_1.axis4.position())
        if controller_1.axis3.position() < -75:
            forward = -75
        else:
            forward = controller_1.axis3.position()
        left_drive_smart_speed = forward + rotate
        right_drive_smart_speed = forward - rotate

        if left_drive_smart_speed < 10 and left_drive_smart_speed > -10:
            if left_drive_smart_stopped:
                left_drive_smart.stop()
                left_drive_smart_stopped = 0
        else:
            left_drive_smart_stopped = 1
        if right_drive_smart_speed < 10 and right_drive_smart_speed > -10:
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
                wait(50, MSEC)
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
                wait(50, MSEC)
        else:
            puncher.stop()
    # wings control
        if controller_1.buttonR1.pressing():
            wings.set(not wings_status)
        elif controller_1.buttonR2.pressing():
            wings_status = not wings_status
            while controller_1.buttonR2.pressing():
                wait(50, MSEC)
        else:
            wings.set(wings_status)
            
        if controller_1.buttonY.pressing():
            blocker.set(False)
    
    # Wait before repeating the controller input process
    wait(20, MSEC)

#choose team
team_position = team_choosing()
# Competition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)