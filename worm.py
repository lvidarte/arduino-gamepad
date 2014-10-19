#!/usr/bin/python

import time
import serial
import sys


class Worm:

    def __init__(self, gamepad, matrix):
        self.gamepad = gamepad
        self.matrix = matrix
        self.start()

    def start(self):
        self.init()
        self.gamepad.on('button-press', self.restart)
        self.gamepad.on('move', self.move)
        self.gamepad.listen()

    def init(self):
        self.matrix.reset()
        self.set_rand_worm()
        self.draw_worm()

    def restart(self, _):
        self.init()

    def draw_worm(self):
        self.matrix.clear_all()
        for i, pos in enumerate(self.worm):
            x, y = pos
            if i == 0:
                r, g, b = 15, 0, 0
            else:
                r, g, b = 0, 15, 0
            self.matrix.set(x=x, y=y, r=r, g=g, b=b)

    def set_rand_worm(self):
        self.matrix.set_rand_x()
        self.matrix.set_rand_y()
        self.worm = [(self.matrix.x, self.matrix.y)]
        for i in range(3):
            x, y = self.worm[i]
            self.worm.append((x - 1, y))

    def move(self, event):
        while self.gamepad.event_is_hold(event):
            self.move_worm()
            self.draw_worm()
            time.sleep(.5)

    def move_worm(self):
        event = self.gamepad.last_event
        head = self.worm[0]
        if event.is_move_left():
            head = head[0] - 1, head[1]
        if event.is_move_right():
            head = head[0] + 1, head[1]
        if event.is_move_up():
            head = head[0], head[1] + 1
        if event.is_move_down():
            head = head[0], head[1] - 1
        self.worm.insert(0, head)
        self.worm.pop()


if __name__ == '__main__':

    import gamepad

    try:
        import matrix
    except ImportError:
        print "Matrix module not found"
        print "Download it and copy here the matrix dir"
        print "https://github.com/lvidarte/arduino-matrix-rgb"

    try:
        serial1 = serial.Serial('/dev/ttyUSB0', 9600)
    except OSError:
        print "Can't connect to serial1 device"
        sys.exit(1)

    try:
        serial2 = serial.Serial('/dev/ttyACM0', 9600)
    except OSError:
        print "Can't connect to serial2 device"
        sys.exit(1)

    g = gamepad.Gamepad(serial1)
    m = matrix.Matrix(serial2)
    w = Worm(g, m)
