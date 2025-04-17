import os
import json
import logging
from datetime import datetime
from typing import Dict, Tuple, List
import sys
sys.path.append('..')
from tools.time_tools import time_round
from tools.sql_tools import sqltool
from tools.model import StatusYoubikeModel, SummaryYoubikeModel
from configs.path_configs import raw_json_path
from configs.sql_configs import matadata_sql_conf, status_youbike_sql_conf, summary_youbike_sql_conf

logger = logging.getLogger(__name__)

class Extracter:
    """
    处理 raw JSON 文件和 metadata，返回未处理的新状态数据列表
    """
    def __init__(self, metadata_tool: sqltool):
        self.metadata_tool = metadata_tool
        self.metadata_tool.check_table_exist_and_create()

    def extract_one_json(self, file: str) -> List[dict]:
        full_path = os.path.join(raw_json_path, file)
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 更新 metadata
        try:
            update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            insert_sql = (
                f"INSERT INTO {self.metadata_tool.conf.table_name} "\
                f"VALUES ('{file}', '{update_time}');"
            )
            self.metadata_tool.execute(insert_sql, (file, update_time))
            logger.debug(f"Inserted metadata for {file}")
        except Exception:
            logger.warning(f"Cannot insert {file} into {self.metadata_tool.conf.table_name}")

        # 返回文件内容（支持 list 或 单dict）
        return data if isinstance(data, list) else [data]

    def extract_all_json(self) -> List[dict]:
        # 已处理的文件名
        rows = self.metadata_tool.show_all_value()
        # rows is a tuple of tuples, each row like (fileName,)
        processed = {row[0] for row in rows}

        all_data: List[dict] = []
        for file in os.listdir(raw_json_path):
            if file not in processed:
                try:
                    records = self.extract_one_json(file)
                    all_data.extend(records)
                except Exception as e:
                    logger.warning(f"Error processing file {file}: {e}")
        return all_data
class TransformerAndLoader:
    """
    管理多个 SummaryYoubikeModel，将 StatusYoubikeModel 按站点、星期几、时间段分类汇总，
    并将结果写入数据库。
    """
    def __init__(self,
                 status_tool: sqltool,
                 summary_tool: sqltool):
        # 读取和写入工具
        self.status_tool = status_tool
        self.summary_tool = summary_tool
        # 确保表存在
        self.status_tool.check_table_exist_and_create()
        self.summary_tool.check_table_exist_and_create()
        # 汇总模型字典
        self.summary_model_dict: Dict[Tuple[str, str, str], SummaryYoubikeModel] = {}
        # 批量写入列表
        self.status_model_list: List[StatusYoubikeModel] = []
        self.extract_from_sql()
    def extract_from_sql(self):#从sql读取资料,还没写完
        pass

    def insert(self, data:dict):#将送来的data依照站点和时间存进去不同的summary model
        date_obj = datetime.strptime(data['infoTime'], '%Y-%m-%d %H:%M:%S')
        data['weekday']  = date_obj.strftime('%w') #0=sunday,...
        data['time']     = time_round(date_obj)    #时间
        key = (data['sno'], data['weekday'], data['time'])
        if key not in self.summary_model_dict:
            # 初始化新的 SummaryYoubikeModel，使用当前状态的 total
            summary = SummaryYoubikeModel(
                sno=data['sno'],
                weekday=data['weekday'],
                time=data['time']
            )
            self.summary_model_dict[key] = summary
            logger.debug(f"Created new summary model for key={key}")
        summary_model = self.summary_model_dict[key]
        
        summary_model.insert(data)
        #logger.debug(f"Inserted status into summary model for key={key}")
    def update_all(self):
        """
        对所有 summary 模型执行 update() 汇总计算，并返回所有汇总结果列表。
        """
        summaries = []
        for summary in self.summary_model_dict.values():
            result = summary.update()  # 返回插入前的 datalist
            summaries.extend(result)
        return summaries

    def load_to_sql(self):
        self.status_model_list.extend(self.update_all())
        # 先写状态明细表
        
        data_list=[]
        for status in self.status_model_list:
            data_list.append(status.to_tuple())
        self.status_tool.insert_list(self.status_tool.conf.insert_sql,data_list)
        # 再写汇总表
        data_list=[]
        for summary in self.summary_model_dict.values():
            data_list.append(summary.to_tuple())
        self.summary_tool.insert_list(self.summary_tool.conf.insert_sql,data_list)
        logger.debug("Loaded summary records to SQL")

def etl_routine():
    # 创建 SQL 工具
    metadata_tool = sqltool(matadata_sql_conf)
    status_tool = sqltool(status_youbike_sql_conf)
    summary_tool = sqltool(summary_youbike_sql_conf)
    # 提取器
    extractor = Extracter(metadata_tool)
    data_list = extractor.extract_all_json()
    # 转换 & 加载
    transformer = TransformerAndLoader(status_tool, summary_tool)
    for data in data_list:
        transformer.insert(data)
    transformer.load_to_sql()
if __name__=='__main__':
    etl_routine()

 