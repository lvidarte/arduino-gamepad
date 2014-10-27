# Arduino Gamepad

<img src="https://github.com/lvidarte/arduino-gamepad/blob/master/gamepad.png" width="500px" />

### Load Arduino Sketch

Then build and upload the Arduino sketch. I use [inotool](http://inotool.org) for that

    ino build && ino upload


### Use example

```python
from serial import Serial
from gamepad import Gamepad

serial = Serial('/dev/ttyUSB0')
gamepad = Gamepad(serial)
```

Create the callback function

```python
def move(self, event):
    print 'move', event.state.get_axes()
```

Attach the callback to an event

```python
gamepad.on('move', move)
gamepad.listen()
```

<img src="https://github.com/lvidarte/arduino-gamepad/blob/master/gamepad.jpg" width="600px" />

### Events

    move
    move-x
    move-y
    move-right
    move-left
    move-up
    move-down
    move-center
    button
    button-press
    button-release
    switch
    switch-press
    switch-release

### Special events

The `move-right`, `move-left`, `move-up` and `move-down` events are holding when were fired and unholding when the `move-center` event is fired.

This is useful if you want to run some code by a timer. For example, imagine you want to implement pacman like game. If you move left the pacman will continue move left until it hit the next wall.

```python
def move(event):
    while gamepad.is_holding(event):
        print 'move',
        if event.is_move_left():
            print 'left'
        elif event.is_move_right():
            print 'right'
        elif event.is_move_up():
            print 'up'
        elif event.is_move_down():
            print 'down'
        time.sleep(1)

def move_center(event):
    print "center", event.state.get_axes()

gamepad.on('move', move)
gamepad.on('move-center', move_center)
gamepad.listen()
```

### Full example using a rgb led matrix: Snake

This is an example using another project: [arduino-matrix-rgb](https://github.com/lvidarte/arduino-matrix-rgb)

[![Snake Arduino](http://img.youtube.com/vi/qr-ROlCskwY/0.jpg)](https://www.youtube.com/watch?v=qr-ROlCskwY)

