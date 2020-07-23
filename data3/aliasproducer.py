from kafka import KafkaProducer
from kafka import KafkaConsumer
import time
from datetime import datetime

def producer():
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    counter = 0
    while True:
        producer.send('alias3', key=bytes('{0}/{1}'.format(counter, datetime.now()), 'utf-8'), value= bytes('jg0015{0}||123456715{0}'.format(counter), 'utf-8'))
        counter += 1
        if counter > 10:
            break
        producer.flush()

producer()
