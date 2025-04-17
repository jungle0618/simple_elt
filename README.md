# 台北 YouBike ETL

一個用兩天時間完成的 ETL 練習，抓取台北市 YouBike 站點的即時資料，並將資料存入本地 SQL 資料庫。

## 資料來源
- 政府資料開放平台：https://data.gov.tw/dataset/9221

## 前置需求
- 已安裝並運行 MySQL
- 安裝所需 Python 套件：

## 設定
1. 更新 `configs/sql_configs.py` 中的資料庫設定。
2. 更新 `configs/path_configs.py` 中的檔案路徑設定。
3. 在 MySQL 中建立目標資料庫：
   ```sql
   CREATE DATABASE etl_program_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

## 執行 ETL
- 啟動定時 ETL（每 15 分鐘抓取一次資料）：
  ```bash
  python3 main.py
  ```
- 手動執行擷取器：
  ```bash
  python3 etl/extracter.py
  ```

## 已知問題
- 尚未實作：及時從 SQL 中讀取資料並載入模型。
