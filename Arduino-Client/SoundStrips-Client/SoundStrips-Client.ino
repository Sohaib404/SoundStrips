/*
SoundStrips-Client.ino: Arduino Sketch that communicates with the SoundStrips GUI python application through serialport COM3.

Author: Sohaib Khadri
Copyright: GPLv3 2020, Sohaib Khadri

*/


#include <FastLED.h> //library used to interface with the LED strip

#define LED_PIN     5
#define NUM_LEDS    150
#define BRIGHTNESS  255
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
// aray holding LED color values
CRGB leds[NUM_LEDS];

#define UPDATES_PER_SECOND 75
// initialzing global variables
char incomingData = 0;
int incomingVal = 0;

CRGB color = CRGB::Red;
int red = 255;
int green = 0;
int blue = 0;
float fade_speed = 12.5;

void setup() {
    // setup delay
    delay(2000);
    // initialize LED strip
    FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
    FastLED.setBrightness(BRIGHTNESS);
    
    //link with com3
    Serial.begin(9600);
    Serial.setTimeout(50); 

    // setup flash
      for(int i = 0; i < NUM_LEDS; i++) {
        leds[i] = CRGB(red, green, blue);
    }
}

// flash used to test settings after changing them
void flash() {
        for(int i = 0; i < NUM_LEDS; i++) {
        leds[i] = CRGB(red, green, blue);
    }
}

// applying new settings
void changeVals() {

  char newSettings[16];
  bool cont = true;
  // i is number of characters in new settings string, used later to split string
  int i = 0;
    while(cont) {
        while(!(Serial.available() > 0)) {
            // waitingn for next available character
        }

        // reading characters in new settings string
        newSettings[i] = Serial.read();
        
        // checking for end of new settings string
        if(newSettings[i] == '.') {
          cont = false;
        }
        
        i++;
     }

  //converting new settings string to fade and RGB color values
  String newFade;
  String newR;
  String newG;
  String newB;
  int k = 0;
  for (int j=0; j < i-1; j++) {

        
    if(newSettings[j] == ',') {
      k++;

    } else {
      switch (k) {
          case 0:
            newFade = String(newFade + newSettings[j]);
            break;
          case 1:
            newR = String(newR + newSettings[j]);
            break;
          case 2:
            newG = String(newG + newSettings[j]);
            break;
          case 3:
            newB = String(newB + newSettings[j]);
            break;
      }
    }      
  }

  fade_speed = newFade.toInt();
  red = newR.toInt();
  green = newG.toInt();
  blue = newB.toInt();

  // test lights with new settings
  flash();

}

void loop() {


  if(Serial.available() > 0) {
    
    incomingData = Serial.read();
    incomingVal = atoi(&incomingData);

    if(incomingVal == 9) {      
      changeVals();
      return;
    }
    
    Serial.print(incomingVal);

    for(int i = 0; i < NUM_LEDS; i++) {
      leds[i] = CRGB(red, green, blue);
    }
    
  } else {
    for(int i = 0; i < NUM_LEDS; i++) {
      leds[i].fadeToBlackBy(fade_speed*(256/100));
    }      
  }

  //display LEDs
  FastLED.show();
  FastLED.delay(1000 / UPDATES_PER_SECOND);
}
