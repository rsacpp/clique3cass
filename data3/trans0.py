from kafka import KafkaProducer
from kafka import KafkaConsumer
import time
from datetime import datetime

def producer():
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    counter = 0
    while True:
        producer.send('transfer0', key=bytes('{0}/{1}'.format(counter, datetime.now()), 'utf-8'), value= bytes('jg00159&&BDCA1||22b97f6a||8->jg008&&d0eb164674df5de1&&0001&&1234567159'.format(counter), 'utf-8'))
        counter += 1
        if counter > 0:
            break
        producer.flush()

producer()
