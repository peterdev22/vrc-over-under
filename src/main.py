# Library imports
from vex import *
import urandom

# ------------------------
# Code by Eric & Peter (mostly Eric)
# Team 75477M 'Frij'
# Over Under 2023-2024
# ------------------------

# Wiring Guide
# - drivetrain: left a: #1;  left b: #6;  left c: #10;  right a: #11;  right b: #16  right c: #20;
# - intake: #7, puncher: #4
# - inertial sensor: #3
# - gps sensor: #9
# - optial sensot: #8
# - elevation cylinders: #a; #b


# Brain
brain = Brain()

# Controllers
controller_1 = Controller(PRIMARY)

# Motors (A front, C back)
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_6_1, True)
left_motor_b = Motor(Ports.PORT6, GearSetting.RATIO_6_1, True)
left_motor_c = Motor(Ports.PORT10, GearSetting.RATIO_6_1, True)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b, left_motor_c)

right_motor_a = Motor(Ports.PORT11, GearSetting.RATIO_6_1, False)
right_motor_b = Motor(Ports.PORT16, GearSetting.RATIO_6_1, False)
right_motor_c = Motor(Ports.PORT20, GearSetting.RATIO_6_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

puncher = Motor(Ports.PORT4, GearSetting.RATIO_36_1, False)
intake = Motor(Ports.PORT7, GearSetting.RATIO_6_1, True)

# Drivetrain
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 299.24, 320, 255, MM, 5/3)

# Sensor
inertial = Inertial(Ports.PORT3)
gps = Gps(Ports.PORT9, -5.00, -2.80, INCHES, 270) #* x-offset, y-offset, angle offset
optical = Optical(Ports.PORT8)


# Pneumatics
elevation_a = DigitalOut(brain.three_wire_port.a)
elevation_b = DigitalOut(brain.three_wire_port.b)
expansion_c = DigitalOut(brain.three_wire_port.c)

# wait for rotation sensor to fully initialize
wait(30, MSEC)

# Pre-set variables
left_drive_smart_stopped = False
right_drive_smart_stopped = False

left_drive_smart_speed = 0
right_drive_smart_speed = 0

intake.set_stopping(HOLD)
puncher.set_stopping(HOLD)

puncher.set_velocity(70,PERCENT)
puncher.set_position(0,DEGREES)

team_position = " "

inertial.calibrate()
gps.calibrate()
inertial.set_heading(0, DEGREES)

elevation_a.set(True)
elevation_b.set(True)

expansion_c.set(False)
expansion_status = False

# team and side choosing
# - 1 for defence and 2 for offence
def team_choosing():
    choosing = True
    selected = False
    color = ""
    team_position = ""
    while choosing:
        if 139 <= brain.screen.x_position() <= 240 and 8 <= brain.screen.y_position() <= 26:
            brain.screen.draw_image_from_file("red_begin.png", 0, 0)
            color = "red"
            selected = False
        elif 249 <= brain.screen.x_position() <= 351 and 8 <= brain.screen.y_position() <= 26:
            brain.screen.draw_image_from_file("blue_begin.png", 0, 0)
            color = "blue"
            selected = False
        elif 358 <= brain.screen.x_position() <= 461 and 8 <= brain.screen.y_position() <= 26:
            brain.screen.draw_image_from_file("skill_begin.png", 0, 0)
            color = "skill"
            selected = True
            team_position = "skill"
        elif color == "red":
            if 19 <= brain.screen.x_position() <= 138 and 52 <= brain.screen.y_position() <= 74:
                brain.screen.draw_image_from_file("red_offence.png", 0, 0)
                selected = True
                team_position = "red_offence"
                while 19 <= brain.screen.x_position() <= 138 and 52 <= brain.screen.y_position() <= 74:
                    wait(20, MSEC)
            elif 19 <= brain.screen.x_position() <= 138 and 85 <= brain.screen.y_position() <= 107:
                brain.screen.draw_image_from_file("red_defence.png", 0, 0)
                selected = True
                team_position = "red_defence"
                while 19 <= brain.screen.x_position() <= 138 and 85 <= brain.screen.y_position() <= 107:
                    wait(20, MSEC)
        elif color == "blue":
            if 19 <= brain.screen.x_position() <= 138 and 52 <= brain.screen.y_position() <= 74:
                brain.screen.draw_image_from_file("blue_offence.png", 0, 0)
                selected = True
                team_position = "blue_offence"
                while 19 <= brain.screen.x_position() <= 138 and 52 <= brain.screen.y_position() <= 74:
                    wait(20, MSEC)
            elif 19 <= brain.screen.x_position() <= 138 and 85 <= brain.screen.y_position() <= 107:
                brain.screen.draw_image_from_file("blue_defence.png", 0, 0)
                selected = True
                team_position = "blue_defence"
                while 19 <= brain.screen.x_position() <= 138 and 85 <= brain.screen.y_position() <= 107:
                    wait(20, MSEC)
        elif 19 <= brain.screen.x_position() <= 138 and 120 <= brain.screen.y_position() <= 142 and selected:
            brain.screen.draw_image_from_file(team_position + "_confirmed.png",  0,  0)
            selected = False
            choosing = False
            return team_position


# turing def
# - Direction = RIGHT or LEFT
def drivetrain_turn(target_angle, Direction):
    drivetrain.turn(Direction)
    current_angle = inertial.heading(DEGREES)
    while not target_angle + 1 > current_angle > target_angle:
        if Direction == LEFT:
            turn_angle = current_angle - target_angle
        else:
            turn_angle = target_angle - current_angle
        if turn_angle < 0:
            turn_angle += 360
        current_angle = inertial.heading(DEGREES)
        drivetrain.set_turn_velocity(turn_angle*0.3, PERCENT)
    drivetrain.stop()

# gps sensor def
def goto(x_cord, y_cord):
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
            drivetrain.drive_for(FORWARD, a, MM)

# todo vision sensor def
def vision(object):
    pass
        
# elevation def
# - status = True(extend) or False(retract)
def elevation(status):
    elevation_a.set(status)
    elevation_b.set(status)

# Autonomous def
def autonomous():
    #defencive
    controller_1.screen.print(team_position)
    if team_position == "red_defence" or team_position == "blue_defence":
        pass      
    elif team_position == "red_offence" or team_position == "blue_offence":
        pass
    elif team_position == "skill":
        pass
    else:
        controller_1.screen.print("team position not selected")

#  Driver Control def
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped, claw_stopped
    # Process every 20 milliseconds
    while True:
    # Drive Train
        forward = controller_1.axis3.position()
        rotate = controller_1.axis4.position()*0.6

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
            left_drive_smart.set_velocity(left_drive_smart_speed, PERCENT)
            left_drive_smart.spin(FORWARD)
        if right_drive_smart_stopped:
            right_drive_smart.set_velocity(right_drive_smart_speed, PERCENT)
            right_drive_smart.spin(FORWARD)
    # puncher control 
        if controller_1.buttonR1.pressing():
        #    punch(1)
            puncher.spin_for(REVERSE, 1080, DEGREES, wait = True)
            puncher.spin_to_position(0,DEGREES, wait = False)
            ''' elif 110.00 <= optical.hue()<=130.00 or 20.00 <= optical.hue()<=60.00 or 280.00 <= optical.hue()<=360.00:
            wait(50, MSEC)
            puncher.spin_for(REVERSE, 1080, DEGREES, Wait = True)'''
        else:
            puncher.stop()
    # elevation control
        if controller_1.buttonR2.pressing():
            elevation(False)
        else:
            elevation(True)
    #intake control
        if controller_1.buttonL1.pressing():
            intake.spin(FORWARD)
        elif controller_1.buttonL2.pressing():
            intake.spin(REVERSE)
        else:
            intake.stop()
    #expansion control
    '''
        if controller_1.buttonX.pressing():
            expansion_status = not expansion_status
            while controller_1.buttonX.pressing():
                wait(10,MSEC)
        expansion_c.set(expansion_status)
    '''
    # Wait before repeating the controller input process
    wait(20, MSEC)

#choose team
team_position = team_choosing()

# Competition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)