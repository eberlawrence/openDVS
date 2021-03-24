#include <TimerOne.h>
#include <Timer.h>

#define analog_signal_port    A0
#define close_hand            3    // Prosthesis control signal A.
#define open_hand             4    // Prosthesis control signal B.
#define PWM                   5    // Send a PWM for the H-Bridge.
#define cA                    7    // Channel A of the H-Bridge.
#define cB                    8    // Channel B of the H-Bridge.


#define fs                    1000 // sampling rate of 1000 Hz
#define ts                    1000/fs // period of 1 ms
#define fw                    10 // downsampling to 20 Hz
#define timer_period          10000 // 5 ms
#define calibration_time      5000 //  time for calibrating the EMG signal -> 5 seconds

#define multiplier            5 //
#define signal_threshold      200 //  

Timer T1;

short motorSpeed = 120;         // Set the engine speed of rotation

bool waiting_start_flag = true;
int min_contraction_count = 0;

long current_time = 0;

int numbers[fw]; //vetor com os valores para média móvel
bool calibrate = true;
long raw_calibration_signal_sum = 0;
long emg_calibration_signal_sum = 0;
int signal_offset;
int funcEvent;
int count = 0;
bool change_move = false;
int time_move = 0;
bool first_close = false;

char state = 'a';

int emg_signal;
int raw_signal;
uint16_t retified_signal;




void setup()
{
  pinMode(PWM, OUTPUT);
  pinMode(cA, OUTPUT);
  pinMode(cB, OUTPUT);
  pinMode(close_hand, OUTPUT);
  pinMode(open_hand, OUTPUT);

  Serial.begin(115200);

  Timer1.initialize(timer_period); // 10 us
  Timer1.attachInterrupt(control_signal_callback);

}



/* FUNCTIONS */


// Rotate the wrist forward.
void forward(uint8_t mSpeed) {
  digitalWrite(cA, LOW);
  digitalWrite(cB, HIGH);
  analogWrite(PWM, mSpeed);
}


// Rotate the wrist backward.
void backward(uint8_t mSpeed) {
  digitalWrite(cA, HIGH);
  digitalWrite(cB, LOW);
  analogWrite(PWM, mSpeed);
}


// Stop the rotation.
void stop_motor() {
  digitalWrite(cA, LOW);
  digitalWrite(cB, LOW);
  analogWrite(PWM, 0);
}


long moving_average(uint16_t retified_signal)
{
  for (int i = fw - 1 ; i > 0 ; i--) {
    numbers[i] = numbers[i - 1];
  }
  numbers[0] = retified_signal;
  long acc = 0;
  for (int i = 0 ; i < fw ; i++) {
    acc += numbers[i];
  }
  return acc / fw;
}


bool signal_up = true;
bool first_spike = true;
int border_count = 0;
bool start_count = false;
bool end_task = false;

bool wait = false;
bool allowed = false;
int block = 1;


void control_signal_callback()
{
  if (calibrate == false) {
    raw_signal = analogRead(analog_signal_port) - signal_offset; //ler o valor da entrada analogica
    retified_signal = abs(raw_signal);
    int emg_signal = moving_average(retified_signal);
    emg_signal *= multiplier;
    //    Serial.print(count);
    //    Serial.print(",");
    //    Serial.print(block * 100);
    //    Serial.print(",");
    //    Serial.println(emg_signal);


    if (emg_signal > signal_threshold and wait == false) {
      start_count = true;
      Serial.println(block);
      wait = true;
    }
    
    if (emg_signal < signal_threshold and start_count == false) {
      allowed = true;
    }

    if (start_count == true and block == 1) {
      //      Serial.println(count);
      if (count == 200) {
        Serial.println("Entrou 1");
        if (emg_signal < signal_threshold) {
          Serial.println("Entrou 1.1");
          block = 2;
          start_count = false;
          allowed = false;
          wait = false;
          count = 0;
        }
        else if (emg_signal >= signal_threshold) {
          Serial.println("Entrou 1.2");
          block = 3;
          start_count = false;
          allowed = false;
          wait = false;
          count = 0;
        }
      }
      else {
        count += 10;
      }
    }
    else if (start_count == true and block == 2 and allowed == true) {
      if (count == 200) {
        Serial.println("Entrou 2");
        if (emg_signal < signal_threshold) {
          Serial.println("Entrou 2.1");
          state = 'd';
          count = 0;
        }
        else if (emg_signal >= signal_threshold) {
          Serial.println("Entrou 2.2");
          state = 'e';
          start_count = false;
          count = 0;
        }
      }
      else {
        count += 10;
      }
    }
    else if (start_count == true and block == 3 and allowed == true) {
      if (count == 200) {
        Serial.println("Entrou 3");
        if (emg_signal < signal_threshold) {
          Serial.println("Entrou 3.1");
          state = 'c';
          count = 0;
          start_count = false;
        }
        else if (emg_signal >= signal_threshold) {
          Serial.println("Entrou 3.2");
          state = 'b';
          count = 0;
          start_count = false;
        }
      }
      else {
        count += 10;
      }
    }
  }
}

int old_state = 0;


void machine()
{
  unsigned long time_now = 0;
  switch (state)
  {
    case 'a':
      digitalWrite(close_hand, LOW);
      digitalWrite(open_hand, HIGH);
      state = 'g';
      break;
    case 'b':
      digitalWrite(close_hand, HIGH);
      digitalWrite(open_hand, LOW);
      state = 'g';
      break;
    case 'c':
      digitalWrite(open_hand, HIGH);
      delay(200);
      digitalWrite(open_hand, LOW);
      delay(200);
      digitalWrite(open_hand, HIGH);
      state = 'g';
      break;
    case 'd':
      forward(motorSpeed);
      state = 'g';
      break;
    case 'e':
      backward(motorSpeed);
      state = 'g';
      break;
    case 'f':
      stop_motor();
      state = 'g';
      break;
    case 'g':
      break;
  } //end switch
  old_state = state;
} //end machine


int calibration_count = 0;

void getOffset() {
  int raw_calibration_signal = analogRead(analog_signal_port);
  raw_calibration_signal_sum = raw_calibration_signal_sum + raw_calibration_signal;
  calibration_count++;
}

void loop()
{
  while (calibrate == true) {
    T1.update();
    if (calibration_count < calibration_time) {
      T1.every(ts, getOffset);
    }
    else {
      signal_offset = raw_calibration_signal_sum / calibration_count;
      T1.stop(funcEvent);
      calibrate = false;
    }
  }
  if (calibrate == false) {
    machine();
  }
}
