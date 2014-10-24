import time
from gamepad import Gamepad
from serial import Serial

serial = Serial('/dev/ttyUSB0', 9600)
gamepad = Gamepad(serial)

print """
this is the way to repeat some code on
the following events

 * move-left
 * move-right
 * move-up
 * move-down
"""

def move(event):
    while gamepad.is_holding(event):
        print 'move',
        if event.is_move_left():
            print 'left'
        elif event.is_move_right():
            print 'right'
        elif event.is_move_up():
            print 'up'
        elif event.is_move_down():
            print 'down'
        time.sleep(1)

def center(event):
    print "center", event.state.get_axes()

gamepad.on('move', move)
gamepad.on('move-center', center)
gamepad.listen()
