
#define encoder        2
#define cA             7
#define cB             8
#define PWM            5
#define start          10

int graspType;
bool flag = false;
int data[5];
short motorSpeed = 50; 
int angleObject = 48;
volatile byte angleHand = 0;
 
void setup()                         
{
  pinMode(encoder, INPUT);
  pinMode(cA, OUTPUT);
  pinMode(cB, OUTPUT);
  pinMode(PWM, OUTPUT);
  pinMode(start, INPUT_PULLUP);
  Serial.begin(115200);

  attachInterrupt(0, fixAngle, RISING);
}


void Forward(uint8_t mSpeed)
{
  digitalWrite(cA, LOW); 
  digitalWrite(cB, HIGH);
  analogWrite(PWM, mSpeed);
}

void Backward(uint8_t mSpeed)
{
  digitalWrite(cA, HIGH);
  digitalWrite(cB, LOW); 
  analogWrite(PWM, mSpeed);
}

void Stop()
{
  digitalWrite(cA, LOW);
  digitalWrite(cB, LOW);  
  analogWrite(PWM, 0);
}


void fixAngle()
{
  if (angleObject > angleHand)
  {
    angleHand++;
    delay(10);
  }
  if (angleObject < angleHand)
  {
    angleHand--;
    delay(10);
  }
}


void loop()
{  
    if(digitalRead(start) == LOW and flag == false)
    {
      Serial.println(1);
      flag = true;
      delay(500);
    }
    
    if(Serial.available())    
    {
      delay(500);
      for (int i = 0; i < Serial.available() + 1; i++)
      {
        data[i] = Serial.read();
        // Serial.println(data[i]);
      }

      graspType = data[0];
      angleObject = data[1];
      while(angleObject != angleHand)
      {
        if (angleObject > angleHand)
        {
          Forward(motorSpeed);
          //delay(100);
        }
        else if (angleObject < angleHand)
        {
          Backward(motorSpeed);
          //delay(100);
        }
      }
      if (angleObject == angleHand)
      {
        Stop();
      }
      flag = false;
    }
}







//    Serial.print("Angle object: ");
//    Serial.print(angleObject);
//    Serial.print("\n\n");
//    Serial.print("Angle hand: ");
//    Serial.print(angleHand);
//    Serial.print("\n\n\n");
//    float a = digitalRead(encoder);
//    Serial.println(a);
