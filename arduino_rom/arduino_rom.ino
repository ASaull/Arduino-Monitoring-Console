#include <stdlib.h>

// constant locations of pins
const int audio_pin = 3;
const int mute_pin = 2;
//const int ledPin = 13;       // the pin that the LED is attached to
const int cpu_pin = 11;
const int ram_pin = 10;
const int gpu_pin = 9;
const int cpu_led_pin = 13;
const int ram_led_pin = 12;
const int gpu_led_pin = 8;
const int motor_pin = 12;
const int volume_pin = A0;


// Variables will change:
int audio_state = 0;          // current state of the button
int last_audio_state = 0;     // previous state of the button
int mute_state = 0;           // current state of the button
int last_mute_state = 0;      // previous state of the button
int volume = 0;               // volume reading from the volume dial
double volume_percent_f;      //volume as a percentage
int volume_percent;
int last_volume_percent;      //previous volume percent
double cpu_percent;
double ram_percent;
double gpu_percent;
unsigned long lastUpdated = millis();
char s[4]; // a character array to store incoming serial commands.
char next; // the next place to insert into s
char type; // the type of command we have received from the PC. ex. 'c' to change cpu dial
char value[3]; // the value given by the command. ex. '57' to change cpu dial to 57%
unsigned char v_read = 0;
unsigned int v_sum = 0;

void setup() {
  // initialize the button pin as a input:
  pinMode(audio_pin, INPUT);
  pinMode(mute_pin, INPUT_PULLUP);
  // initialize the cpu as an output:
  pinMode(cpu_pin, OUTPUT);
  pinMode(cpu_led_pin, OUTPUT);
  pinMode(ram_pin, INPUT);
  pinMode(motor_pin, OUTPUT);
  // initialize serial communication:
  Serial.begin(9600);
  Serial.setTimeout(10);
  
  analogWrite(cpu_pin, 225/2);
  analogWrite(ram_pin, 236/2);
  analogWrite(gpu_pin, 255/2);
}


void loop() {
  
  // The audio switch is currently not implemented due to hardware limitations.
  
  ///////////////// AUDIO SWITCH /////////////////
  /*// read the pushbutton input pin:
  audio_state = digitalRead(audio_pin);

  // compare the buttonState to its previous state4
  if (audio_state != last_audio_state) {
    // if the state has changed, increment the counter
    ////////////////////////////////Serial.println("audiotoggle");
    delay(50);
  }
  // save the current state as the last state, for next time through the loop
  last_audio_state = audio_state;*/

  /////////////////// VOLUME DIAL //////////////////
  // read the volume
  volume = analogRead(volume_pin);
  v_sum += volume;
  v_read += 1;
  if (v_read == 10)
  {
      volume_percent_f = (double)v_sum / 10230;
      volume_percent = 100 * volume_percent_f;
      v_sum = 0;
      v_read = 0;

      if (abs(volume_percent - last_volume_percent) > 0)
      {
        Serial.print("v");
        Serial.println(volume_percent);
        last_volume_percent = volume_percent;
      }
  }

  /////////////////// MUTE BUTTON //////////////////
  // read the pushbutton input pin:
  mute_state = digitalRead(mute_pin);

  // compare the buttonState to its previous state4
  if (mute_state != last_mute_state) {
    // if the state has changed, we figure out what it changed to
    if (mute_state == LOW) Serial.println("mute");
    else Serial.println("unmute");
    // the switch state will not be stable initially, wait a bit
    delay(50);
  }
  // save the current state as the last state, for next time through the loop
  last_mute_state = mute_state;
  
  //We always read lines from serial
  if (Serial.available() > 0)
  {
    int i = Serial.read();
    if (i != 10) // 10 is the ASCII line feed character
    {
      s[next] = i;
      next++;
    }
    else // this is the end of the line, terminate the string s and create type and value
    {
      s[next] = '\0';
      next = 0;
      type = s[0];
      memcpy(value, &s[1], 3);
    }
  }

  ////////////////// PROCESSING COMMAND TYPES ///////////////////////

  if (type == 'c') // we will write value to the cpu pin
  {
    cpu_percent = atof(value);
  
    if (cpu_percent > 97)
    {
      cpu_percent = 97, digitalWrite(cpu_led_pin, HIGH);
    }
    else
    {
      digitalWrite(cpu_led_pin, LOW);
    }
    int cpu_write = int(cpu_percent / 100 * 230);
    analogWrite(cpu_pin, cpu_write);
    lastUpdated = millis();

    //we reset type so that we dont run this code again until we have a new type
    type = NULL;
  }
  
  if (type == 'r') // we will write value to the ram pin
  {
    ram_percent = atof(value);
  
    if (ram_percent > 90)
    {
      digitalWrite(ram_led_pin, HIGH);
    }
    int ram_write = int(ram_percent / 100 * 234);
    analogWrite(ram_pin, ram_write);

    //we reset type so that we dont run this code again until we have a new type
    type = NULL;
  }
  
  if (type == 'g') // we will write value to the gpu pin
  {
    gpu_percent = atof(value);
  
    if (gpu_percent > 90)
    {
      digitalWrite(gpu_led_pin, HIGH);
    }
    int gpu_write = int(gpu_percent / 100 * 218);
    analogWrite(gpu_pin, gpu_write);

    //we reset type so that we dont run this code again until we have a new type
    type = NULL;
  }

  // If the computer is no longer providing updates, we reset the dials.
  // This is necessary in the event the PC side script is terminated, or
  // the computer is powered off while still providing power to the Arduino.
  if (millis() - lastUpdated > 1000)
  {
    analogWrite(gpu_pin, 0);
    analogWrite(cpu_pin, 0);
    analogWrite(ram_pin, 0);
  }

  Serial.flush();
}
