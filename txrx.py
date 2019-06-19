import time
import serial
ser = serial.Serial('/dev/ttyACM0', 9600)
print("hey")
while True:
 print("hey")   
 val= ser.readline().decode("ascii")
 val=int(val)
 print("hey1")
 print(val)
 if val==0:
     print("car at entrence");
     ser.write(str.encode('1')) #send 1
     print ("servo turned ON at entrance ")
     time.sleep(1)
 time.sleep(0.1)


 if val==1:
     print("car at exit");
     ser.write(str.encode('0') )#send 1
     print ("servo turned ON at exit ")
     time.sleep(1)
 time.sleep(0.1)
