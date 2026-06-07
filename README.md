# LyricLCD

This Project displays synchronized song lyrics from your PC on a 16x2 LCD using Arduino Uno R4 Minima and Python.

Features:
  1) Automatically detects what song is being played.
  2) Fetches the lyrics for the song automatically.
  3) Auto syncs the lyrics and the song.
  4) Displays the Lyrics on the 16x2 LCD.

Hardware Required:
  1) Arduino Uno R4 Minima/Arduino Uno R3
  2) Jumper Wires
  3) 16x2 I2C LCD
  4) USB Data cable compatible with your Arduino

Software Required:
  1) Arduino IDE
  2) Python (3.12 or any version that supports winsdk library)
  3) Any music player that windows considers as a Media Session when opened.

Python Libraries which require Installation:
  1) winsdk
  2) requests
  3) pyserial

Wiring:
       I2C    |   Arduino 
    1)   VCC ----> 5V
    2)   GND ----> GND
    3)   SDA ----> A4
    4)   SCL ----> A5




