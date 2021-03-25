
#define time_per_revolution 2000000 // 2 seconds
#define steps_per_revolution 3200   // 3200 steps
#define angle_per_step 0.1125       // 0.1125 degrees


int PUL = 3; //define Pulse pin
int DIR = 2; //define Direction pin
int ENA = 5; //define Enable Pin
bool start_flag = true;

float time_per_step = time_per_revolution / steps_per_revolution;

void setup() {
  pinMode (PUL, OUTPUT);
  pinMode (DIR, OUTPUT);
  pinMode (ENA, OUTPUT);
  Serial.begin(115200);
}


int angle = 0;
int sign = 1;
int steps = 0;

void loop() {
  if (start_flag == true) {
    Serial.println("Digite o ângulo de -90 até +90:" );
    Serial.print("\n");
    start_flag = false;
  }


  if ( Serial.available())
  {
    char ch = Serial.read();
    if (ch >= '0' && ch <= '9') {
      angle = (angle * 10) + (ch - '0');
    }
    else if ( ch == '-') {
      sign = -1;
    }
    else  {
      angle = angle * sign ;
      Serial.print("Ângulo: ");
      Serial.print(angle);
      Serial.print(" graus\n\n\n");


      steps = round(abs(angle) / angle_per_step);

      if (angle > 0) {
        for (int i = 0; i < steps; i++)
        {
          digitalWrite(DIR, LOW);
          digitalWrite(ENA, HIGH);
          digitalWrite(PUL, HIGH);
          delayMicroseconds(time_per_step / 2);
          digitalWrite(PUL, LOW);
          delayMicroseconds(time_per_step / 2);
        }
      }
      else if (angle < 0) {
        for (int i = 0; i < steps; i++)
        {
          digitalWrite(DIR, HIGH);
          digitalWrite(ENA, HIGH);
          digitalWrite(PUL, HIGH);
          delayMicroseconds(time_per_step / 2);
          digitalWrite(PUL, LOW);
          delayMicroseconds(time_per_step / 2);
        }
      }

      angle = 0;
      sign = 1;
      start_flag = true;
    }
  }
}
