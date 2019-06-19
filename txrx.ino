#define sensorPin 3
#define sensorPin1 2
#define sensorPin2 4
#define sensorPin3 5
#include <Servo.h>
Servo myservo;
Servo myservo1; 


//int t=0;
int data;
int pos=0;

int val = 0;
int val1 = 0;

int val2 = 0;
int val3 = 0;
void setup()
{
   Serial.begin(9600);
   pinMode(3,INPUT);
   pinMode(2,INPUT);
   pinMode(5,INPUT);
   pinMode(4,INPUT);
   pinMode(11,OUTPUT);
   pinMode(10,OUTPUT);
   //pinMode(LED_BUILTIN, OUTPUT);
   myservo.attach(9);
   myservo1.attach(6);   
}
 
void loop()
{
    digitalWrite(10,LOW);
    digitalWrite(11,LOW);
    myservo.write(pos);
    myservo1.write(pos);
    while (Serial.available())
      {
       data = Serial.read();
      }
    val = digitalRead(sensorPin1);
    val1 = digitalRead(sensorPin);
    if((val1==0) && (val==0))
    {
   
    Serial.println(0);
    }
    delay (100);


    
    val2 = digitalRead(sensorPin2);
    val3 = digitalRead(sensorPin3);
    if((val2==0) && (val3==0))
    {
    Serial.println(1);
    }
    delay (100);



  

    if (data == '1')
   {
       for (pos = 0; pos <= 90; pos += 1) 
      { // goes from 0 degrees to 180 degrees
        // in steps of 1 degree
        myservo.write(pos);              // tell servo to go to position in variable 'pos'
        delay(50) ;                    // waits 15ms for the servo to reach the position
      }
      for (pos = 90; pos >= 0; pos -= 1)
      { // goes from 180 degrees to 0 degrees
       myservo.write(pos);              // tell servo to go to position in variable 'pos'
       delay(15);                       // waits 15ms for the servo to reach the position
      } 
     data=0;
   }










    if (data == '0')
   {
       for (pos = 0; pos <= 90; pos += 1) 
      { // goes from 0 degrees to 180 degrees
        // in steps of 1 degree
        myservo1.write(pos);              // tell servo to go to position in variable 'pos'
        delay(50);                      // waits 15ms for the servo to reach the position
      }
      for (pos = 90; pos >= 0; pos -= 1)
      { // goes from 180 degrees to 0 degrees
       myservo1.write(pos);              // tell servo to go to position in variable 'pos'
       delay(15);                       // waits 15ms for the servo to reach the position
      } 
     data=0;
   }


   if (data == 'l')
   {
    digitalWrite(10,LOW);
    digitalWrite(11,HIGH);
    delay(6000);
    data = 's';

   }
   if (data == 'r')
   {
    digitalWrite(11,LOW);
    digitalWrite(10,HIGH);
    delay(6000);
    data = 's';
    
   }
}
