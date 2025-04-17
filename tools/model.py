#models of each data
import json
from datetime import datetime
import sys
import os
sys.path.append('..')
from logs.logger import logger
from tools.time_tools import time_round
from tools.sql_tools import sqltool
class UbikeStationsModel:#list of Single station data in a fix time
    def __init__(self, data:str):
        data_dict=json.loads(data)
        self.data_list=[]
        for data in data_dict:
            self.data_list.append(SingleStationModel(data))
    def to_json(self,sep=','):
        stations_data = []
        for station in self.data_list:
            stations_data.append(station.to_dict())
            # 转换为JSON字符串
        return json.dumps(stations_data, ensure_ascii=False)
    def to_csv(self,sep=','):
        csv_line=''
        for data in self.data_list:
            csv_line+=data.to_csv()
            csv_line+='\n'
        return csv_line
    def filter(self):#清除不需要的资讯
        pass
    def save(self,path:str,file_type:str):
        if file_type=='csv':
            data=self.to_csv()
        elif file_type=='json':
            data=self.to_json()
        else:
            logger.warning(f'save type error')
            return
        file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "." + file_type
        try:
            with open(os.path.join(path,file_name),'w',encoding='utf-8') as f:
                f.write(data)
            logger.info(f'create {file_name} to {path}')
        except:
            logger.error(f'cannot create {file_name} to {path}')
class SingleStationModel:
    def __init__(self,data):
        self.sno = str(data['sno'])  # 站点编号
        self.sna = data['sna']       # 中文站名
        self.sarea = data['sarea']   # 行政区
        self.mday = data['mday']     # 资料更新日期时间
        self.ar = data['ar']         # 中文地址
        self.sareaen = data['sareaen']  # 英文行政区
        self.snaen = data['snaen']   # 英文站名
        self.aren = data['aren']     # 英文地址
        self.act = int(data['act'])  # 站点状态 （0表示没有车子)
        self.srcUpdateTime = data['srcUpdateTime']  # 来源更新时间
        self.updateTime = data['updateTime']        # 资料更新时间
        self.infoTime = data['infoTime']            # 信息时间
        self.infoDate = data['infoDate']            # 信息日期
        self.total = int(data['total'])                      # 总停车格数
        self.available_rent_bikes = int(data['available_rent_bikes'])  # 可租车辆
        self.available_return_bikes = int(data['available_return_bikes'])  # 可还车位
        self.latitude = float(data['latitude'])    # 纬度
        self.longitude = float(data['longitude'])  # 经度
    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
    def to_csv(self,sep=','):
        csv_line = \
            f"{self.sno}{sep}" \
            f"{self.sna}{sep}" \
            f"{self.sarea}{sep}" \
            f"{self.mday}{sep}" \
            f"{self.ar}{sep}" \
            f"{self.sareaen}{sep}" \
            f"{self.snaen}{sep}" \
            f"{self.aren}{sep}" \
            f"{self.act}{sep}" \
            f"{self.srcUpdateTime}{sep}" \
            f"{self.updateTime}{sep}" \
            f"{self.infoTime}{sep}" \
            f"{self.infoDate}{sep}" \
            f"{self.total}{sep}" \
            f"{self.available_rent_bikes}{sep}" \
            f"{self.latitude}{sep}" \
            f"{self.longitude}{sep}" \
            f"{self.available_return_bikes}"
        return csv_line
    def to_dict(self):
        return {
            'sno': self.sno,
            'sna': self.sna,
            'sarea': self.sarea,
            'mday': self.mday,
            'ar': self.ar,
            'sareaen': self.sareaen,
            'snaen': self.snaen,
            'aren': self.aren,
            'act': self.act,
            'srcUpdateTime': self.srcUpdateTime,
            'updateTime': self.updateTime,
            'infoTime': self.infoTime,
            'infoDate': self.infoDate,
            'total': self.total,
            'available_rent_bikes': self.available_rent_bikes,
            'available_return_bikes': self.available_return_bikes,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
class SummaryYoubikeModel:#统计每个ubike站在每个小时时间平均的车位数量
    def __init__(self,sno,weekday,time):
        self.sno=sno#ubike station id
        self.weekday=weekday#0=sunday...
        self.time=time
        self.total = 0
        #bike number data
        self.available_rent_bikes = 0 # 可租车辆
        self.available_return_bikes = 0  # 可还车位
        self.available_rate = None
        self.lock_bikes= None
        self.lock_rate= None
        self.datalist=[]#list of status model
        self.sample_size=0#被统计的sample数量,没被统计的不会加进去
    def to_json(self,sep=','):
        return json.dumps(self.to_dict(), ensure_ascii=False)
    def to_csv(self,sep=','):
        csv_line = \
            f"{self.sno}{sep}" \
            f"{self.weekday}{sep}" \
            f"{self.time}{sep}" \
            f"{self.total}{sep}" \
            f"{self.available_rent_bikes}{sep}" \
            f"{self.available_rate}{sep}"\
            f"{self.available_return_bikes}{sep}"\
            f"{self.lock_bikes}{sep}"\
            f"{self.lock_rate}{sep}"\
            f"{self.sample_size}"
        return csv_line
    def to_dict(self):
        return {
            'sno'                   : self.sno,
            'weekday'               : self.weekday,
            'time'                  : self.time,
            'total'                 : self.total,
            'available_rent_bikes'  : self.available_rent_bikes,
            'available_return_bikes': self.available_return_bikes,
            'available_rate'        : self.available_rate,
            'lock_bikes'            : self.lock_bikes,
            'lock_rate'             : self.lock_rate,
            'sample_size'           : self.sample_size,
        }
    def insert(self,data:dict):#insert a data to datalist
        if self.sno!=data['sno']:
            logger.error('insert to wrong model')
        self.datalist.append(StatusYoubikeModel(data))
    def update(self):#update information of bike number, and return datalist
        if len(self.datalist)==0:
            return
        total_total=(self.total)*(self.sample_size)
        total_available_rent_bikes=(self.available_rent_bikes)*(self.sample_size)
        total_available_return_bikes=(self.available_return_bikes)*(self.sample_size)
        for data in self.datalist:
            total_total                 +=data.total
            total_available_rent_bikes  +=data.available_rent_bikes
            total_available_return_bikes+=data.available_return_bikes
            self.sample_size            +=1
        self.total                  =total_total/self.sample_size
        self.available_rent_bikes   =total_available_rent_bikes/self.sample_size
        self.available_return_bikes =total_available_return_bikes/self.sample_size
        self.available_rate         =self.available_rent_bikes/self.total
        self.lock_bikes             =self.total-self.available_rent_bikes-self.available_return_bikes
        self.lock_rate              =self.lock_bikes/self.total
        #清空datalist
        ret=self.datalist.copy()
        self.datalist.clear()
        return ret
    def to_sql(self,tool:sqltool):
        insert_sql=f"insert into {tool.conf.table_name} values("\
        f"'{self.sno}',"\
        f"{self.weekday},"\
        f"'{self.time}',"\
        f"{self.total},"\
        f"{self.available_rent_bikes},"\
        f"{self.available_return_bikes},"\
        f"{self.lock_bikes},"\
        f"{self.available_rate}," \
        f"{self.lock_rate},"\
        f"{self.sample_size});"
        #tool.execute(insert_sql)
        #logger.debug(f'insert into {tool.conf.table_name}')
        return insert_sql
    def to_tuple(self):
        return (
            self.sno,
            self.weekday,
            self.time,
            self.total,
            self.available_rent_bikes,
            self.available_return_bikes,
            self.lock_bikes,
            self.available_rate,
            self.lock_rate,
            self.sample_size
        )
class StatusYoubikeModel:#经过处理的单比数据
    def __init__(self,data:dict):
        self.sno = str(data['sno'])  
        self.sna = data['sna']       # 站名
        self.sarea = data['sarea']   # 行政区
        self.ar = data['ar']         # 地址
        self.act = int(data['act'])  # 0表示站位没有车
        self.infoTime = data['infoTime']            # 时间
        self.infoDate = data['infoDate']            # 日期
        self.weekday  = data['weekday']             # 星期几(1=星期天)
        self.time     = data['time']                # 时间(h:m:s)
        # 车辆数量
        self.total = int(data['total'])                      #总车格
        self.available_rent_bikes = int(data['available_rent_bikes'])  #可租的车未数
        self.available_return_bikes = int(data['available_return_bikes'])  # 可还车位数
        self.available_rate = self.available_rent_bikes/self.total #车位可用的比例
        self.lock_bikes=self.total-self.available_rent_bikes-self.available_return_bikes #不能使用的车位数量，很热门的地方ubike工作人员会把ubike挤在一起挪出空间
        self.lock_rate=self.lock_bikes/self.total
        self.latitude = float(data['latitude'])
        self.longitude = float(data['longitude'])
    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
    def to_csv(self,sep=','):
        csv_line = \
            f"{self.sno}{sep}" \
            f"{self.sna}{sep}" \
            f"{self.sarea}{sep}" \
            f"{self.ar}{sep}" \
            f"{self.act}{sep}" \
            f"{self.infoTime}{sep}" \
            f"{self.infoDate}{sep}" \
            f"{self.weekday}{sep}" \
            f"{self.time}{sep}" \
            f"{self.total}{sep}" \
            f"{self.available_rent_bikes}{sep}" \
            f"{self.available_return_bikes}{sep}" \
            f"{self.available_rate}{sep}"\
            f"{self.lock_bikes}{sep}"\
            f"{self.lock_rate}{sep}"\
            f"{self.latitude}{sep}" \
            f"{self.longitude}" \
            
        return csv_line
    def to_dict(self):
        return {
            'sno'                   : self.sno,
            'sna'                   : self.sna,
            'sarea'                 : self.sarea,
            'ar'                    : self.ar,
            'act'                   : self.act,
            'infoTime'              : self.infoTime,
            'infoDate'              : self.infoDate,
            'weekday'               : self.weekday,
            'time'                  : self.time,
            'total'                 : self.total,
            'available_rent_bikes'  : self.available_rent_bikes,
            'available_return_bikes': self.available_return_bikes,
            'available_rate'        : self.available_rate,
            'lock_bikes'            : self.lock_bikes,
            'lock_rate'             : self.lock_rate,
            'latitude'              : self.latitude,
            'longitude'             : self.longitude,
        }
    def to_sql(self,tool:sqltool):
        insert_sql=f"insert into {tool.conf.table_name} values("\
        f"'{self.sno}',"\
        f"{self.weekday},"\
        f"'{self.time}',"\
        f"{self.total},"\
        f"{self.available_rent_bikes},"\
        f"{self.available_return_bikes},"\
        f"{self.lock_bikes},"\
        f"{self.available_rate}," \
        f"{self.lock_rate},"\
        f"'{self.infoDate}',"\
        f"'{self.infoTime}',"\
        f"'{self.sna}',"\
        f"'{self.sarea}',"\
        f"'{self.ar}',"\
        f"{self.act});"
    def to_tuple(self):
        return (
            self.sno,
            self.weekday,
            self.time,
            self.total,
            self.available_rent_bikes,
            self.available_return_bikes,
            self.lock_bikes,
            self.available_rate,
            self.lock_rate,
            self.infoDate,
            self.infoTime,
            self.sna,
            self.sarea,
            self.ar,
            self.act
        )
        '''tool.execute(insert_sql)
        logger.debug(f'insert into {tool.conf.table_name}')
        '''
        return insert_sql


if __name__=='__main__':
    pass