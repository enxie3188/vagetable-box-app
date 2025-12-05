原鄉蔬菜箱數位平台 (Indigenous Vegetable Box Platform)

這是一個專為原鄉部落設計的智慧蔬菜箱供應鏈管理系統。透過數位化平台串聯農民生產端與客戶消費端，實現從「種植規劃」到「出貨配送」的全流程管理。

專案特色

本系統解決了蔬菜箱配送中常見的供需不平衡與物流繁瑣問題：

全自動媒合 (Global Matching)：系統根據庫存狀況與訂閱合約，自動跨部落調度蔬菜，生成最佳配貨單。

智慧種植管理：農民透過「轉盤抽籤」領取種苗，系統自動推算採收日，確保產能穩定。

數位出貨單 (QR Code)：支援批量列印出貨單，每張單據皆附有專屬 QR Code，客戶掃描即可回填「下一次預計收貨日」，數據直接同步回資料庫。

可視化戰情室：即時監控各部落天氣、庫存水位與未來產能預測。

功能模組

1. 農民種植端

種苗領取（轉盤互動介面）

個人種植紀錄與預計採收日追蹤

2. 戰情總覽 (Dashboard)

各據點即時天氣資訊

未來 4 週供需預測分析圖表

即時庫存水位與作物類別佔比

3. 訂單與媒合 (OMS)

訂戶管理：支援單次、月配、雙週配等多種合約模式。

自動配貨：一鍵啟動全域配貨演算法，自動扣除庫存並產生訂單明細。

出貨單系統：

支援批量選取與下載出貨單 (HTML/PDF)。

內建客戶專屬 QR Code 連結。

4. 系統設定

農民與作物資料庫管理

苗種進貨盤數設定

本機安裝與執行

前置需求

Python 3.8 或以上版本

1. 下載專案並安裝依賴套件

請確保目錄下有 requirements.txt 檔案。

pip install -r requirements.txt


2. 啟動系統

streamlit run vegetable_platform.py


3. 初始化資料庫

首次執行時，系統會自動連接 SQLite。請在網頁左側側邊欄點擊 「修復資料庫 (Init DB)」，系統將建立資料表結構並寫入範例測試數據。

部署 (Streamlit Cloud)

本專案已優化，可直接免費部署於 Streamlit Community Cloud：

將此專案上傳至 GitHub (包含 vegetable_platform.py 與 requirements.txt)。

登入 Streamlit Cloud 並連結您的 GitHub Repository。

設定主程式路徑為 vegetable_platform.py。

點擊 Deploy 即可上線供多人使用。

檔案結構說明

vegetable_platform.py: 核心主程式 (包含前端 UI 與後端邏輯)。

requirements.txt: 專案所需的 Python 套件清單。


Created with Python & Streamlit
