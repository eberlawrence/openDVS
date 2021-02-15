#include <TimerOne.h>
#include <Timer.h>

#define analog_signal_port    A0

#define encoder               2    // Receive the encoder values. Interrupt used.

#define close_hand            3    // Receive the button status used for closing the hand. Interrupt used.
#define open_hand             4    // Send a HIGH level to change the grasp type and open the hand.

#define PWM                   5    // Send a PWM for the H-Bridge.
#define cA                    7    // Channel A of the H-Bridge.
#define cB                    8    // Channel B of the H-Bridge.

#define laser                 12

#define threshold             30

#define fs 500
#define ts 1000/fs // 1/hz
#define fw 20


Timer T1;

int graspType;                  // Store the grasp type as "int".
int graspTypeAux = 0;           // Store the last grasp type selected.
bool flag = false;              // Flag to avoid the repetition of the first condition.
int data[2];                    // Store received data obteined from Python through serial port.
short motorSpeed = 120;         // Set the engine speed of rotation
int objectAngle;                // Store the object angle.
volatile int WristAngle = 0;    // Adjust the wrist angle according to the object angle.

bool waiting_start_flag = true;
int min_contraction_count = 0;

long current_time = 0;


int NONRET_AD;
int F_AD;   //recebe o valor original filtrado
int numbers[fw]; //vetor com os valores para média móvel
uint16_t AD;
bool calibrate = true;
int a = 0;
long offset = 0;
int finalOffset;
int funcEvent;
int count = 0;
bool change_move = false;
int time_move = 0;
bool first_close = false;
int soma;

void setup()
{
  pinMode(encoder, INPUT);

  pinMode(PWM, OUTPUT);
  pinMode(cA, OUTPUT);
  pinMode(cB, OUTPUT);

  pinMode(close_hand, OUTPUT);
  pinMode(open_hand, OUTPUT);

  pinMode(laser, OUTPUT);

  Serial.begin(115200);

  Timer1.initialize(10000);
  Timer1.attachInterrupt(control_signal_callback);

  attachInterrupt(digitalPinToInterrupt(2), fixAngle, CHANGE);    // Interrupt for the encoder.
}



/* FUNCTIONS */


// Rotate the wrist forward.
void Forward(uint8_t mSpeed) {
  digitalWrite(cA, LOW);
  digitalWrite(cB, HIGH);
  analogWrite(PWM, mSpeed);
}


// Rotate the wrist backward.
void Backward(uint8_t mSpeed) {
  digitalWrite(cA, HIGH);
  digitalWrite(cB, LOW);
  analogWrite(PWM, mSpeed);
}


// Stop the rotation.
void Stop() {
  digitalWrite(cA, LOW);
  digitalWrite(cB, LOW);
  analogWrite(PWM, 0);
}


// Used on the first interrupt. Fix the angle wrist according to the object angle, incrementing or decrementing it.
void fixAngle() {
  bool wait = true;
  if (objectAngle > WristAngle) {
    WristAngle++;
    wait = false;
  }
  if (objectAngle < WristAngle) {
    WristAngle--;
    wait = false;
  }
  else if (objectAngle == WristAngle) {
    Stop();
  }
}

// Rotate the engine if there is a mismatch between the angles.
void rotateMotor(int new_angle)
{
  if (WristAngle < new_angle)
  {
    Forward(motorSpeed);
  }
  else if (WristAngle > new_angle)
  {
    Backward(motorSpeed);
  }
}

long moving_average()
{
  for (int i = fw - 1 ; i > 0 ; i--) {
    numbers[i] = numbers[i - 1];
  }
  numbers[0] = AD;
  long acc = 0;
  for (int i = 0 ; i < fw ; i++) {
    acc += numbers[i];
  }
  return acc / fw;
}

void control_signal_callback()
{
  NONRET_AD = analogRead(analog_signal_port) - finalOffset; //ler o valor da entrada analogica
  AD = abs(NONRET_AD);
  int emg_signal = moving_average();
  emg_signal *= 2;
  Serial.println(emg_signal);
  if (change_move == true) {
    digitalWrite(open_hand, LOW);
    if (time_move == 100) {
      digitalWrite(open_hand, HIGH);
      digitalWrite(close_hand, LOW);
      change_move = false;
      time_move = 0;
    }
    time_move += 10;
  }
  else if (first_close = true) {
    digitalWrite(close_hand, LOW);
    digitalWrite(open_hand, HIGH);
  }

  //  start func
  if (waiting_start_flag == true) {
    if (emg_signal > threshold) {
      if (count == 0) {
        count++;
        current_time += 10;
      }
      else {
        current_time += 10;
        if (current_time > 200) {
          digitalWrite(close_hand, HIGH);
          digitalWrite(open_hand, LOW);
          first_close = true;
        }
      }
    }
    else if (emg_signal < threshold and count == 1) {
      count = 0;
      if (current_time <= 200) {
        waiting_start_flag = false;
        objectAngle = 0;
        rotateMotor(objectAngle);
        digitalWrite(laser, HIGH);
      }
      else {
        current_time = 0;
      }
    }

  }
}


void getOffset() {
  int emgSignal = analogRead(A0);
  offset = offset + emgSignal;
  a++;
}

void loop()
{
  while (calibrate == true) {
    T1.update();
    if (a < 5000) {
      T1.every(ts, getOffset);
    }
    else {
      finalOffset = offset / a;
      T1.stop(funcEvent);
      calibrate = false;
    }
  }
  if (calibrate == false) {
    if (waiting_start_flag == false) {
      Serial.println("start"); // Write "1", then the acquisition in Python starts.
      waiting_start_flag = true;
      delay(50);
    }

    if (Serial.available() and waiting_start_flag == true) {
      delay(50);
      for (int i = 0; i < Serial.available() + 1; i++) {
        data[i] = Serial.read();    // Store received data, that is both grasp type and object angle.
      }
      graspType = data[0];
      objectAngle = (int)(data[1] - 45);   // Subtract the offset inserted in python script.
      rotateMotor(objectAngle);    // Start to rotate the motor if the angles are different.
      if (graspType != graspTypeAux) {    // Change the grasp, if the grasp type received and the last grasp type are different.
        graspTypeAux = graspType;
        change_move = true;
      }
      waiting_start_flag = true; // Reset the system.
      digitalWrite(laser, LOW);
    }
  }
}
