# Arduino Gamepad

<img src="https://github.com/lvidarte/arduino-gamepad/blob/master/gamepad.png" width="600px" />

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

<img src="https://github.com/lvidarte/arduino-gamepad/blob/master/gamepad2.png" width="600px" />

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

### Snake example

[![Snake Arduino](http://img.youtube.com/vi/qr-ROlCskwY/0.jpg)](https://www.youtube.com/watch?v=qr-ROlCskwY)
