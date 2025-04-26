#include <Servo.h>

Servo joint_1, joint_2;
float q1, q2;
float x[20];
float y[20];
int size;
String data;  

// Parameters 
float l1=10;
float l2=9.5;


/* ------------------------------ FUNCTIONS ------------------------------ */

void Inverse_Kin(float px, float py) {
  float cosq2 = (pow(px,2)+ pow(py,2) - pow(l1,2)-  pow(l2,2))/(2*l1*l2);
}

void draw_line(float x_start, float y_start, float x_end, float y_end, float u) {
 
}

/* ------------------------------ SETUP ------------------------------ */

void setup() {
  joint_1.attach(9);
  joint_2.attach(10);

  Inverse_Kin(0,10);

  Serial.begin(9600);
}

/* ------------------------------ LOOP ------------------------------ */

void loop() {
  //--------- COMMUNICATION ---------//
  size = 0;
  while (true) {
    if (Serial.available() > 0) {
      data = Serial.readStringUntil('\n');  // Read until newline
      if (data == "stop"){ 
        Serial.println("ACK");
        break;
      }

      int commaIndex = data.indexOf(',');
      if(commaIndex != -1) {
        Serial.println("ACK");

        x[size] = data.substring(0, commaIndex).toFloat();
        y[size] = data.substring(commaIndex + 1).toFloat();
        size++;
      }
    } 
  }

  //--------- KINEMATICS ---------//
  
  
}
