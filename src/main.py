# Library imports
from vex import *
import urandom

# ------------------------
# Code by Eric & Peter (mostly Eric)
# Team 75477F 'Frij'
# Over Under 2023-2024
# ------------------------

# Wiring Guide
# - drivetrain: left a: #1;  left b: #6;  left c: #10;  right a: #11;  right b: #16  right c: #20;
# - claw motor: #2
# - inertial sensor: #3
# - gps sensor: #9

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

claw = Motor(Ports.PORT2, GearSetting.RATIO_36_1, True)

# Drivetrain
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 299.24, 320, 255, MM, 1.6666666666666667)

# Sensor
inertial = Inertial(Ports.PORT3)
gps = Gps(Ports.PORT9, -5.00, -2.80, INCHES, 270) #* x-offset, y-offset, angle offset

# Pneumatics
cylinder_a = DigitalOut(brain.three_wire_port.a)

# wait for rotation sensor to fully initialize
wait(30, MSEC)

# Pre-set variables
left_drive_smart_stopped = False
right_drive_smart_stopped = False

left_drive_smart_speed = 0
right_drive_smart_speed = 0

claw_speed = 0
claw_stopped = False
claw.set_stopping(HOLD)

team_position = " "

inertial.calibrate()
gps.calibrate()
wait(2,SECONDS)
inertial.set_heading(0, DEGREES)


# team and side choosing
# 1 for defence and 2 for offence
def team_choosing():
    brain.screen.set_font(FontType.MONO15)
    brain.screen.set_fill_color(Color.RED)
    brain.screen.draw_rectangle(0,0,240,120)
    brain.screen.set_cursor(3, 8)
    brain.screen.print("Red 1")
    brain.screen.set_fill_color(Color.RED)
    brain.screen.draw_rectangle(240,0,240,120)
    brain.screen.set_cursor(3, 32)
    brain.screen.print("Red 2")
    brain.screen.set_fill_color(Color.BLUE)
    brain.screen.draw_rectangle(0,120,240,120)
    brain.screen.set_cursor(10, 8)
    brain.screen.print("Blue 1")
    brain.screen.set_fill_color(Color.BLUE)
    brain.screen.draw_rectangle(240,120,240,120)
    brain.screen.set_cursor(10, 32)
    brain.screen.print("Blue 2")
    while not brain.screen.pressing():
        wait(5,MSEC)
    if brain.screen.x_position<240 and brain.screen.y_position<120:
        brain.screen.set_fill_color(Color.RED)
        team_position = "RED_1"
    elif brain.screen.x_position>240 and brain.screen.y_position<120:
        brain.screen.set_fill_color(Color.RED)
        team_position = "RED_2"
    elif brain.screen.x_position<240 and brain.screen.y_position>120:
        brain.screen.set_fill_color(Color.BLUE)
        team_position = "BLUE_1"
    elif brain.screen.x_position>240 and brain.screen.y_position>120:
        brain.screen.set_fill_color(Color.BLUE)
        team_position = "BLUE_2"
    brain.screen.draw_rectangle(0,0,240,120)
    brain.screen.set_cursor(6, 9)
    brain.screen.set_font(FontType.MONO60)
    brain.screen.print("75477F")
    brain.screen.next_row()
    brain.screen.print(team_position)
    
# turing def
#* Direction = RIGHT or LEFT
#! do not change!
def drivetrain_turn(target_angle, Direction):
    drivetrain.turn(Direction)
    current_angle = inertial.heading(DEGREES)
    while not target_angle+1 > current_angle > target_angle:
        if Direction == LEFT:
            turn_angle = current_angle - target_angle
        else:
            turn_angle = target_angle - current_angle
        if turn_angle < 0:
            turn_angle += 360
        current_angle = inertial.heading(DEGREES)
        drivetrain.set_turn_velocity(turn_angle*0.3, PERCENT)
    drivetrain.stop()

#gps sensor def
#! do not change!
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

# ------------------------ Autonomous Start -------------------------------
def autonomous():
    if team_position == "RED_1" or team_position == "BLUE_1":
        pass
    elif team_position == "RED_2" or team_position == "BLUE_2":
        pass
    else:
        pass


# -------------- Autonomous End & Driver Control Start ---------------------
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped, claw_stopped
    
    # Process every 20 milliseconds
    while True:
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

# claw control
        claw_speed = controller_1.axis2.position()

        if claw_speed < 3 and claw_speed > -3:
            if claw_stopped:
                claw.stop()
                claw_stopped = False
        else:
            claw_stopped = True
        
        if claw_stopped:
            claw.set_velocity(claw_speed, PERCENT)
            claw.spin(FORWARD)  
# todo puncher control 
        pass

# ---------------------- Driver Control End -------------------------------

    # Wait before repeating the controller input process
    wait(20, MSEC)

#choose team
team_choosing()

# Competition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)