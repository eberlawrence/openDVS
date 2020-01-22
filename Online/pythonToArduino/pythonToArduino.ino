
#define start 10
int flag = 0;

void setup()
{
  Serial.begin(9600);

  pinMode(start, INPUT_PULLUP);
}


void loop()
{
  if(digitalRead(start) == LOW)
  {
    Serial.println(1);
    delay(1000);
  }
   if(Serial.available() > 0)
  {
    int angle = Serial.read();
    Serial.println(angle);
  } 
  
//  if(digitalRead(start) == LOW)
//  {
//    flag = 1;
//    Serial.println(flag);
//    delay(1000);
//    if(Serial.available() > 0)
//    {
//      int angle = Serial.read();
//      Serial.println(angle);
//    }
//    
//  }
//  else
//  {
//    flag = 0;
//    Serial.println(flag);
//  }
  
  


    
  //Serial.println(1);
}



//void setup() 
//{
//  Serial.begin(115200);
//}
//
//void loop() 
//{
//  int sensorValue = analogRead(A0);
//  Serial.println(sensorValue);
//  delay(50); 
//}


//int inPin = 7;    
//int val = 0;     
//
//void setup() {
//  pinMode(inPin, INPUT);    
//  Serial.begin(115200);
//}
//
//void loop() {
//  val = digitalRead(inPin);  
//  Serial.println(val);
//  delay(20);
//}








//
//#define BRAKE          0
//#define CW             1
//#define CCW            2
//#define MOTOR_A        7
//#define MOTOR_B        8
//#define MOTOR_PWM      5
//
//short usSpeed = 100;  //default motor speed
//unsigned short usMotor_Status = BRAKE;
// 
//void setup()                         
//{
//  pinMode(MOTOR_A, OUTPUT);
//  pinMode(MOTOR_B, OUTPUT);
//  pinMode(MOTOR_PWM, OUTPUT);
//  Serial.begin(9600);
//}
//
//
//void motorGo(uint8_t direct, uint8_t pwm)
//{
//  if(direct == CW)
//  {
//    digitalWrite(MOTOR_A, LOW); 
//    digitalWrite(MOTOR_B, HIGH);
//  }
//  else if(direct == CCW)
//  {
//    digitalWrite(MOTOR_A, HIGH);
//    digitalWrite(MOTOR_B, LOW);      
//  }
//  else
//  {
//    digitalWrite(MOTOR_A, LOW);
//    digitalWrite(MOTOR_B, LOW);            
//  }
//  
//  analogWrite(MOTOR_PWM, pwm); 
//}
//
//void Stop()
//{
//  usMotor_Status = BRAKE;
//  motorGo(usMotor_Status, 0);
//}
//
//void Forward()
//{
//  usMotor_Status = CW;
//  motorGo(usMotor_Status, usSpeed);
//}
//
//void Reverse()
//{
//  usMotor_Status = CCW;
//  motorGo(usMotor_Status, usSpeed);
//}
//
//
//void loop() 
//{
//  Forward();
//  delay(2000);
//  Stop();
//  delay(1000);
//  Reverse();
//  delay(2000);
//  Stop();
//  delay(1000);
//}
//
