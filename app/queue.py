import redis
from rq import Queue

redis_conn = redis.Redis(host="localhost", port=6379, db=0)
invoice_queue = Queue("invoice_queue", connection=redis_conn)
