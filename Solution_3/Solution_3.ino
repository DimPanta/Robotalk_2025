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
  // float cosq2, sinq2;
  // float d1, d2, a;

  float cosq2 = (pow(px, 2) + pow(py, 2) - pow(l1, 2) - pow(l2, 2)) /(2*l1*l2);
  cosq2 = constrain(cosq2,-1.0,1.0);
  float sinq2 = sqrt(1 - pow(cosq2,2));
  q2 = atan2(sinq2, cosq2);

  float d1 = l1 + l2*cosq2;
  float d2 = l2*sinq2;
  float a = atan2(d2,d1);

  q1 = atan2(py,px) - a;

  q1 = (q1 * 180)/PI;
  q2 = (q2 * 180)/PI;

  joint_1.write(q1);
  joint_2.write(q2);
}

void line(float x_start, float y_start, float x_end, float y_end, float u) {
  float px = x_start;
  float py = y_start;

  Inverse_Kin(px, py);

  delay(100);

  for (float s = u; s < 1.0 + u/2; s += u) {
    px = x_start + s * (x_end - x_start);
    py = y_start + s * (y_end - y_start);

    Inverse_Kin(px, py);

    delay(100);
  }
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
  Inverse_Kin(x[0], y[0]);
  delay(1000);


  for(int i=0; i<=(size-2); i++) {
    line(x[i], y[i], x[i+1], y[i+1], 0.05);
    delay(10);
  }
  
}
