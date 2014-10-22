# Arduino Gamepad

<img src="https://github.com/lvidarte/arduino-gamepad/blob/master/gamepad.png" width="400px" />

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
def start(self, event):
    print "Start!"
```

Attach the callback to an event

```python
gamepad.on('button-press', start)
```

### Snake example

<iframe width="560" height="315" src="//www.youtube.com/embed/qr-ROlCskwY" frameborder="0" allowfullscreen></iframe>
