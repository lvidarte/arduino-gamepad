#!/usr/bin/python -i

import time
import serial
import sys


class Worm:

    def __init__(self, gamepad, matrix):
        self.gamepad = gamepad
        self.matrix = matrix
        self.matrix.reset()
        self.set_rand_snake()
        self.draw_snake()
        self.init()

    def draw_snake(self):
        self.matrix.clear_all()
        for i, pos in enumerate(self.snake):
            x, y = pos
            if i == 0:
                r, g, b = 15, 0, 0
            else:
                r, g, b = 0, 15, 0
            self.matrix.set(x=x, y=y, r=r, g=g, b=b)

    def set_rand_snake(self):
        self.matrix.set_rand_x()
        self.matrix.set_rand_y()
        self.snake = [(self.matrix.x, self.matrix.y)]
        for i in range(3):
            x, y = self.snake[i]
            self.snake.append((x - 1, y))

    def button(self, event):
        print "clear"
        self.matrix.clear_all()
        self.matrix.set_rand_rgb()
        self.matrix.set_rand_x()
        self.matrix.set_rand_y()
        self.matrix.fill()

    def switch(self, event):
        print "random color"
        self.matrix.set_rand_rgb()
        self.matrix.fill()

    def move(self, event):
        print "MOVE"
        while self.gamepad.event_is_hold(event):
            self.move_snake()
            self.draw_snake()
            time.sleep(.5)

    def move_right(self, event):
        print "move right"

    def move_snake(self):
        event = self.gamepad.last_event
        head = self.snake[0]
        if event.is_left():
            head = head[0] - 1, head[1]
        if event.is_right():
            head = head[0] + 1, head[1]
        if event.is_up():
            head = head[0], head[1] + 1
        if event.is_down():
            head = head[0], head[1] - 1
        self.snake.insert(0, head)
        self.snake.pop()

    def init(self):
        self.gamepad.on('button-press', self.button)
        self.gamepad.on('switch-press', self.switch)
        self.gamepad.on('move', self.move)
        self.gamepad.on('move-right', self.move_right)
        self.gamepad.listen()

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
