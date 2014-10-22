# Arduino Gamepad

![Fritzing blueprint](https://github.com/lvidarte/arduino-gamepad/blob/master/gamepad.png =400x)

### Load Arduino Sketch

Then build and upload the Arduino sketch. I use [inotool](http://inotool.org) for that

    ino build && ino upload


### Use example

Basic import

    from serial import Serial
    from gamepad import Gamepad

    serial = Serial('/dev/ttyUSB0')
    gamepad = Gamepad(serial)

Create the callback function

    def start(self, event):
        print "Start!"

Attach the callback to an event

    gamepad.on('button-press', start)
