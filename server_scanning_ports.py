# MIT License ,See https://github.com/Domdkw/mcserver-port-scanning/blob/master/LICENSE
from mcstatus import JavaServer
import csv
import os
import concurrent.futures
from queue import Queue
import threading
import time
import platform
import shutil

# 配置参数
SERVER_ADDRESS = input("请输入服务器地址[play.simpfun.cn...]: ").strip() or "play.simpfun.cn"
start_port_input = input("请输入起始端口[10000]: ").strip()
START_PORT = int(start_port_input) if start_port_input else 10000
print(f"起始端口: {START_PORT}")
end_port_input = input("请输入结束端口[65533]: ").strip()
END_PORT = int(end_port_input) if end_port_input else 65533
print(f"结束端口: {END_PORT}")
THREAD_COUNT = 10
CSV_FILENAME = "server_scan_results.csv"
DEFAULT_DELAY = 1

total_ports = END_PORT - START_PORT + 1

# 存储活跃服务器列表
active_servers = []
batch_servers = []

# 存储扫描结果的队列和列表
result_queue = Queue()
scan_results = []

# 控制CSV文件是否已创建
csv_file_created = False
csv_lock = threading.Lock()

# 界面显示相关
display_lock = threading.Lock()

scanned_count = 0


def get_minecraft_server_status(server_address, server_port):
    """
    获取Minecraft服务器状态
    :param server_address: 服务器地址
    :param server_port: 服务器端口
    :return: 服务器状态字典或None
    """
    try:
        server = JavaServer(server_address, server_port)
        status = server.status()

        # 提取相关信息
        online_count = status.players.online
        max_players = status.players.max
        version = status.version.name
        protocol = status.version.protocol
        latency = status.latency

        result = {
            "server_address": server_address,
            "server_port": server_port,
            "online_count": online_count,
            "max_players": max_players,
            "version": version,
            "protocol": protocol,
            "latency": latency
        }
        # 只将成功响应的服务器添加到结果队列
        result_queue.put(result)
        return result
    except Exception:
        return None


def write_results_to_csv():
    """
    将扫描结果写入CSV文件
    """
    global csv_file_created

    with csv_lock:
        # 检查是否是第一次创建文件
        file_exists = os.path.exists(CSV_FILENAME)
        mode = 'a' if (file_exists and csv_file_created) else 'w'

        with open(CSV_FILENAME, mode, newline='', encoding='utf-8') as csvfile:
            fieldnames = ['server_address', 'server_port', 'online_count', 'max_players', 'version', 'protocol', 'latency']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # 如果是第一次创建文件，写入表头
            if mode == 'w':
                writer.writeheader()
                csv_file_created = True

            # 只写入成功响应的服务器结果
            while not result_queue.empty():
                result = result_queue.get()
                if result['version'] != 'N/A':
                    writer.writerow(result)
                    scan_results.append(result)


def clear_screen():
    """清空控制台屏幕"""
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def draw_progress_bar(progress, total, found_count, batch_start, batch_end):
    """
    在屏幕顶部绘制进度条
    :param progress: 当前进度
    :param total: 总进度
    :param found_count: 已发现的服务器数量
    :param batch_start: 当前批次起始端口
    :param batch_end: 当前批次结束端口
    """
    terminal_width = shutil.get_terminal_size().columns
    
    print('=' * terminal_width)
    
    percent = (progress / total) * 100 if total > 0 else 0
    bar_length = min(40, terminal_width - 35)
    filled_length = int(bar_length * progress / total) if total > 0 else 0
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    
    print(f'| 进度: [{bar}] {percent:.1f}% ({progress}/{total})')
    print(f'| 已发现服务器: {found_count} 个 | 当前批次: {batch_start}-{batch_end}')
    
    print('=' * terminal_width)


def print_batch_servers(servers):
    """
    打印当前批次发现的服务器
    :param servers: 当前批次服务器列表
    """
    if servers:
        print()
        print('当前批次发现的服务器:')
        print('-' * 50)
        for server in servers:
            print(f'  {server["server_address"]}:{server["server_port"]} | '
                  f'在线: {server["online_count"]}/{server["max_players"]} | '
                  f'版本: {server["version"]} | 延迟: {server["latency"]:.0f}ms')
        print('-' * 50)
    else:
        print()
        print('当前批次未发现活跃服务器')


def scan_port(port):
    """
    扫描指定端口
    :param port: 端口号
    :return: 服务器状态字典或None
    """
    global scanned_count
    status = get_minecraft_server_status(SERVER_ADDRESS, port)
    with display_lock:
        scanned_count += 1
        if status is not None and status['online_count'] != 'N/A':
            active_servers.append(status)
            batch_servers.append(status)
            write_results_to_csv()
    return status


if __name__ == "__main__":
    if os.path.exists(CSV_FILENAME):
        os.remove(CSV_FILENAME)
        print(f"已删除旧的结果文件: {CSV_FILENAME}")
    csv_file_created = False

    try:
        thread_input = input(f"请输入扫描线程数 [{THREAD_COUNT}]: ").strip()
        if thread_input == '':
            thread_count = THREAD_COUNT
        else:
            thread_count = int(thread_input)
            if thread_count <= 0:
                raise ValueError
        print(f"设置线程数为: {thread_count}")
    except ValueError:
        print(f"输入无效，使用默认线程数: {THREAD_COUNT}")
        thread_count = THREAD_COUNT

    try:
        delay_input = input(f"请输入批次间隔时间(秒) [{DEFAULT_DELAY}]: ").strip()
        if delay_input == '':
            batch_delay = DEFAULT_DELAY
        else:
            batch_delay = float(delay_input)
            if batch_delay < 0:
                raise ValueError
        print(f"设置批次间隔时间为: {batch_delay} 秒")
    except ValueError:
        print(f"输入无效，使用默认间隔时间: {DEFAULT_DELAY} 秒")
        batch_delay = DEFAULT_DELAY

    batch_size = thread_count

    clear_screen()

    scanned_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        for batch_start in range(START_PORT, END_PORT + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, END_PORT)
            batch_ports = range(batch_start, batch_end + 1)

            clear_screen()
            draw_progress_bar(scanned_count, total_ports, len(active_servers), batch_start, batch_end)
            print(f'正在扫描端口: {batch_start} - {batch_end} ...')

            futures = [executor.submit(scan_port, port) for port in batch_ports]
            concurrent.futures.wait(futures)

            clear_screen()
            draw_progress_bar(scanned_count, total_ports, len(active_servers), batch_start, batch_end)
            print_batch_servers(batch_servers)

            batch_servers.clear()

            if batch_end < END_PORT:
                print()
                print(f'等待 {batch_delay} 秒后继续...')
                time.sleep(batch_delay)

    print()
    print('=' * shutil.get_terminal_size().columns)
    print()
    print("[完成] 所有端口扫描完成!")
    print(f"[完成] 总共扫描了 {total_ports} 个端口，发现 {len(active_servers)} 个活跃服务器")
    print(f"[完成] 扫描结果已保存到: {CSV_FILENAME}")
