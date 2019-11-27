int led1 = 13; 
void setup(){
  Serial.begin(9600); 
  pinMode(led1, OUTPUT); 
}
void loop(){
  if(Serial.available() > 0)
  {
    int leitura = Serial.read();
    Serial.println(leitura); 
  }
}
