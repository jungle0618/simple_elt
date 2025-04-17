class youbike_sql_conf:
    host:       str='127.0.0.1'
    port:       int=3306
    user:       str='root'
    password:   str= ''
    db:         str='etl_program_db'
    charset:    str='utf8'
    pKey:       str='pKey'
    table_name: str='stations'
    create_sql: str="""
    CREATE TABLE IF NOT EXISTS stations (
        sno VARCHAR(20) NOT NULL COMMENT '站点编号',
        sna VARCHAR(100) NOT NULL COMMENT '中文站名',
        sarea VARCHAR(50) COMMENT '行政区',
        mday DATETIME COMMENT '资料更新日期时间',
        
        -- 地址信息
        ar VARCHAR(200) COMMENT '中文地址',
        sareaen VARCHAR(100) COMMENT '英文行政区',
        snaen VARCHAR(100) COMMENT '英文站名',
        aren VARCHAR(200) COMMENT '英文地址',
        
        -- 状态信息
        act TINYINT DEFAULT 1 COMMENT '站点状态 (1-启用, 0-禁用)',
        
        -- 时间信息
        srcUpdateTime DATETIME COMMENT '来源更新时间',
        updateTime DATETIME COMMENT '资料更新时间',
        infoTime TIME COMMENT '信息时间',
        infoDate DATE COMMENT '信息日期',
        
        -- 车辆数量
        total INT DEFAULT 0 COMMENT '总停车格数',
        available_rent_bikes INT DEFAULT 0 COMMENT '可租车辆',
        available_return_bikes INT DEFAULT 0 COMMENT '可还车位',
        
        -- 地理坐标
        latitude DECIMAL(10, 6) COMMENT '纬度',
        longitude DECIMAL(10, 6) COMMENT '经度',
    )CHARSET=utf8 COMMENT='共享单车站点信息表';
    """
    
class status_youbike_sql_conf:#比上个多一些有用的资讯
    host:       str='127.0.0.1'
    port:       int=3306
    user:       str='root'
    password:   str= ''
    db:         str='etl_program_db'
    charset:    str='utf8'
    pKey:       str='pKey'
    table_name: str='station_status_snapshot'
    create_sql = create_sql = """
    CREATE TABLE IF NOT EXISTS station_status_snapshot (
        sno VARCHAR(20) NOT NULL COMMENT '站点编号',
        weekday TINYINT NOT NULL COMMENT '星期几 (0=星期日)',
        `time` TIME NOT NULL COMMENT '时间段 (四舍五入的15分钟单位)',

        -- 统计信息
        total DECIMAL(8,2) DEFAULT 0 COMMENT '平均总停车格数',
        available_rent_bikes DECIMAL(8,2) COMMENT '平均可租车辆数',
        available_return_bikes DECIMAL(8,2) COMMENT '平均可还车位数',
        lock_bikes DECIMAL(8,2) COMMENT '平均锁车数量',
        available_rate DECIMAL(5,4) COMMENT '平均可租比例',
        lock_rate DECIMAL(5,4) COMMENT '平均锁车比例',

        infoDate DATE NOT NULL COMMENT '信息日期',
        infoTime TIME NOT NULL COMMENT '信息时间',
        sna VARCHAR(100) COMMENT '中文站名',
        sarea VARCHAR(50) COMMENT '行政区',
        ar VARCHAR(200) COMMENT '中文地址',

        -- 状态信息
        act TINYINT DEFAULT 1 COMMENT '站点状态 (1-启用, 0-禁用)'

    ) CHARSET=utf8 COMMENT='共享单车每15分钟状态快照表';
    """
    insert_sql=insert_sql = """
    INSERT INTO station_status_snapshot (
        sno, weekday, `time`,
        total, available_rent_bikes, available_return_bikes,
        lock_bikes, available_rate, lock_rate,
        infoDate, infoTime, sna, sarea, ar, act
    ) VALUES (
        %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s, %s, %s, %s
    )
    """
class summary_youbike_sql_conf:#统计过后的资料
    host:       str='127.0.0.1'
    port:       int=3306
    user:       str='root'
    password:   str= ''
    db:         str='etl_program_db'
    charset:    str='utf8'
    pKey:       str='sno'
    table_name: str='station_time_summary'
    create_sql = """
    CREATE TABLE IF NOT EXISTS station_time_summary (
        sno VARCHAR(20) NOT NULL COMMENT '站点编号',
        weekday TINYINT NOT NULL COMMENT '星期几 (0=星期日)',
        `time` TIME NOT NULL COMMENT '时间段 (四舍五入的15分钟单位)',

        -- 统计信息
        total DECIMAL(8,2) DEFAULT 0 COMMENT '平均总停车格数',
        available_rent_bikes DECIMAL(8,2) COMMENT '平均可租车辆数',
        available_return_bikes DECIMAL(8,2) COMMENT '平均可还车位数',
        lock_bikes DECIMAL(8,2) COMMENT '平均锁车数量',
        available_rate DECIMAL(5,4) COMMENT '平均可租比例',
        lock_rate DECIMAL(5,4) COMMENT '平均锁车比例',
        sample_size INT DEFAULT 0 COMMENT '样本数量',

        -- 组合主键
        PRIMARY KEY (sno, weekday, time),

        -- 索引优化
        INDEX idx_time_slot (time),
        INDEX idx_weekday (weekday),
        INDEX idx_station_weekday (sno, weekday)
    ) CHARSET=utf8 COMMENT='Ubike 每站每时间段汇总统计';
    """
    insert_sql=f"""
    INSERT INTO station_time_summary (
    sno, weekday, time, total,
    available_rent_bikes, available_return_bikes, lock_bikes,
    available_rate, lock_rate, sample_size
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
class matadata_sql_conf:#储存有哪些raw 档案被写进去
    host:       str='127.0.0.1'
    port:       int=3306
    user:       str='root'
    password:   str= ''
    db:         str='etl_program_db'
    charset:    str='utf8'
    pKey:       str='fileName'
    table_name='matadata'
    create_sql: str="""
    CREATE TABLE IF NOT EXISTS matadata (
        fileName varchar(100) primary key comment '档案名称',
        updateTime datetime not null comment '资料更新时间'
    )charset=utf8 comment='共享单车站点信息表';
    """

