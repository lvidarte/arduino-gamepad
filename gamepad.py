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
        self.name = self.get_name()

    def get_name(self):
        if self.cmd == CMD_X:
            return 'change-x'
        elif self.cmd == CMD_Y:
            return 'change-y'
        elif self.cmd == CMD_SW and self.switch == 0:
            return 'release-switch'
        elif self.cmd == CMD_SW and self.switch == 1:
            return 'press-switch'
        elif self.cmd == CMD_BT and self.button == 0:
            return 'release-button'
        elif self.cmd == CMD_BT and self.button == 1:
            return 'press-button'

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
            self.run_callbacks(event)


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

