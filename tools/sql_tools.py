#python处理sql的界面

import pymysql
import sys
sys.path.append('..')
from configs.sql_configs import youbike_sql_conf,matadata_sql_conf
from logs.logger import logger
class sqltool:
    def __init__(self,sql_conf):
        self.conf=sql_conf
        self.conn=pymysql.Connection(
            host        =sql_conf.host,
            port        =sql_conf.port,
            user        =sql_conf.user,
            password    =sql_conf.password,
            db          =sql_conf.db,
            charset     =sql_conf.charset,
            autocommit  =False
        )
        logger.info('sql database open')
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn=None
            logger.info('sql database close')
        else:
            logger.warning('close warning')

    def query(self,sql:str):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result=cursor.fetchall()
                cursor.close()
            logger.debug(f'sql query {sql}')
            return result

        except:
            logger.warning(f'sql query warning {sql}')
    def execute(self,sql:str,isAutoCommit:bool=True):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                if isAutoCommit:
                    self.conn.commit()
                cursor.close()
            logger.debug(f'sql execute {sql}')
            return
        except:
            logger.warning(f'sql execute warning {sql}')

    def select_db(self,db:str):
        self.conn.select_db(db)
    def reset_db(self):
        self.conn.select_db(self.conf.db)
    def check_table_exist(self,db_name:str,table_name:str):
        self.select_db(db_name)
        tables=self.query('show tables')
        #self.reset_db()
        return (table_name,) in tables
    def check_table_exist_and_create(self,db_name:str='',table_name:str=''):
        if db_name=='':
            db_name=self.conf.db
        if table_name=='':
            table_name=self.conf.table_name
        if self.check_table_exist(db_name,table_name):
            logger.info(f'{table_name} is already exist in {db_name}')
        try:
            self.select_db(db_name)
            create_table_sql=self.conf.create_sql
            self.execute(create_table_sql)
            logger.info(f'sql create {table_name} from {db_name}')
            return 1
        except:
            logger.warning(f'sql cannot create {table_name} from {db_name}')
    def show_all_value(self,db_name:str='',table_name:str=''):
        if db_name!='':
            self.select_db(db_name)
        if table_name=='':
            table_name=self.conf.table_name
        sql=f'select {self.conf.pKey} from {table_name}'
        return self.query(sql)
    def insert_list(self,sql:str,data_list:list):
        try:
            with self.conn.cursor() as cursor:
                cursor.executemany(sql, data_list)
            self.conn.commit()
            logger.debug(f'sql execute {sql}')
            return
        except:
            logger.warning(f'sql execute warning {sql}')

if __name__=='__main__':
    pass