#!/usr/bin/python

import threading
import time
import serial
import sys

BODY_LEN   = 4
BODY_COLOR = (0, 15, 0)
HEAD_COLOR = (15, 0, 0)
FOOD_COLOR = (15, 15, 0)
WALL_COLOR = (0, 0, 15)


class Snake:

    def __init__(self, gamepad, matrix):
        self.gamepad = gamepad
        self.matrix = matrix
        self.init()
        self.start()

    def init(self):
        self.snake = []
        self.wall = []
        self.food = None
        self.score = 0
        self.speed = .5
        self.direction = (1, 0)
        self.paused = False
        self.matrix.reset()
        self.matrix.set_page_bg()
        self.init_snake()
        self.draw_board()
        self.matrix.flip()

    def start(self):
        print "Start!"
        self.start_snake()
        self.start_gamepad()

    def start_gamepad(self):
        self.gamepad.on('move', self.move)
        self.gamepad.on('switch-press', self.pause)
        self.gamepad.on('button-press', self.restart)
        self.gamepad.listen()

    def start_snake(self):
        self.t = threading.Thread(target=self.live)
        self.t.daemon = True
        self.t.start()

    def live(self):
        while True:
            if not self.paused:
                self.move_snake()
                self.draw_board()
                self.matrix.flip()
                time.sleep(self.speed)

    def move(self, event):
        if event.is_move_left():
            self.direction = (-1, 0)
        if event.is_move_right():
            self.direction = (1, 0)
        if event.is_move_up():
            self.direction = (0, 1)
        if event.is_move_down():
            self.direction = (0, -1)

    def restart(self, _):
        self.init()

    def pause(self, event):
        if self.paused:
            self.paused = False
        else:
            self.paused = True

    def init_snake(self):
        self.snake = [
            (5, 4),
            (4, 4),
            (3, 4),
            (2, 4),
        ]

    def draw_snake(self):
        self.matrix.clear_all()
        for i, pos in enumerate(self.snake):
            x, y = pos
            if i == 0:
                r, g, b = HEAD_COLOR
            else:
                r, g, b = self.get_body_color(i)
            self.matrix.set(x=x, y=y, r=r, g=g, b=b)

    def get_body_color(self, i):
        return (
            self.get_gradient(BODY_COLOR[0], i),
            self.get_gradient(BODY_COLOR[1], i),
            self.get_gradient(BODY_COLOR[2], i),
        )

    def get_gradient(self, color, i):
        relation = color / (len(self.snake) - 1)
        gradient = color - (relation * i)
        if gradient < relation:
            gradient = relation
        return gradient

    def draw_food(self):
        if self.food == None:
            self.food = self.matrix.set_rand_xy()
            while self.food in self.snake + self.wall:
                self.food = self.matrix.set_rand_xy()
        self.matrix.set_xy(*self.food)
        self.matrix.set_rgb(*FOOD_COLOR)
        self.matrix.fill()

    def draw_wall(self, color=WALL_COLOR):
        self.wall = [
            (0, 2), (0, 1), (0, 0), (1, 0), (2, 0),
            (0, 5), (0, 6), (0, 7), (1, 7), (2, 7),
            (5, 7), (6, 7), (7, 7), (7, 6), (7, 5),
            (5, 0), (6, 0), (7, 0), (7, 1), (7, 2),
        ]
        self.matrix.set_rgb(*color)
        for pos in self.wall:
            self.matrix.set_xy(*pos)
            self.matrix.fill()

    def draw_board(self):
        self.draw_snake()
        self.draw_wall()
        self.draw_food()

    def move_snake(self):
        head = self.snake[0]
        x, y = self.direction
        if x != 0:
            head = (head[0] + x) % matrix.COLS, head[1]
        if y != 0:
            head = head[0], (head[1] + y) % matrix.ROWS
        self.check_state(head)

    def check_state(self, head):
        if head in self.snake[1:] + self.wall:
            self.end()
            self.init()
        else:
            self.snake.insert(0, head)
            if head == self.food:
                self.food = None
                self.score += 100
                self.speed -= .02
                print 'Score:', self.score
            else:
                self.snake.pop()

    def end(self):
        if self.score == (matrix.COLS * matrix.ROWS) - \
                         BODY_LEN - len(self.wall):
            print 'You Win!'
        else:
            print 'Game Over!'
            color = (15, 0, 0)
            self.matrix.clear_all()
            self.matrix.set_rgb(*color)
            self.draw_wall(color)
        self.matrix.flip()
        time.sleep(2)


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

    g = gamepad.Gamepad(serial1, sensibility = 2)
    m = matrix.Matrix(serial2)
    time.sleep(2)
    s = Snake(g, m)
