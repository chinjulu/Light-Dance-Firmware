import pygame
import socket
import time
import threading

# 初始化 Pygame
pygame.init()

# 畫面大小與顏色設置
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 122, 255)
RED = (255, 0, 0)

# 創建顯示視窗
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Device Monitor")

# 字型設置
font = pygame.font.SysFont("Times New Roman", 20)

# 設備狀態存儲
devices = {}
exit_event = threading.Event()  # 新增結束程式的事件
stop_event = threading.Event()  # 用於控制停止功能的事件
start_event = threading.Event()  # 控制開始功能

# UDP 通信相關設置
broadcast_address = "192.168.0.255"
port = 12345
response_port = 12346
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("", response_port))
exit_event = threading.Event()

# 按鈕類
class Button:
    def __init__(self, x, y, width, height, color, text, text_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = font.render(self.text, True, self.text_color)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# 按鈕動作

def broadcast_message(message):
    sock.sendto(message.encode(), (broadcast_address, port))
    if message != "heartbeat":
        print(f"Broadcasted message: {message}")

def start_action():
    start_event.set()  # 啟用停止事件
    threading.Thread(target=start_function, daemon=True).start()

def start_function():
    while start_event.is_set():
        broadcast_message("start")
        time.sleep(0.001)  # 每 0.001 秒發送一次開始訊號

        # 檢查是否所有設備都已回應 "running"
        all_running = all(device["status"] == "running" for device in devices.values())
        if all_running:
            print("All devices have been running.")
            start_event.clear()

def stop_action():
    stop_event.set()  # 啟用停止事件
    threading.Thread(target=stop_function, daemon=True).start()

def stop_function():
    while stop_event.is_set():
        broadcast_message("stop")
        time.sleep(0.001)  # 每 0.001 秒發送一次停止訊號

        # 檢查是否所有設備都已回應 "stopped"
        all_stopped = all(device["status"] == "stopped" for device in devices.values())
        if all_stopped:
            print("All devices have stopped.")
            stop_event.clear()


def exit_action():
    exit_event.set()
    pygame.quit()
    exit()

# 定期發送心跳訊號
def heartbeat_function():
    while not exit_event.is_set():
        broadcast_message("heartbeat")
        time.sleep(0.1)  # 每 0.1 秒發送一次心跳訊號

# 設置按鈕
buttons = [
    Button(50, 500, 100, 50, BLUE, "Start", WHITE, start_action),
    Button(200, 500, 100, 50, RED, "Stop", WHITE, stop_action),
    Button(350, 500, 100, 50, GRAY, "Exit", BLACK, exit_action),
]

# 獲取本機 IP 地址
def get_local_ip():
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_sock.connect(("8.8.8.8", 80))
    local_ip = temp_sock.getsockname()[0]
    temp_sock.close()
    return local_ip

local_ip = get_local_ip()

# 接收設備回應的執行緒
def listen_for_responses():
    while not exit_event.is_set():
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode()
            device_ip = addr[0]

            if ":" in message:
                device_id, task_status = map(str.strip, message.split(":", 1))
            else:
                device_id, task_status = "Unknown", message

            if device_ip not in devices:
                devices[device_ip] = {
                    "id": device_id,
                    "status": task_status,
                    "last_seen": time.time()
                }
            else:
                devices[device_ip]["status"] = task_status
                devices[device_ip]["last_seen"] = time.time()
        except Exception:
            pass

# 啟動回應監聽執行緒
listener_thread = threading.Thread(target=listen_for_responses, daemon=True)
listener_thread.start()

# 主循環
heartbeat_thread = threading.Thread(target=heartbeat_function, daemon=True)  # 啟動心跳執行緒
heartbeat_thread.start()

first = 1
running = True
while running:
    screen.fill(WHITE)

    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            exit_event.set()  # 設定退出事件
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.is_clicked(event.pos):
                    button.action()  # 觸發按鈕行為

    # 繪製按鈕
    for button in buttons:
        button.draw(screen)

    # 顯示設備狀態
    y_offset = 50
    for ip, info in devices.items():
        last_seen = f"{time.time() - info['last_seen']:.1f}s ago"
        print({info['status']})
        if first == 1 or {info['status']} != {'heartbeat received'}:
            first = 0
            status_text = f"Device {info['id']} | IP: {ip} | Status: {info['status']} | Last Seen: {last_seen}"
        status_surface = font.render(status_text, True, BLACK)
        screen.blit(status_surface, (50, y_offset))
        y_offset += 30

    pygame.display.flip()
    time.sleep(0.05)  # 控制刷新速度

pygame.quit()
