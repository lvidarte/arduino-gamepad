#!/usr/bin/python -i

import serial
import sys


USB_DEV = '/dev/ttyUSB0'

CMD_MASK   = 0b11000000
PARAM_MASK = 0b00111111

CMD_X  = 0b00000000
CMD_Y  = 0b01000000
CMD_SW = 0b10000000
CMD_BT = 0b11000000

CMD_NAMES = ('X', 'Y', 'SW', 'BT')

STOP_VALUES = (31, 32)


try:
    conn = serial.Serial(USB_DEV, 9600)
except OSError:
    print "Can't connect to serial device"
    sys.exit(1)

class Event(object):

    def __init__(self, cmd, x, y, switch, button):
        self.cmd = cmd
        self.x = x
        self.y = y
        self.switch = switch
        self.button = button
        self.types = self.get_types()

    def get_types(self):
        types = []
        types += self._get_types_cmd_xy()
        types += self._get_types_cmd_sw()
        types += self._get_types_cmd_bt()
        return types

    def _get_types_cmd_xy(self):
        types = []
        if self.cmd in (CMD_X, CMD_Y):
            if self.x in STOP_VALUES and self.y in STOP_VALUES:
                types.append('stop')
            else:
                types.append('move')
                types += self._get_types_cmd_x()
                types += self._get_types_cmd_y()
        return types

    def _get_types_cmd_x(self):
        types = []
        if self.cmd == CMD_X:
            types.append('move-x')
            if self.x > STOP_VALUES[-1]:
                types.append('move-right')
            if self.x < STOP_VALUES[0]:
                types.append('move-left')
        return types

    def _get_types_cmd_y(self):
        types = []
        if self.cmd == CMD_Y:
            types.append('move-y')
            if self.y > STOP_VALUES[-1]:
                types.append('move-bottom')
            if self.y < STOP_VALUES[0]:
                types.append('move-top')
        return types

    def _get_types_cmd_sw(self):
        types = []
        if self.cmd == CMD_SW:
            types.append('switch')
            if self.switch:
                types.append('switch-press')
            else:
                types.append('switch-release')
        return types

    def _get_types_cmd_bt(self):
        types = []
        if self.cmd == CMD_BT:
            types.append('button')
            if self.button:
                types.append('button-press')
            else:
                types.append('button-release')
        return types

class Gamepad(object):

    def __init__(self, conn):
        self.conn = conn
        self.x = None
        self.y = None
        self.switch = None
        self.button = None
        self._callbacks = []

    def on(self, event, callback):
        self._callbacks.append({'event': event, 'f': callback})

    def get_cmd(self, data):
        return data & CMD_MASK

    def get_param(self, data):
        return data & PARAM_MASK

    def get_cmd_name(self, cmd):
        return CMD_NAMES[cmd >> 6]

    def set(self, data):
        self.cmd = self.get_cmd(data)
        self.param = self.get_param(data)
        if self.cmd == CMD_X:
            self.x = self.param
        if self.cmd == CMD_Y:
            self.y = self.param
        if self.cmd == CMD_SW:
            self.switch = self.param
        if self.cmd == CMD_BT:
            self.button = self.param

    def get_event(self):
        return Event(self.cmd,
                     self.x,
                     self.y,
                     self.switch,
                     self.button)

    def run_callbacks(self, event):
        for callback in self._callbacks:
            if callback['event'] in (event.name, 'all'):
                callback['f'](event)

    def listen(self):
        while True:
            data = ord(self.conn.read())
            self.set(data)
            event = self.get_event()
            print "events%s, xy(%s, %s)" % (event.types, self.x, self.y)
            #self.run_callbacks(event)


if __name__ == '__main__':

    gamepad = Gamepad(conn)

    class Game:

        def __init__(self, gamepad):
            self.gamepad = gamepad
            self.x = 0
            self.init()

        def button(self, event):
            self.x += 1
            print "%s, %s, %s" % (event.name, event.button, self.x)

        def move(self, event):
            print "%s (%s, %s)" % (event.name, event.x, event.y)

        def init(self):
            self.gamepad.on('press-button', self.button)
            self.gamepad.on('release-button', self.button)
            self.gamepad.on('release-switch', self.button)
            self.gamepad.on('change-x', self.move)
            self.gamepad.on('change-y', self.move)
            self.gamepad.listen()

    game = Game(gamepad)

