/*
  Corrigir rotação, perdendo passo. ok
  
  Pensar em como ajustar a angulação da mão. Apenas pra 180 graus. 90 graus para cada lado. ok
  
  Fazer a parte da garra. ok
  
  Colocar dois botões para simular EMG. ok
  
  Refazer o treinamento da rede. 
  
  Terminar o hardware.
  
  Tesar o sistema.
*/


#define encoder        2    // Receive the encoder values. Interrupt used.
#define changeGrasp    4    // Send a HIGH level to change the grasp type and open the hand.

#define PWM            5    // Send a PWM for the H-Bridge.
#define cA             7    // Channel A of the H-Bridge.
#define cB             8    // Channel B of the H-Bridge.

#define bt_close       3    // Receive the button status used for closing the hand. Interrupt used.
#define bt_start       10   // Button to start the acquisition.

#define grasp_tripod   11
#define grasp_power    12


int graspType;                  // Store the grasp type as "int". 
int graspTypeAux = 0;           // Store the last grasp type selected.
bool flag = false;              // Flag to avoid the repetition of the first condition.
int data[2];                    // Store received data obteined from Python through serial port. 
short motorSpeed = 40;         // Set the engine speed of rotation
int objectAngle;                // Store the object angle.
volatile int WristAngle = 0;    // Adjust the wrist angle according to the object angle.
 
void setup()                         
{
  pinMode(encoder, INPUT);
  pinMode(changeGrasp, OUTPUT);
  
  pinMode(PWM, OUTPUT);
  pinMode(cA, OUTPUT);
  pinMode(cB, OUTPUT);
  
  pinMode(bt_close, INPUT_PULLUP);
  pinMode(bt_start, INPUT_PULLUP);

  pinMode(grasp_tripod, OUTPUT);
  pinMode(grasp_power, OUTPUT);
  
  Serial.begin(115200);

  digitalWrite(changeGrasp, HIGH);    // Starts HIGH to keep the hand open.
   
  attachInterrupt(digitalPinToInterrupt(2), fixAngle, CHANGE);    // Interrupt for the encoder.
  attachInterrupt(digitalPinToInterrupt(3), openHand, CHANGE);   // Interrupt for the hand closing.
}



/* FUNCTIONS */


// Rotate the wrist forward.
void Forward(uint8_t mSpeed)
{
  digitalWrite(cA, LOW); 
  digitalWrite(cB, HIGH);
  analogWrite(PWM, mSpeed);
}


// Rotate the wrist backward.
void Backward(uint8_t mSpeed)
{
  digitalWrite(cA, HIGH);
  digitalWrite(cB, LOW); 
  analogWrite(PWM, mSpeed);
}


// Stop the rotation.
void Stop()
{
  digitalWrite(cA, LOW);
  digitalWrite(cB, LOW);  
  analogWrite(PWM, 0);
}


// Used on the first interrupt. Fix the angle wrist according to the object angle, incrementing or decrementing it.
void fixAngle()
{
  if (objectAngle > WristAngle)
  {
    WristAngle++;
  }
  if (objectAngle < WristAngle)
  {
    WristAngle--;
  }
}


// Used on the second interrupt. It's possible close the hand any time.
void openHand()
{ 
  if (digitalRead(bt_close) == HIGH)
  {
    digitalWrite(changeGrasp, LOW);
  }
  else
  {
    digitalWrite(changeGrasp, HIGH);
  }
            
}


// Rotate the engine if there is a mismatch between the angles.
void rotateMotor()
{
  while(objectAngle != WristAngle)
  {
    if (objectAngle > WristAngle)
    {
      Forward(motorSpeed);
    }
    else if (objectAngle < WristAngle)
    {
      Backward(motorSpeed);
    }
  }
}


void loop()
{
  
  if(digitalRead(bt_start) == LOW and flag == false) // Initial condition. Press the button:
  {
    Serial.println(1); // Write "1", then the acquisition in Python starts.
    flag = true;
    delay(500);
  }
  if(Serial.available())    // Wait for data.
  {
    delay(500);
    for (int i = 0; i < Serial.available() + 1; i++)
    {
      data[i] = Serial.read();    // Store received data, that is both grasp type and object angle.
    }
    graspType = data[0];
    if (graspType != 1)     // if a shape was detected.
    {
      if (graspType == 0){
        digitalWrite(grasp_tripod, HIGH);
        digitalWrite(grasp_power, LOW);
      }
      if (graspType == 2){
        digitalWrite(grasp_power, HIGH);
        digitalWrite(grasp_tripod, LOW);
      }
      objectAngle = data[1] - 45;   // Subtract the offset inserted in python script.
      rotateMotor();    // Start to rotate the motor if the angles are different.
      
      if (objectAngle == WristAngle)
      {
        Stop();   // if the angles are the same the rotation stops.
        if (graspType != graspTypeAux)    // Change the grasp, if the grasp type received and the last grasp type are different.
        {
          graspTypeAux = graspType;
          digitalWrite(changeGrasp, LOW);
          delay(100);
          digitalWrite(changeGrasp, HIGH);
        }
      }
    }
    
    flag = false; // Reset the system.
  }
}
