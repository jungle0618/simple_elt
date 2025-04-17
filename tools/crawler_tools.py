''''
每隔一小时
抓取 YouBike2.0臺北市公共自行車即時資訊 https://data.gov.tw/dataset/137993
和 天氣預報的歷史資料 https://data.gov.tw/dataset/9221
到csv资料夹
'''
#移动到etl_program,不然import path会烂
import sys
sys.path.append('..')

import json
import csv
from datetime import datetime
import pandas as pd
import urllib.request as req
from tools.model import SingleStationModel,UbikeStationsModel
from logs.logger import logger
from configs.path_configs import raw_csv_path,raw_json_path
import os
def crawler(url:str):
    request = req.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    })
    with req.urlopen(request) as response:
        data = response.read().decode('utf-8')
    ubike_model=UbikeStationsModel(data)
    ubike_model.save(raw_csv_path,'csv')
    ubike_model.save(raw_json_path,'json')
    logger.info('crawler a file and save')
#自动抓取

if __name__ == '__main__':
    pass
    
