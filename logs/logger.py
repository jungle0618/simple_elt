import logging
import os
from configs.path_configs import logs_path
logger=logging.getLogger()
file_handler = logging.FileHandler(
    filename=os.path.join(logs_path, 'app.log'),
    mode='a',  # 追加模式
    encoding='utf-8'
)
format=logging.Formatter('%(asctime)s %(filename)s %(levelname)s:%(message)s')
file_handler.setFormatter(format)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)