# SoundStrips

SoundStrips is a personal project made by me (Sohaib Khadri) to control LED light strips using the Audio outputting from a computer. Using pyaudio and serial, SoundStrips processes audio outputting from any audio device on your computer in **realtime** to control your LED light strips so that you can sync them with movies, video games, music, microphones, and more! This project was made and tested using Windows 10, python 3.8, a ws2812b 150 LED addressable light strip, and an Arduino MEGA 2560.

## Wiring Instructions
 This project was made to minimize hardware audio processing and find a way to directly control the lights in a simple yet efficient way using software-side audio processing in python. Due to this approach, the only required parts are:

- an Arduino
- strip of **addressable** LED lights 
- 5V power adapter to power the strip
- 300-500 ohm resistor

Each LED on a strip uses about 50mA when set to full brightness so make sure to use a 5V power adapter that can output more than (50mA * # of LEDs).

### Instructions
1. LED light strip Ground & Arduino Ground <--> Power Adapter Ground
2. LED light strip 5V <--> Power Adapter 5V
3. LED light strip Data <--> 300-500 ohm resistor <--> Arduino DATA PIN 5
4. Arduino USB-B <--> Computer USB-A

## Installation

### Arduino (Client)
Since the Arduino saves and runs the most recent uploaded script on startup. This code will only need be uploaded to the Arduino once:

1.  Make sure your Arduino is using serialport COM3.

2. Run and Upload "SoundStrips-Client" on your Arduino.

### Computer (Server)
The python file has already been built and can be directly run as an application.

1. Navigate to the "Sound Control Panel" in your "Sound Settings". Under "Recording", enable the "Stereo Mix" device.

2. Start up the application, click the gear icon and refresh the device list to display all the current recording devices on your computer. For general audio outputted through applications, click "Stereo Mix" and push select.

3. Go back to the main menu by hitting the menu icon, and customize how your lights will react to the sound.
4. Hit the power button to start the light show.

 If need be, you can tweak the python file for troubleshooting or customization and rebuild the application. (See Troubleshooting)


## Using the SoundStrips App

The SoundStrips application uses the tkinter GUI system to make interfacing easier.



![SoundStrips GUI](SoundStrips GUI.JPG) ![SoundStrips GUI2](SoundStrips GUI2.JPG)

### Power
The Power Button can turn on and off the lights. The power will automatically be turned off when a new audio device is selected and will have to be turned on again manually. Make sure to turn the power off before exiting the application so the serialport closes and is not left opened.

### Presets
Presets you've made can be chosen from the dropdown and loaded in using the load button and deleted using the delete button. A preset saves the color, volume threshold, brightness, and the fade speed. It does NOT save which device you were using.

### Customize
The customize menu is used to change how the lights react.
- The volume threshold sets the bar that the current volume has to reach to turn on the lights. This setting, unlike the rest, works in realtime and does not need to be uploaded to the Arduino for changes to take effect. Using the live feed can help you decide what value to set this at.
- The brightness slider is very self explanatory. 
- The fade speed slider sets how fast the lights fade out after being turned on.
- The color button sets the color of the lights.
  
- Using the save button will save all the above settings into a preset. Presets are case sensitive and cannot have the same name.
- Press the upload button to send the current set values to the Arduino. You must hit upload for the changes to take place.

### Live Feed
 The live feed can be paused and played and will show the current audio devices volume output. Use this to help set the volume threshold. The live feed will sometimes show in the top left of fullscreen games and applications to help you determine a good volume threshold aswell (experimental).

### Settings 
 Select what audio device you want the application to listen to. Refresh the list using the refresh button and select a device with the select button. (Stereo Mix and Microphone have been tested to work)

The "Reset all Settings" button will reset the application to the default presets and device.

## Troubleshooting

 The application "SoundStrips-Server" must always have the "images" folder, LICENSE.txt, and README.txt in the same directory for the application to start.

 Although this project calls for addressable LED light strips, it is possible to get this working for any light or component that can be interfaced using an Arduino by altering the code in the arduino file.

 If need be, you can alter the python file to work better for yourself, customization, or troubleshooting. To rebuild the application, navigate to the .py file location using windows powershell and build using pyinstaller (python 3.x and containing libraires required):

```bash
pyinstaller.exe --onefile --windowed --icon.ico=images\icon.ico SoundStrips-Server.py
```

For other issues or help, feel free to [email me](mailto:sohaibx@live.ca).

## External Libraries Used

- [FastLED](https://github.com/FastLED/FastLED)
- [Pyaudio](https://pypi.org/project/PyAudio/)
- [Pyserial](https://pythonhosted.org/pyserial/)
- [audiooop](https://docs.python.org/2/library/audioop.html) 
- [ttkthemes](https://ttkthemes.readthedocs.io/en/latest/)
- [pyinstaller](https://www.pyinstaller.org/)



## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)