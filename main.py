from app import app
from apscheduler.schedulers.background import BackgroundScheduler
from hourly import some_job

sched = BackgroundScheduler(daemon=True)
sched.add_job(some_job,'interval',minutes=60)
sched.start()

app.run(host='0.0.0.0', port=8080)