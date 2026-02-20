# simpfun端口扫描

## 重要声明
在使用此工具之前，请确保您有权对目标系统进行端口扫描。您必须确保已获得目标系统的合法授权，未经授权的扫描可能违反法律法规或服务协议。
一旦出现问题或被封禁，作者不对因工具使用导致的任何法律后果承担责任。

## 介绍
simpfun端口扫描是一个简单易用的Minecraft服务器端口扫描工具，旨在帮助用户快速检测目标主机上开放的端口。它适用于网络安全测试、系统维护以及学习网络编程等领域。工具具有友好的用户界面和高效的扫描功能，能够提供准确的端口状态反馈。

## 功能特性
- 多线程并发扫描，提高扫描效率
- 支持自定义端口范围
- 实时显示扫描进度
- 结果自动保存为CSV文件
- 显示服务器在线人数、版本、延迟等信息

## 环境要求
- Python 3.8+
- mcstatus >= 11.1.0

## 安装步骤

### 1. 克隆仓库
```bash
git clone https://github.com/Domdkw/mcserver-port-scanning.git
cd mcserver-port-scanning
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

或者使用pyproject.toml:
```bash
pip install .
```

## 使用方法

### 运行脚本
```bash
python simpfun_scanning_ports.py
```

### 配置参数
运行后按提示输入以下信息：
- **服务器地址**: 输入目标服务器地址（默认: play.simpfun.cn）
- **起始端口**: 输入扫描起始端口（默认: 10000）
- **结束端口**: 输入扫描结束端口（默认: 65533）

### 输出结果
扫描完成后，结果会自动保存到 `server_scan_results.csv` 文件中，包含以下信息：
- server_address: 服务器地址
- server_port: 服务器端口
- online_count: 在线玩家数
- max_players: 最大玩家数
- version: 游戏版本
- protocol: 协议版本
- latency: 服务器延迟

## 注意事项
- 确保您的网络环境允许进行端口扫描。
- 不建议对公共互联网上的设备进行大规模扫描，以免造成不必要的网络负担。
- 扫描可能需要较长时间，请耐心等待。

## 许可证
MIT License - See LICENSE file for details
