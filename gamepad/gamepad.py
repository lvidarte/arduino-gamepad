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

STOP_VALUES = (31, 32)

NO_REPEATABLE_EVENTS = (
    'move-left',
    'move-right',
    'move-up',
    'move-down'
)


class Event:

    get_id = itertools.count().next

    def __init__(self, state, stop_values):
        self.id = Event.get_id()
        self.state = state
        self.stop_values = stop_values
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
        return self.state.x in self.stop_values and \
               self.state.y in self.stop_values

    def is_move_left(self):
        return self.state.x < self.stop_values[0]

    def is_move_right(self):
        return self.state.x > self.stop_values[-1]

    def is_move_up(self):
        return self.state.y < self.stop_values[0]

    def is_move_down(self):
        return self.state.y > self.stop_values[-1]

    def is_switch(self):
        return self.state.data.cmd == CMD_SW

    def is_switch_press(self):
        return self.is_switch() and self.state.switch == 1

    def is_switch_release(self):
        return self.is_switch() and self.state.switch == 0

    def is_button(self):
        return self.state.data.cmd == CMD_BT

    def is_button_press(self):
        return self.is_button() and self.state.button == 1

    def is_button_release(self):
        return self.is_button() and self.state.button == 0

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

    def __init__(self, serial):
        self.serial = serial
        self.state = State()
        self.event = None
        self.callbacks = []
        self.hold_event(None)
        self.set_sensibility(10)

    def on(self, event_name, handler):
        self.callbacks.append({
            'event_name': event_name,
            'handler'   : handler
        })

    def set_sensibility(self, value = 10):
        if value > 10:
            value = 10
        if value < 1:
            value = 1
        factor = 30 - (value * 3)
        self.stop_values = (
            STOP_VALUES[0] - factor,
            STOP_VALUES[-1] + factor + 1
        )

    def hold_event(self, event):
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
        t.daemon = True
        t.start()

    def listen(self):
        while True:
            data = self.read_data()
            self.state.update(data)
            self.event = self.create_event()
            self.dispatcher(self.event)

    def read_data(self):
        data = ord(self.serial.read())
        return Data(data)

    def create_event(self):
        state = copy.copy(self.state)
        return Event(state, self.stop_values)

    def dispatcher(self, event):
        if event.is_move_center():
            self.hold_event(None)
        for callback in self.callbacks:
            for event_name in event.names:
                if event_name == callback['event_name']:
                    if self.event_is_holdeable(event):
                        self.hold_event(event)
                    self.start_thread(callback['handler'], event)

    def log(self):
        print self.__str__()

    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)

