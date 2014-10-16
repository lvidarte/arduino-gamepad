import threading
import copy
import itertools


CMD_MASK   = 0b11000000
PARAM_MASK = 0b00111111

XY_VALUE_MASK = 0b1111

CMD_X  = 0b00000000
CMD_Y  = 0b01000000
CMD_SW = 0b10000000
CMD_BT = 0b11000000

CMD_NAMES = ('X', 'Y', 'SW', 'BT')

STOP_VALUES = (31, 32)

NO_REPEATABLE_EVENTS = (
    'move-left',
    'move-right',
    'move-up',
    'move-down'
)


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
        self.event_hold(None)

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

    def event_hold(self, event):
        if event is None:
            self.hold = None
        else:
            self.hold = event.id

    def event_is_hold(self, event):
        return self.hold == event.id

    def event_is_holdeable(self, event):
        for event_name in event.names:
            if event_name in NO_REPEATABLE_EVENTS:
                return self.hold is None
        return False

    def start_thread(self, handler, event):
        t = threading.Thread(target=handler, args=(event,))
        t.start()

    def dispatcher(self, event):
        if event.is_center():
            self.event_hold(None)
        for callback in self.callbacks:
            for event_name in event.names:
                if event_name == callback['event_name']:
                    if self.event_is_holdeable(event):
                        self.event_hold(event)
                    self.start_thread(callback['handler'], event)

    def serial_read(self):
        return ord(self.conn.read())

    def listen(self):
        while True:
            data = self.serial_read()
            self.set_state(data)
            self.last_event = self.get_event()
            self.dispatcher(self.last_event)

    def log(self):
        print self.__str__()

    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)

