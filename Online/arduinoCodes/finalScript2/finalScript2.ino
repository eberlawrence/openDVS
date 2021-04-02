#include <TimerOne.h>
#include <Timer.h>

#define analog_signal_port          A0

#define encoder                     2    // Receive the encoder values. Interrupt used.

#define close_hand                  3    // Prosthesis control signal A.
#define open_hand                   4    // Prosthesis control signal B.
#define PWM                         5    // Send a PWM for the H-Bridge.
#define cA                          7    // Channel A of the H-Bridge.
#define cB                          8    // Channel B of the H-Bridge.
#define initial_state_led           9

#define fs                          1000 // sampling rate of 1000 Hz
#define ts                          1000/fs // period of 1 ms
#define fw                          25 // downsampling to 20 Hz
#define timer_period                10000 // 5 ms
#define calibration_time            5000 //  time for calibrating the EMG signal -> 5 seconds

#define multiplier                  5 //
#define higher_signal_threshold     350 //
#define lower_signal_threshold      250 //  
#define time_threshold              600


Timer T1;

int sinal = 0;
bool teste = false;
short motor_speed = 100;         // Set the engine speed of rotation

volatile float Wrist_angle = 0;    // Adjust the wrist angle according to the object angle.
bool clockwise_flag = false;
bool counterclockwise_flag = false;

int numbers[fw]; //vetor com os valores para média móvel
bool calibrate = true;
int calibration_count = 0;
long raw_calibration_signal_sum = 0;
long emg_calibration_signal_sum = 0;
int signal_offset;
int funcEvent;
char state = 'a';

int emg_signal;
int raw_signal;
uint16_t retified_signal;

bool start_count = false;
bool undo = false;
bool wait = false;
int block = 1;
bool wait_signal_decrease = false;
int counter = 0;


void setup()
{
  pinMode(PWM, OUTPUT);
  pinMode(cA, OUTPUT);
  pinMode(cB, OUTPUT);
  pinMode(close_hand, OUTPUT);
  pinMode(open_hand, OUTPUT);

  pinMode(initial_state_led, OUTPUT);
  Serial.begin(115200);

  Timer1.initialize(timer_period); // 10 us
  Timer1.attachInterrupt(control_signal_callback);

  attachInterrupt(digitalPinToInterrupt(2), fix_angle, CHANGE);    // Interrupt for the encoder.
}



/* FUNCTIONS */
bool forward_flag = true;
bool backward_flag = true;


void fix_angle() {
  if (clockwise_flag == true) {
    Wrist_angle += 2.5;
  }
  else if (counterclockwise_flag == true) {
    Wrist_angle -= 2.5;
  }

  if (Wrist_angle >= 90.0 and forward_flag == true) {
    forward_flag = false;
    state = 'f';
    //    Serial.println("Entrou1");
  }
  else if (Wrist_angle < 90.0 and forward_flag == false) {
    forward_flag = true;
  }
  if (Wrist_angle <= -90.0 and backward_flag == true) {
    wait_signal_decrease = true;
    backward_flag = false;
    state = 'f';
    //    Serial.println("Entrou2");
  }
  else if (Wrist_angle > -90.0 and backward_flag == false) {
    backward_flag = true;
  }
  //  Serial.println(Wrist_angle);
}

// Rotate the wrist forward.
void forward(uint8_t mSpeed) {
  clockwise_flag = true;
  counterclockwise_flag = false;
  digitalWrite(cA, LOW);
  digitalWrite(cB, HIGH);
  analogWrite(PWM, mSpeed);
}


// Rotate the wrist backward.
void backward(uint8_t mSpeed) {
  clockwise_flag = false;
  counterclockwise_flag = true;
  digitalWrite(cA, HIGH);
  digitalWrite(cB, LOW);
  analogWrite(PWM, mSpeed);
}


// Stop the rotation.
void stop_motor() {
  clockwise_flag = false;
  counterclockwise_flag = false;
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



void control_signal_callback()
{
  if (calibrate == false) {
    raw_signal = analogRead(analog_signal_port) - signal_offset; //ler o valor da entrada analogica
    retified_signal = abs(raw_signal);
    int emg_signal = moving_average(retified_signal);
    emg_signal *= multiplier;
        Serial.print(higher_signal_threshold);
        Serial.print(",");
        Serial.print(lower_signal_threshold);
        Serial.print(",");
        Serial.println(emg_signal);


    if (block == 1) {
      digitalWrite(initial_state_led, HIGH);
    }

    if (wait == true and block == 1) {
      digitalWrite(initial_state_led, LOW);
      if (counter >= time_threshold) {
        //        Serial.println("ENTROU1");
        if (emg_signal < lower_signal_threshold) {
          block = 3;
          start_count = false;
          wait = false;
        }
      }
      else if (emg_signal < lower_signal_threshold and counter < time_threshold) {
        //        Serial.println("ENTROU2");
        block = 2;
        start_count = false;
        wait = false;
      }
    }
    else {

      if (emg_signal > higher_signal_threshold) {
        wait = true;
        start_count = true;
      }
    }

    if (start_count == true) {
      counter += 10;
    }
    else {
      counter = 0;
    }


    if (wait_signal_decrease == true) {
      if (emg_signal < lower_signal_threshold) {
        start_count = false;
        wait = false;
        undo = false;
        block = 1;
        wait_signal_decrease = false;
//        Serial.println(Wrist_angle);
      }
    }

    if (wait == true and block == 2) {
      if (undo == true) {
        if (emg_signal > higher_signal_threshold) {
          //          Serial.println("BLOCO DE PARADA");
          state = 'f';
          wait_signal_decrease = true;
        }
      }
      else {
        //        Serial.println("Bloco 2");
        if (counter >= time_threshold) {
          if (emg_signal < lower_signal_threshold and undo == false) {
            if (forward_flag == false) {
              wait_signal_decrease = true;
            }
            else {
              //            Serial.println("Bloco 2A");
              state = 'd';
              undo = true;
            }
          }
        }
        else if (emg_signal < lower_signal_threshold and counter < time_threshold and undo == false) {
          if (backward_flag == false) {
            wait_signal_decrease = true;
          }
          else {
            //          Serial.println("Bloco 2B");
            state = 'e';
            undo = true;
          }

        }
      }
    }

    if (wait == true and block == 3) {

      if (undo == true) {
        if (emg_signal > higher_signal_threshold) {
          //          Serial.println("BLOCO DE PARADA");
          state = 'a';
          wait_signal_decrease = true;
        }
      }
      else {
        //        Serial.println("Bloco 3");
        if (counter >= time_threshold) {
          if (emg_signal < lower_signal_threshold and undo == false) {
            //            Serial.println("Bloco 3A");
            Serial.println(Wrist_angle);
            state = 'b';
            undo = true;
          }
        }
        else if (emg_signal < lower_signal_threshold and counter < time_threshold and undo == false) {
          //          Serial.println("Bloco 3B");
          state = 'c';
          wait_signal_decrease = true;
        }
      }
    }
  }
}




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
      digitalWrite(close_hand, LOW);
      delay(300);
      digitalWrite(open_hand, LOW);
      delay(300);
      digitalWrite(open_hand, HIGH);
      state = 'g';
      break;
    case 'd':
      if (forward_flag == true) {
        forward(motor_speed);
      }
      state = 'g';
      break;
    case 'e':
      if (backward_flag == true) {
        backward(motor_speed);
      }
      state = 'g';
      break;
    case 'f':
      stop_motor();
      state = 'g';
      break;
    case 'g':
      break;
  } //end switch
} //end machine


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
