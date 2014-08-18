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

void init_joistick()
{
    pinMode(PIN_SW, INPUT);
    digitalWrite(PIN_SW, HIGH);
}

byte map_value(int value)
{
    return map(value, 0, 1023, 0, 63);
}

byte read_x()
{
    int x = analogRead(PIN_X);
    return map_value(x);
}

byte read_y()
{
    int y = analogRead(PIN_Y);
    return map_value(y);
}

byte read_sw()
{
    return digitalRead(PIN_SW) == 0 ? 1 : 0;
}

byte read_bt()
{
    return digitalRead(PIN_BT) == 0 ? 1 : 0;
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

void send_report()
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
    init_joistick();
    Serial.begin(9600);
}

void loop()
{
    if (Serial.available())
    {
        byte data = Serial.read();

        if (data == 0)
        {
            send_report();
        }
    }

    send_x();
    send_y();
    send_sw();
    send_bt();

    delay(10);
}
