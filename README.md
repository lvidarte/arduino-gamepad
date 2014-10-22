# Arduino Gamepad

<img src="https://github.com/lvidarte/arduino-gamepad/blob/master/gamepad.png" style="width:400px" />

### Load Arduino Sketch

Then build and upload the Arduino sketch. I use [inotool](http://inotool.org) for that

    ino build && ino upload


### Use example

Basic import

```python
from serial import Serial
from gamepad import Gamepad

serial = Serial('/dev/ttyUSB0')
gamepad = Gamepad(serial)
```

Create the callback function

```python
def start(self, event):
    print "Start!"
```

Attach the callback to an event

```python
gamepad.on('button-press', start)
```
