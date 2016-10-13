"""
Author: Leo Vidarte <http://nerdlabs.com.ar>

This is free software,
you can redistribute it and/or modify it
under the terms of the GPL version 3
as published by the Free Software Foundation.

"""

import threading
import itertools
import copy


CMD_MASK   = 0b11000000
PARAM_MASK = 0b00111111

XY_VALUE_MASK = 0b1111

CMD_X  = 0b00000000
CMD_Y  = 0b01000000
CMD_SW = 0b10000000
CMD_BT = 0b11000000

CMD_NAMES = ('X', 'Y', 'SW', 'BT')

BUTTON_STATUS = ('released', 'pressed')

CENTER_VALUES = (31, 32)

NO_REPEATABLE_EVENTS = (
    'move-left',
    'move-right',
    'move-up',
    'move-down'
)

SENSIBILITY_HIGH   = 10
SENSIBILITY_MEDIUM = 5
SENSIBILITY_LOW    = 1


class Event:

    get_id = itertools.count().next

    def __init__(self, state, center_values = CENTER_VALUES):
        self.id = Event.get_id()
        self.state = state
        self.center_values = center_values
        self.names = self.get_names()

    def get_names(self):
        return self._get_names_move() + \
               self._get_names_switch() + \
               self._get_names_button()

    def is_x(self):
        return self.state.data.cmd == CMD_X

    def is_y(self):
        return self.state.data.cmd == CMD_Y

    def is_move(self):
        return self.is_x() or self.is_y()

    def is_move_center(self):
        return self.is_move() and \
               self.state.x in self.center_values and \
               self.state.y in self.center_values

    def is_move_left(self):
        return self.is_x() and \
               self.state.x < self.center_values[0]

    def is_move_right(self):
        return self.is_x() and \
               self.state.x > self.center_values[-1]

    def is_move_up(self):
        return self.is_y() and \
               self.state.y < self.center_values[0]

    def is_move_down(self):
        return self.is_y() and \
               self.state.y > self.center_values[-1]

    def is_switch(self):
        return self.state.data.cmd == CMD_SW

    def is_switch_press(self):
        return self.is_switch() and \
               self.state.switch == 1

    def is_switch_release(self):
        return self.is_switch() and \
               self.state.switch == 0

    def is_button(self):
        return self.state.data.cmd == CMD_BT

    def is_button_press(self):
        return self.is_button() and \
               self.state.button == 1

    def is_button_release(self):
        return self.is_button() and \
               self.state.button == 0

    def _get_names_move(self):
        if self.is_move():
            return ['move'] + \
                self._get_names_move_x() + \
                self._get_names_move_y()
        else:
            return []

    def _get_names_move_x(self):
        names = []
        if self.is_x():
            names.append('move-x')
            if self.is_move_right():
                names.append('move-right')
            elif self.is_move_left():
                names.append('move-left')
            elif self.is_move_center():
                names.append('move-center')
        return names

    def _get_names_move_y(self):
        names = []
        if self.is_y():
            names.append('move-y')
            if self.is_move_up():
                names.append('move-up')
            elif self.is_move_down():
                names.append('move-down')
            elif self.is_move_center():
                names.append('move-center')
        return names

    def _get_names_switch(self):
        names = []
        if self.is_switch():
            names.append('switch')
            if self.is_switch_press():
                names.append('switch-press')
            elif self.is_switch_release():
                names.append('switch-release')
        return names

    def _get_names_button(self):
        names = []
        if self.is_button():
            names.append('button')
            if self.is_button_press():
                names.append('button-press')
            elif self.is_button_release():
                names.append('button-release')
        return names

    def __str__(self):
        return "Event: %s" % self.state.__str__()

    def __repr__(self):
        return self.__str__()


class Data:

    def __init__(self, data):
        self.cmd = self._get_cmd(data)
        self.param = self._get_param(data)

    def _get_cmd(self, data):
        return data & CMD_MASK

    def _get_param(self, data):
        return data & PARAM_MASK

    def __str__(self):
        return "(%s, %s)" % (
            CMD_NAMES[self.cmd >> 6], self.param
        )

    def __repr__(self):
        return self.__str__()


class State: 

    def __init__(self, x=0, y=0, switch=0, button=0):
        self.x = x
        self.y = y
        self.switch = switch
        self.button = button
        self.data = None

    def get_axes(self):
        return (self.x, self.y)

    def update(self, data):
        self.data = data
        if data.cmd == CMD_X:
            self.x = data.param
        elif data.cmd == CMD_Y:
            self.y = data.param
        elif data.cmd == CMD_SW:
            self.switch = data.param
        elif data.cmd == CMD_BT:
            self.button = data.param

    def __str__(self):
        return "xy(%s, %s) switch:%s, button:%s" % (
            self.x, self.y,
            BUTTON_STATUS(self.switch),
            BUTTON_STATUS(self.button))

    def __repr__(self):
        return self.__str__()


class Gamepad(object):

    def __init__(self, serial, sensibility = SENSIBILITY_HIGH):
        self.serial = serial
        self.set_sensibility(sensibility)
        self.state = State()
        self.event = None
        self._callbacks = []
        self._hold = None

    def on(self, event_name, handler):
        self._callbacks.append({
            'event_name': event_name,
            'handler'   : handler
        })

    def set_sensibility(self, factor):
        if factor > 10:
            factor = 10
        if factor < 1:
            factor = 1
        factor = 30 - (factor * 3)
        self.center_values = range(
            CENTER_VALUES[0] - factor,
            CENTER_VALUES[-1] + factor + 1)

    def is_holding(self, event):
        return self._hold == event.id

    def _is_holdeable(self, event):
        for event_name in event.names:
            if event_name in NO_REPEATABLE_EVENTS:
                return self._hold is None
        return False

    def _start_thread(self, handler, event):
        t = threading.Thread(target=handler, args=(event,))
        t.daemon = True
        t.start()

    def listen(self):
        while True:
            data = self.read_data()
            self.state.update(data)
            self.event = self.create_event()
            self._dispatcher(self.event)

    def read_data(self):
        data = ord(self.serial.read())
        return Data(data)

    def create_event(self):
        state = copy.deepcopy(self.state)
        return Event(state, self.center_values)

    def _dispatcher(self, event):
        if event.is_move_center():
            self._hold = None
        for callback in self._callbacks:
            for event_name in event.names:
                if event_name == callback['event_name']:
                    if self._is_holdeable(event):
                        self._hold = event.id
                    self._start_thread(callback['handler'], event)

    def __str__(self):
        return "Gamepad: %s" % self.state.__str__()

    def __repr__(self):
        return self.__str__()

