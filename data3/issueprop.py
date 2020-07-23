from kafka import KafkaProducer
from kafka import KafkaConsumer
import time
from datetime import datetime

def producer():
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    counter = 0
    while True:
        producer.send('issue0', key=bytes('{0}/{1}'.format(counter, datetime.now()), 'utf-8'), value= bytes('BDCA1||8||1234567159'.format(counter), 'utf-8'))
        counter += 1
        if counter > 5:
            break
        producer.flush()

producer()
