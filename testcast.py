import socket
import time
import threading
import curses  # 用於終端動態刷新
import sys  # 用於退出程式

# 配置廣播和接收訊息的埠
broadcast_address = "192.168.0.255"  # 根據你的網段調整
port = 12345  # 廣播埠
response_port = 12346  # 接收回傳訊息的埠

# 紀錄板子的狀態
devices = {}
exit_event = threading.Event()  # 新增結束程式的事件
stop_event = threading.Event()  # 用於控制停止功能的事件

# 定義每塊板子的狀態
class DeviceState:
    def __init__(self, ip, device_id):
        self.ip = ip
        self.device_id = device_id
        self.last_response_time = None
        self.status = "Disconnected"  # 初始狀態為未連線
        self.task_status = "Waiting"  # 初始任務狀態為等待中

# 獲取本機 IP 地址
def get_local_ip():
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_sock.connect(("8.8.8.8", 80))
    local_ip = temp_sock.getsockname()[0]
    temp_sock.close()
    return local_ip

local_ip = get_local_ip()

# 創建 UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("", response_port))  # 綁定埠用於接收回傳訊息

# 發送廣播訊息
def broadcast_message(message):
    sock.sendto(message.encode(), (broadcast_address, port))
    if message != "heartbeat":
        print(f"Broadcasted message: {message}")

# 定期發送心跳訊號
def heartbeat_function():
    while not exit_event.is_set():
        broadcast_message("heartbeat")
        time.sleep(0.1)  # 每 5 秒發送一次心跳訊號

# 發送停止訊號，直到所有設備回應
def stop_function():
    while stop_event.is_set():
        broadcast_message("stop")
        time.sleep(0.001)  # 每 1 秒發送一次停止訊號

        # 檢查是否所有設備都已回應 "stopped"
        all_stopped = True
        for device in devices.values():
            if device.task_status != "stopped":
                all_stopped = False
                break

        # 如果所有設備已停止，結束廣播
        if all_stopped:
            print("All devices have stopped.")
            stop_event.clear()

# 接收板子回傳訊息的函數
def listen_for_responses():
    while not exit_event.is_set():
        try:
            data, addr = sock.recvfrom(1024)  # 接收回傳訊息
            message = data.decode()
            device_ip = addr[0]

            # 假設回應格式為 "deviceId: 回應內容"
            if ":" in message:
                device_id, task_status = map(str.strip, message.split(":", 1))
            else:
                device_id, task_status = "Unknown", message

            # 更新板子狀態
            if device_ip not in devices:
                devices[device_ip] = DeviceState(device_ip, device_id)
            devices[device_ip].last_response_time = time.time()
            devices[device_ip].status = (
                "Running" if task_status == "running" else "Connecting"
            )
            devices[device_ip].task_status = task_status
        except Exception as e:
            pass  # 忽略錯誤

# 動態刷新並接收指令的函數
def display_and_handle_input(stdscr):
    curses.curs_set(0)  # 隱藏光標
    stdscr.nodelay(1)   # 非阻塞模式
    input_buffer = ""   # 用於存儲用戶輸入
    while not exit_event.is_set():
        # 清除螢幕
        stdscr.clear()
        stdscr.addstr(0, 0, f"Local IP: {local_ip}")
        stdscr.addstr(1, 0, "[Device Status]")
        current_time = time.time()
        row = 2

        # 更新裝置狀態
        for ip, device in devices.items():
            # 判斷連線狀態
            if device.last_response_time and current_time - device.last_response_time > 0.5:
                device.status = "Disconnected"

            last_seen = (
                f"{current_time - device.last_response_time:.1f} seconds ago"
                if device.last_response_time
                else "Never"
            )
            stdscr.addstr(
                row,
                0,
                #f"Device ID: {device.device_id}, IP: {device.ip}, Status: {device.status}, Task: {device.task_status}, Last Seen: {last_seen}"
                f"Device ID: {device.device_id}, IP: {device.ip}, Status: {device.status}, Last Seen: {last_seen}"
            )
            row += 1

        # 顯示輸入提示和當前輸入內容
        stdscr.addstr(row + 1, 0, "Enter command ('start', 'stop', 'exit'): ")
        stdscr.addstr(row + 2, 0, input_buffer)
        stdscr.refresh()

        # 接收鍵盤輸入
        try:
            key = stdscr.getch()
            if key != -1:
                if key in (10, 13):  # Enter 鍵
                    if input_buffer.lower() == "start":
                        broadcast_message("start")
                    elif input_buffer.lower() == "stop":
                        stop_event.set()  # 啟動停止功能
                        threading.Thread(target=stop_function, daemon=True).start()
                    elif input_buffer.lower() == "exit":
                        exit_event.set()
                        break
                    input_buffer = ""  # 清空輸入緩衝區
                elif key == 127:  # Backspace 鍵
                    input_buffer = input_buffer[:-1]
                else:
                    input_buffer += chr(key)
        except Exception:
            pass

        # 每 0.1 秒刷新一次
        time.sleep(0.1)

# 主程式
if __name__ == "__main__":
    try:
        # 啟動回應監聽執行緒
        listener_thread = threading.Thread(target=listen_for_responses, daemon=True)
        listener_thread.start()

        # 啟動心跳訊號執行緒
        heartbeat_thread = threading.Thread(target=heartbeat_function, daemon=True)
        heartbeat_thread.start()

        # 啟動動態顯示和輸入處理
        curses.wrapper(display_and_handle_input)

    except KeyboardInterrupt:
        exit_event.set()
        print("\nProgram terminated.")

    finally:
        sock.close()
