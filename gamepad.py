#!/usr/bin/python -i

import time
import serial
import sys
import threading
import matrix
import copy
import itertools


USB_DEV = '/dev/ttyUSB0'

CMD_MASK   = 0b11000000
PARAM_MASK = 0b00111111

XY_VALUE_MASK = 0b1111

CMD_X  = 0b00000000
CMD_Y  = 0b01000000
CMD_SW = 0b10000000
CMD_BT = 0b11000000

CMD_NAMES = ('X', 'Y', 'SW', 'BT')

STOP_VALUES = (31, 32)

NO_REPEATABLE_EVENTS = ('move', 'move-left', 'move-right', 'move-up', 'move-down')

try:
    conn = serial.Serial(USB_DEV, 9600)
except OSError:
    print "Can't connect to serial device"
    sys.exit(1)


class Event(object):

    get_id = itertools.count().next

    def __init__(self, cmd, state):
        self.id = Event.get_id()
        self.cmd = cmd
        self.state = state
        self.names = self.get_names()

    def get_names(self):
        names = []
        names += self._get_names_move()
        names += self._get_names_switch()
        names += self._get_names_button()
        return names

    def is_x(self):
        return self.cmd == CMD_X

    def is_y(self):
        return self.cmd == CMD_Y

    def is_move(self):
        return self.is_x() or self.is_y()

    def is_switch(self):
        return self.cmd == CMD_SW

    def is_button(self):
        return self.cmd == CMD_BT

    def is_center(self):
        return self.state.x in STOP_VALUES and self.state.y in STOP_VALUES

    def is_left(self):
        return self.state.x < STOP_VALUES[0]

    def is_right(self):
        return self.state.x > STOP_VALUES[-1]

    def is_up(self):
        return self.state.y < STOP_VALUES[0]

    def is_down(self):
        return self.state.y > STOP_VALUES[-1]

    def _get_names_move(self):
        names = []
        if self.is_move():
            names.append('move')
            names += self._get_names_move_x()
            names += self._get_names_move_y()
        return names

    def _get_names_move_x(self):
        names = []
        if self.is_x():
            names.append('move-x')
            names += self._get_names_move_x_position()
        return names

    def _get_names_move_x_position(self):
        names = []
        if self.is_x():
            if self.is_right():
                names.append('move-right')
            elif self.is_left():
                names.append('move-left')
            elif self.is_center():
                names.append('move-center')
        return names

    def _get_names_move_y(self):
        names = []
        if self.cmd == CMD_Y:
            names.append('move-y')
            names += self._get_names_move_y_position()
        return names

    def _get_names_move_y_position(self):
        names = []
        if self.is_y():
            if self.is_up():
                names.append('move-up')
            elif self.is_down():
                names.append('move-down')
            elif self.is_center():
                names.append('move-center')
        return names

    def _get_names_switch(self):
        names = []
        if self.is_switch():
            names.append('switch')
            if self.state.switch:
                names.append('switch-press')
            else:
                names.append('switch-release')
        return names

    def _get_names_button(self):
        names = []
        if self.is_button():
            names.append('button')
            if self.state.button:
                names.append('button-press')
            else:
                names.append('button-release')
        return names


class State(object):

    SWITCH_STATES = ('pressed', 'released')
    BUTTON_STATES = ('pressed', 'released')

    def __init__(self, x=0, y=0, switch=0, button=0):
        self.x = x
        self.y = y
        self.switch = switch
        self.button = button

    def get_axes(self):
        return (self.x, self.y)

    def __str__(self):
        return "(%s, %s) switch:%s button:%s" % (
            self.x, self.y, self.switch, self.button
        )

    def __repr__(self):
        return self.__str__()

class Gamepad(object):

    def __init__(self, conn):
        self.conn = conn
        self.state = State()
        self.callbacks = []
        self.reset_hold_events()

    def on(self, event_name, handler):
        self.callbacks.append({
            'event_name': event_name,
            'handler'   : handler
        })

    def get_cmd(self, data):
        return data & CMD_MASK

    def get_param(self, data):
        return data & PARAM_MASK

    def get_cmd_name(self, cmd):
        return CMD_NAMES[cmd >> 6]

    def set_state(self, data):
        self.cmd = self.get_cmd(data)
        self.param = self.get_param(data)
        if self.cmd == CMD_X:
            self.state.x = self.param
        if self.cmd == CMD_Y:
            self.state.y = self.param
        if self.cmd == CMD_SW:
            self.state.switch = self.param
        if self.cmd == CMD_BT:
            self.state.button = self.param
        print self.state

    def get_event(self):
        return Event(self.cmd, copy.copy(self.state))

    def is_hold(self, name, id):
        return self.hold_events[name] == id

    def hold_event(self, name, id):
        self.hold_events[name] = id

    def reset_hold_events(self):
        self.hold_events = {}
        for name in NO_REPEATABLE_EVENTS:
            self.hold_event(name, None)

    def start_thread(self, handler, event):
        t = threading.Thread(target=handler, args=(event,))
        t.start()

    def is_holdeable(self, event_name, event):
        return event_name in NO_REPEATABLE_EVENTS and \
               'move-center' not in event.names and \
               self.hold_events[event_name] is None

    def dispatch(self, event):
        if event.is_center():
            self.reset_hold_events()
        for callback in self.callbacks:
            for event_name in event.names:
                if event_name == callback['event_name']:
                    if self.is_holdeable(event_name, event):
                        self.hold_event(event_name, event.id)
                    self.start_thread(callback['handler'], event)

    def serial_read(self):
        return ord(self.conn.read())

    def listen(self):
        while True:
            data = self.serial_read()
            self.set_state(data)
            self.last_event = self.get_event()
            self.dispatch(self.last_event)

    def log(self):
        print self.__str__()

    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)


if __name__ == '__main__':

    gamepad = Gamepad(conn)

    class Game:

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
            while self.gamepad.is_hold('move', event.id):
                self.move_snake()
                self.draw_snake()
                time.sleep(.5)

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
            self.gamepad.listen()

    m = matrix.Matrix(matrix.conn)
    game = Game(gamepad, m)

