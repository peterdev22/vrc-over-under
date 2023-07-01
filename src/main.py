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
# - gps sensor: #9
# - optial sensot: #7
# - elevation cylinders: #a; #b


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
right_motor_b = Motor(Ports.PORT19, GearSetting.RATIO_6_1, False)
right_motor_c = Motor(Ports.PORT21, GearSetting.RATIO_6_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

puncher_a = Motor(Ports.PORT4, GearSetting.RATIO_36_1, True)
puncher_b = Motor(Ports.PORT14, GearSetting.RATIO_36_1, False)
puncher = MotorGroup(puncher_a, puncher_b)

# Drivetrain
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 299.24, 320, 255, MM, 5/3)

#vision sensor sig
vision__G_TRIBALL = Signature(1, -3911, -319, -2115,-4709, -947, -2828,0.9, 0)

# Sensor
inertial = Inertial(Ports.PORT3)
gps = Gps(Ports.PORT9, -5.00, -2.80, INCHES, 270) #* x-offset, y-offset, angle offset
optical = Optical(Ports.PORT7)
vision = Vision(Ports.PORT13, 50, vision__G_TRIBALL)

# Pneumatics
elevation_a = DigitalOut(brain.three_wire_port.a)
elevation_b = DigitalOut(brain.three_wire_port.b)
claw_c = DigitalOut(brain.three_wire_port.c)
expansion_e = DigitalOut(brain.three_wire_port.e)

# wait for rotation sensor to fully initialize
wait(30, MSEC)

# Pre-set variables
left_drive_smart_stopped = False
right_drive_smart_stopped = False

left_drive_smart_speed = 0
right_drive_smart_speed = 0

puncher.set_stopping(HOLD)

puncher.set_velocity(70,PERCENT)
puncher.set_position(0,DEGREES)


team_position = " "

inertial.calibrate()
gps.calibrate()
inertial.set_heading(0, DEGREES)

elevation_a.set(True)
elevation_b.set(True)

expansion_e.set(False)
expansion_status = False

brain.screen.draw_image_from_file("begin.png", 0, 4)
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
def obj_looking(object): 
    controller_1.screen.set_cursor(1,1)
    if vision.take_snapshot(vision__G_TRIBALL) is not None:
        x_cord = vision.largest_object().centerX
        y_cord = vision.largest_object().centerY
        controller_1.screen.print("x: ", x_cord, "y: ", y_cord)
        if x_cord <= 120:
            drivetrain.turn(LEFT, 10, PERCENT)
        elif x_cord >= 185:
            drivetrain.turn(RIGHT, 10, PERCENT)
        else:
            drivetrain.stop()
    else:
        controller_1.screen.print("object not found")
        
        
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
        obj_looking("test")
    else:
        controller_1.screen.print("team position not selected")

#  Driver Control def
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped, claw_stopped
    # Process every 20 milliseconds
    while True:
        controller_1.screen.clear_screen()
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
            puncher.spin_for(REVERSE, 180, DEGREES, wait = True)
            puncher.spin_to_position(0,DEGREES, wait = False)
        elif optical.is_near_object():
            puncher.spin_for(REVERSE, 180, DEGREES, wait = True)
        else:
            puncher.stop()
    # elevation control
        if controller_1.buttonR2.pressing():
            elevation(False)
        else:
            elevation(True)
    #intake control
        if controller_1.buttonL1.pressing():
            claw_c.set(True)
        else:
            claw_c.set(False)
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