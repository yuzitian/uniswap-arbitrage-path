from apscheduler.schedulers.blocking import BlockingScheduler
from main import *

def main():
    startCronTask(arbitrage, seconds=15)

if __name__ == '__main__':
    main()
