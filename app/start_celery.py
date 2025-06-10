import subprocess
import sys
import os

def run_command(command):
    subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    print("Starting Celery worker...")
    run_command("celery -A app.core.celery_worker.celery_app worker --loglevel=info")
