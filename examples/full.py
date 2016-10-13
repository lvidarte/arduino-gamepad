"""
Author: Leo Vidarte <http://nerdlabs.com.ar>

This is free software,
you can redistribute it and/or modify it
under the terms of the GPL version 3
as published by the Free Software Foundation.

"""

from gamepad import Gamepad
from serial import Serial

serial = Serial('/dev/ttyUSB0', 9600)
gamepad = Gamepad(serial)

def move(event):
    print 'move', event.state.get_axes()

def move_x(event):
    print 'move-x', event.state.x

def move_y(event):
    print 'move-y', event.state.y

def move_left(event):
    print 'move-left', event.state.x

def move_right(event):
    print 'move-right', event.state.x

def move_up(event):
    print 'move-up', event.state.y

def move_down(event):
    print 'move-down', event.state.y

def move_center(event):
    print 'move-center', event.state.get_axes()

def switch(event):
    print 'switch', event.state.switch

def switch_press(event):
    print 'switch-press', event.state.switch

def switch_release(event):
    print 'switch-release', event.state.switch

def button(event):
    print 'button', event.state.button

def button_press(event):
    print 'button-press', event.state.button

def button_release(event):
    print 'button-release', event.state.button

gamepad.on('move', move)
gamepad.on('move-x', move_x)
gamepad.on('move-y', move_y)
gamepad.on('move-left', move_left)
gamepad.on('move-right', move_right)
gamepad.on('move-up', move_up)
gamepad.on('move-down', move_down)
gamepad.on('move-center', move_center)
gamepad.on('switch', switch)
gamepad.on('switch-press', switch_press)
gamepad.on('switch-release', switch_release)
gamepad.on('button', button)
gamepad.on('button-press', button_press)
gamepad.on('button-release', button_release)
gamepad.listen()
