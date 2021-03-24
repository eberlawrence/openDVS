
#define time_per_revolution 20000000 // 20 seconds
#define steps_per_revolution 3200

int PUL = 3; //define Pulse pin
int DIR = 2; //define Direction pin
int ENA = 5; //define Enable Pin
bool flag = true;

void setup() {
  pinMode (PUL, OUTPUT);
  pinMode (DIR, OUTPUT);
  pinMode (ENA, OUTPUT);
}

void loop() {

  if (Serial.available()) {
    input = Serial.read();
    Serial.print("Digite o ângulo de -90 até +90: " );
    Serial.println(input);
  }
  //  if (flag == true) {
  //    delay(500);
  //    float time_per_step = time_per_revolution / steps_per_revolution;
  //
  //    for (int i = 0; i < steps_per_revolution; i++)
  //    {
  //      digitalWrite(DIR, LOW);
  //      digitalWrite(ENA, HIGH);
  //      digitalWrite(PUL, HIGH);
  //      delayMicroseconds(time_per_step / 2);
  //      digitalWrite(PUL, LOW);
  //      delayMicroseconds(time_per_step / 2);
  //    }
  //    flag = false;
  //  }
}
