# Light-Dance-Firmware

pico W 管理與狀態監控系統

## 簡介
本專案包含兩部分：
1. 基於 pico W 的硬體設備管理與狀態監控系統。
2. 基於 Python 的主控端程式，用於管理多個 pico W 設備的通信與指令控制。

該系統使用 WiFi 和 UDP 通信協議，實現設備的連線狀態監控、指令傳輸（如啟動、停止）、以及心跳信號檢測。

---

## 系統架構

### Arduino 部分
1. 通過 HTTP 和 UDP 與伺服器進行通信。
2. 支援接收 "start", "stop", "heartbeat" 等指令。
3. 透過 LittleFS 進行數據存儲。

### Python 部分
1. 發送廣播訊息到所有設備。
2. 接收設備回傳的狀態資訊。
3. 支援指令輸入（start, stop, exit）。
4. 動態顯示設備狀態。

---

## 安裝與配置

### Arduino 部分
1. 硬體需求：
   - pico W
2. 軟體需求：
   - 安裝 [Arduino IDE](https://www.arduino.cc/en/software)。
   - 安裝以下庫：
     - `WiFi.h`
     - `HTTPClient.h`
     - `WiFiUdp.h`
     - `LittleFS.h`
     - `ArduinoJson.h`
3. 設定：
   - 修改以下變數，根據您的網路環境調整：
     - `ssid`：WiFi 名稱。
     - `password`：WiFi 密碼。
     - `responseAddress`：Python 廣播端的 IP 地址。
     - `localPort` 和 `responsePort`：用於通信的埠。
4. 燒錄代碼到 Arduino 開發板。

### Python 部分
1. 硬體需求：
   - 電腦。
2. 軟體需求：
   - Python 版本 >= 3.6。
   - 安裝以下依賴庫：
     - `socket`
     - `time`
     - `threading`
     - `curses`
3. 配置：
   - 修改 `broadcast_address` 和 `port` 變數，根據網段進行調整。

---

## 使用方式

### 啟動 Arduino 程式
1. 燒錄程式後，開發板會自動連接到 WiFi。
2. Arduino 程式將監聽指定的 UDP 埠號，並等待廣播指令。

### 啟動 Python 主控程式
1. 執行 Python 程式。
2. 使用指令控制設備：
   - 輸入 `start`：向所有設備發送啟動指令。
   - 輸入 `stop`：向所有設備發送停止指令。
   - 輸入 `exit`：結束程式。
3. 程式將動態顯示設備的狀態，包括：
   - 設備 ID
   - IP 地址
   - 任務狀態
   - 最近回應時間

---

## 功能與特性

### Arduino 程式
1. **HTTP 通信**：支持 GET 和 POST 請求，可用網址控制 pico W。
2. **UDP 通信**：接收並處理廣播指令。
3. **設備狀態保存**：使用 LittleFS 保存資料。

### Python 程式
1. **廣播訊息**：發送啟動、停止和心跳指令。
2. **設備監控**：接收並解析設備的回應訊息。
3. **用戶界面**：動態顯示設備狀態，並接受指令輸入。

---

## 注意事項
1. 確保設備與 Python 程式處於同一網段。
2. 廣播地址和埠號需根據您的網絡環境調整。
3. 心跳訊號間隔和設備回應超時時間可根據需求調整。
4. 若無法正常工作，檢查防火牆設置是否阻擋了 UDP 通信。



