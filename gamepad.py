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

    def __init__(self, cmd, param):
        self.cmd = cmd
        self.param = param
        self.name = self.get_name()

    def get_name(self):
        if self.cmd == CMD_X:
            return 'change-x'
        elif self.cmd == CMD_Y:
            return 'change-y'
        elif self.cmd == CMD_SW and self.param == 0:
            return 'release-switch'
        elif self.cmd == CMD_SW and self.param == 1:
            return 'press-switch'
        elif self.cmd == CMD_BT and self.param == 0:
            return 'release-button'
        elif self.cmd == CMD_BT and self.param == 1:
            return 'press-button'

class Gamepad(object):

    def __init__(self, conn):
        self.conn = conn
        self._callbacks = []

    def on(self, event, callback):
        self._callbacks.append({'event': event, 'f': callback})

    def _run_callbacks(self, event):
        for callback in self._callbacks:
            if callback['event'] in (event.name, 'all'):
                callback['f'](self, event)

    def get_cmd(self, data):
        return data & CMD_MASK

    def get_param(self, data):
        return data & PARAM_MASK

    def is_x(self, cmd):
        return cmd == CMD_X

    def is_y(self, cmd):
        return cmd == CMD_Y

    def is_switch(self, cmd):
        return cmd == CMD_SW

    def is_button(self, cmd):
        return cmd == CMD_BT

    def get_cmd_name(self, cmd):
        return CMD_NAMES[cmd >> 6]

    def listen(self):
        while True:
            data = ord(self.conn.read())
            cmd = self.get_cmd(data)
            param = self.get_param(data)
            event = Event(cmd, param)
            self._run_callbacks(event)
            print "cmd: %s, param: %s" % (self.get_cmd_name(cmd), param)


if __name__ == '__main__':

    gamepad = Gamepad(conn)

    def press(self, event):
        print "%s: %s, %s" % (
            event.name, 
            self.get_cmd_name(event.cmd),
            event.param)

    def release(self, event):
        print "%s: %s, %s" % (
            event.name,
            self.get_cmd_name(event.cmd),
            event.param)

    def change(self, event):
        print "%s: %s" % (event.name, event.param)

    def all(self, event):
        print '-----------------------'

    gamepad.on('press-button', press)
    gamepad.on('release-button', release)
    gamepad.on('press-switch', press)
    gamepad.on('release-switch', release)
    gamepad.on('change-x', change)
    gamepad.on('change-y', change)
    gamepad.on('all', all)

    gamepad.listen()
