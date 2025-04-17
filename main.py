from configs.url_configs import youbike_url,weather_url
from tools.crawler_tools import crawler
from etl.extract import etl_routine
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from logs.logger import logger
def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(
        crawler,
        'interval',
        minutes=15,
        args=[youbike_url],
        next_run_time=datetime.now()  # 立即执行第一次
    )
    '''
    scheduler.add_job(
        etl_routine,
        'interval',
        hours=1,
        next_run_time=datetime.now()  # 立即执行第一次
    )
    '''
    logger.info('scheduler start')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.warning('scheduler sutdown')

if __name__=='__main__':
    main()