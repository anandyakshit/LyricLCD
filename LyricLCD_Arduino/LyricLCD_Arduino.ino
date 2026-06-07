#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

String incoming = "";

void setup()
{
    Serial.begin(9600);

    lcd.init();
    lcd.backlight();

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("LyricLCD");
}

void loop()
{
    while (Serial.available())
    {
        char c = Serial.read();

        if (c == '\n')
        {
            displayPacket(incoming);
            incoming = "";
        }
        else
        {
            incoming += c;
        }
    }
}

void displayPacket(String packet)
{
    packet.trim();

    int sep = packet.indexOf('|');

    String line1 = "";
    String line2 = "";

    if (sep >= 0)
    {
        line1 = packet.substring(0, sep);
        line2 = packet.substring(sep + 1);
    }
    else
    {
        line1 = packet;
    }

    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print(line1);

    lcd.setCursor(0, 1);
    lcd.print(line2);
}