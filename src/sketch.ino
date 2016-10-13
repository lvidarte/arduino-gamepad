/*
Author: Leo Vidarte <http://nerdlabs.com.ar>

This is free software:
you can redistribute it and/or modify it
under the terms of the GPL version 3
as published by the Free Software Foundation.

*/

#define SERIAL_SPEED 9600

#define PIN_X  A0
#define PIN_Y  A1
#define PIN_SW 5

#define PIN_BT 3
#define PWR_BT 2

#define CMD_X  B00000000
#define CMD_Y  B01000000
#define CMD_SW B10000000
#define CMD_BT B11000000

byte last_x  = 255;
byte last_y  = 255;
byte last_sw = 255;
byte last_bt = 255;

void init_button()
{
    pinMode(PIN_BT, INPUT);
    digitalWrite(PWR_BT, HIGH);
}

void init_joystick()
{
    pinMode(PIN_SW, INPUT);
    digitalWrite(PIN_SW, HIGH);
}

byte map_axis(int axis)
{
    return map(axis, 0, 1023, 0, 63);
}

byte read_x()
{
    int x = analogRead(PIN_X);
    return map_axis(x);
}

byte read_y()
{
    int y = analogRead(PIN_Y);
    return map_axis(y);
}

byte read_sw()
{
    return ! digitalRead(PIN_SW);
}

byte read_bt()
{
    return ! digitalRead(PIN_BT);
}

void send_x()
{
    byte x = read_x();

    if (last_x != x) {
        last_x = x;
        send(CMD_X, x);
    }
}

void send_y()
{
    byte y = read_y();

    if (last_y != y) {
        last_y = y;
        send(CMD_Y, y);
    }
}

void send_sw()
{
    byte sw = read_sw();

    if (last_sw != sw) {
        last_sw = sw;
        send(CMD_SW, sw);
    }
}

void send_bt()
{
    byte bt = read_bt();

    if (last_bt != bt) {
        last_bt = bt;
        send(CMD_BT, bt);
    }
}

void send_status()
{
    send(CMD_X, last_x);
    send(CMD_Y, last_y);
    send(CMD_SW, last_sw);
    send(CMD_BT, last_bt);
}

void send(byte cmd, byte value)
{
    Serial.write(cmd | value);
}

void setup()
{
    init_button();
    init_joystick();
    Serial.begin(SERIAL_SPEED);
}

void loop()
{
    if (Serial.available() && Serial.read() == 0)
    {
        send_status();
    }

    send_x();
    send_y();
    send_sw();
    send_bt();

    delay(10);
}
