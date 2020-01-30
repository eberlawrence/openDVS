/*
  Corrigir rotação, perdendo passo. ok
  
  Pensar em como ajustar a angulação da mão. Apenas pra 180 graus. 90 graus para cada lado. ok
  
  Fazer a parte da garra. ok
  
  Colocar dois botões para simular EMG. ok
  
  Refazer o treinamento da rede. 
  
  Terminar o hardware.
  
  Tesar o sistema.
*/


#define encoder        2
#define closeHand      3
#define changeGrasp    4
#define PWM            5
#define cA             7
#define cB             8
#define start          10


int graspType;
int graspTypeAux = 0;
bool flag = false;
int data[5];
short motorSpeed = 200; 
int angleObject;
volatile int angleHand = 0;
 
void setup()                         
{
  pinMode(start, INPUT_PULLUP);
  pinMode(encoder, INPUT);
  pinMode(closeHand, INPUT);
  pinMode(cA, OUTPUT);
  pinMode(cB, OUTPUT);
  pinMode(PWM, OUTPUT);
  pinMode(changeGrasp, OUTPUT);
  
  Serial.begin(115200);

  digitalWrite(changeGrasp, HIGH);
   
  attachInterrupt(digitalPinToInterrupt(2), fixAngle, RISING);
  attachInterrupt(digitalPinToInterrupt(3), openHand, FALLING);  
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
    delay(20);
  }
  if (angleObject < angleHand)
  {
    angleHand--;
    delay(20);
  }
}

void openHand()
{
  if (digitalRead(closeHand) == HIGH)
  {
    digitalWrite(changeGrasp, LOW);
  }
  else
  {
    digitalWrite(changeGrasp, HIGH);
  }
            
}

void rotateMotor()
{
  while(angleObject != angleHand)
  {
    if (angleObject > angleHand)
    {
      Forward(motorSpeed);
    }
    else if (angleObject < angleHand)
    {
      Backward(motorSpeed);
    }
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
    }
    graspType = data[0];
    if (graspType != 1) // if a shape was detected.
    {
      angleObject = data[1] - 12;

      rotateMotor();
      
      if (angleObject == angleHand)
      {
        Stop();
        if (graspType != graspTypeAux)
        {
          graspTypeAux = graspType;
          digitalWrite(changeGrasp, LOW);
          delay(100);
          digitalWrite(changeGrasp, HIGH);
        }
      }
    }
    flag = false;
  }
}
