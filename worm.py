#!/usr/bin/python

import time
import serial
import sys


class Worm:

    INIT_LEN = 4
    FOOD_COLOR = (0, 0, 15)

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
        self.worm = []
        self.food = None
        self.score = 0
        self.matrix.reset()
        self.matrix.set_page_bg()
        self.set_rand_worm()
        self.draw_worm()
        self.draw_food()
        self.matrix.flip()
        print "Start!"

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

    def draw_food(self):
        if self.food is None:
            self.food = self.matrix.set_rand_xy()
            while self.food in self.worm:
                self.food = self.matrix.set_rand_xy()
        self.matrix.set_xy(*self.food)
        self.matrix.set_rgb(*self.FOOD_COLOR)
        self.matrix.fill()

    def set_rand_worm(self):
        pos = self.matrix.set_rand_xy()
        self.worm = [pos]
        for i in range(self.INIT_LEN - 1):
            x = (pos[0] - 1 - i) % matrix.COLS
            y = pos[1]
            self.worm.append((x , y))

    def move(self, event):
        while self.gamepad.event_is_hold(event):
            self.move_worm()
            self.draw_worm()
            self.draw_food()
            self.matrix.flip()
            time.sleep(.5)

    def move_worm(self):
        event = self.gamepad.last_event
        head = self.worm[0]
        if event.is_move_left():
            head = (head[0] - 1) % matrix.COLS, head[1]
        if event.is_move_right():
            head = (head[0] + 1) % matrix.COLS, head[1]
        if event.is_move_up():
            head = head[0], (head[1] + 1) % matrix.ROWS
        if event.is_move_down():
            head = head[0], (head[1] - 1) % matrix.ROWS
        self.check_state(head)

    def check_state(self, head):
        if head in self.worm[1:]:
            self.game_over()
            self.init()
        else:
            self.worm.insert(0, head)
            if head == self.food:
                self.food = None
                self.score += 1
                print 'Score:', self.score
            else:
                self.worm.pop()

    def game_over(self):
        if self.score == (matrix.COLS * matrix.ROWS) - self.INIT_LEN:
            print 'You Win!'
        else:
            print 'Game Over!'


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
    time.sleep(2)
    w = Worm(g, m)
