import sqlite3
import time
from datetime import datetime
import datetime
from dateutil.parser import parse
import random
n=0
conn = sqlite3.connect('tutorial.db')
c = conn.cursor()

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS parking(num int,unix REAL, datestamp TEXT)")

create_table()

def dynamic_data_entry():
    unix = int(time.time())
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
    num =  int(time.time())

    c.execute("INSERT INTO parking (num,unix, datestamp) VALUES (?, ?, ?)",
          (i+1,'   ','   '))
    

    conn.commit()

print(c)
create_table()
    
for i in range(10):
    dynamic_data_entry()
    
print(c)
