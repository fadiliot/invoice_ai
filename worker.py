from rq import SimpleWorker
from app.queue import redis_conn

worker = SimpleWorker(["invoice_queue"], connection=redis_conn)
worker.work()
