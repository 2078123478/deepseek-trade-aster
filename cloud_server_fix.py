#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
云服务器网络修复脚本
为国内云服务器提供OKX API访问解决方案
"""

import os
import json
from datetime import datetime

def create_proxy_config():
    """创建代理配置模板"""
    print("🌐 创建云服务器代理配置")
    print("=" * 50)
    
    proxy_configs = {
        "方案1_代理服务器": {
            "说明": "使用HTTP/HTTPS代理服务器",
            "配置": {
                "http_proxy": "http://proxy_server:port",
                "https_proxy": "http://proxy_server:port",
                "okx_config": {
                    'options': {
                        'defaultType': 'swap',
                        'adjustForTimeDifference': True,
                    },
                    'timeout': 30,
                    'rateLimit': 100,
                    'enableRateLimit': True,
                    'verify': True,
                    'headers': {
                        'User-Agent': 'AI-Trading-Bot/1.0',
                        'Content-Type': 'application/json',
                    },
                }
            }
        },
        "方案2_SOCKS5代理": {
            "说明": "使用SOCKS5代理服务器",
            "配置": {
                "http_proxy": "socks5://proxy_server:port",
                "https_proxy": "socks5://proxy_server:port",
                "okx_config": {
                    'options': {
                        'defaultType': 'swap',
                        'adjustForTimeDifference': True,
                    },
                    'timeout': 30,
                    'rateLimit': 100,
                    'enableRateLimit': True,
                    'verify': True,
                    'headers': {
                        'User-Agent': 'AI-Trading-Bot/1.0',
                        'Content-Type': 'application/json',
                    },
                }
            }
        },
        "方案3_国内镜像": {
            "说明": "使用国内OKX镜像或CDN",
            "配置": {
                "okx_config": {
                    'urls': {
                        'api': {
                            'public': 'https://okx-api.com/api/v5',  # 假设的镜像
                            'private': 'https://okx-api.com/api/v5',
                        }
                    },
                    'options': {
                        'defaultType': 'swap',
                        'adjustForTimeDifference': True,
                    },
                    'timeout': 30,
                    'rateLimit': 100,
                    'enableRateLimit': True,
                    'verify': True,
                    'headers': {
                        'User-Agent': 'AI-Trading-Bot/1.0',
                        'Content-Type': 'application/json',
                    },
                }
            }
        }
    }
    
    # 保存配置到文件
    with open('proxy_configs.json', 'w', encoding='utf-8') as f:
        json.dump(proxy_configs, f, ensure_ascii=False, indent=2)
    
    print("✅ 代理配置模板已保存到 proxy_configs.json")
    return proxy_configs

def create_env_template():
    """创建环境变量模板"""
    print("\n📝 创建环境变量模板")
    print("=" * 50)
    
    env_template = """# 云服务器代理配置模板
# 根据您的实际配置填写以下参数

# 方案1: HTTP代理
# HTTP_PROXY=http://your_proxy_server:port
# HTTPS_PROXY=http://your_proxy_server:port

# 方案2: SOCKS5代理
# HTTP_PROXY=socks5://your_proxy_server:port
# HTTPS_PROXY=socks5://your_proxy_server:port

# 方案3: 国内镜像（如果有的话）
# OKX_BASE_URL=https://okx-mirror.com/api/v5

# 原有配置保持不变
DEEPSEEK_API_KEY=your_deepseek_api_key
ASTER_USER_ADDRESS=your_aster_wallet_address
ASTER_PRIVATE_KEY=your_aster_private_key
TRADING_ENABLED=false
PRODUCTION_MODE=false
TRADING_EXCHANGE=ASTER
MAX_DAILY_LOSS=100
MAX_POSITION_COUNT=1
MIN_CONFIDENCE_LEVEL=MEDIUM
ENABLE_EMERGENCY_STOP=true
MAX_POSITION_SIZE=0.01
LEVERAGE=5
LOG_LEVEL=INFO
DATABASE_PATH=production_dashboard.db
BACKUP_ENABLED=true
"""
    
    with open('.env.cloud', 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print("✅ 环境变量模板已保存到 .env.cloud")

def create_okx_with_proxy():
    """创建支持代理的OKX客户端"""
    print("\n🔧 创建支持代理的OKX客户端")
    print("=" * 50)
    
    proxy_client_code = '''import ccxt
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_okx_with_proxy():
    """创建支持代理的OKX客户端"""
    
    # 获取代理配置
    http_proxy = os.getenv('HTTP_PROXY', '')
    https_proxy = os.getenv('HTTPS_PROXY', '')
    
    okx_config = {
        'options': {
            'defaultType': 'swap',
            'adjustForTimeDifference': True,
        },
        'timeout': 30,
        'rateLimit': 100,
        'enableRateLimit': True,
        'verify': True,
        'headers': {
            'User-Agent': 'AI-Trading-Bot/1.0',
            'Content-Type': 'application/json',
        },
    }
    
    # 如果有代理配置，添加到配置中
    if http_proxy or https_proxy:
        okx_config['proxies'] = {
            'http': http_proxy,
            'https': https_proxy,
        }
        print(f"🌐 使用代理: {http_proxy or https_proxy}")
    
    # 创建会话
    session = requests.Session()
    
    # 设置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # 设置代理
    if http_proxy or https_proxy:
        session.proxies = {
            'http': http_proxy,
            'https': https_proxy,
        }
    
    okx_config['session'] = session
    
    return ccxt.okx(okx_config)
'''
    
    with open('okx_proxy_client.py', 'w', encoding='utf-8') as f:
        f.write(proxy_client_code)
    
    print("✅ 代理客户端代码已保存到 okx_proxy_client.py")

def create_deployment_guide():
    """创建云服务器部署指南"""
    print("\n📖 创建云服务器部署指南")
    print("=" * 50)
    
    guide = """# 云服务器部署指南

## 🔧 网络问题解决方案

### 问题分析
测试结果显示您的云服务器无法直接访问OKX API，这在国内云服务器上是常见问题。

### 解决方案

#### 方案1: 使用代理服务器 (推荐)
1. 购买或配置代理服务器
2. 设置环境变量:
   ```bash
   export HTTP_PROXY=http://your_proxy:port
   export HTTPS_PROXY=http://your_proxy:port
   ```
3. 或在.env文件中添加:
   ```
   HTTP_PROXY=http://your_proxy:port
   HTTPS_PROXY=http://your_proxy:port
   ```

#### 方案2: 使用VPN
1. 在云服务器上安装VPN客户端
2. 连接到海外服务器
3. 测试OKX API连接

#### 方案3: 使用国内镜像
1. 寻找OKX API的国内镜像服务
2. 修改API端点配置

#### 方案4: 使用海外云服务器
1. 考虑使用香港、新加坡等地的云服务器
2. 这些地区可以直接访问OKX API

### 🚀 部署步骤

1. **准备环境**
   ```bash
   # 安装Python依赖
   pip install -r requirements.txt
   
   # 复制配置模板
   cp .env.cloud .env
   ```

2. **配置代理**
   编辑.env文件，添加您的代理配置

3. **测试连接**
   ```bash
   python test_okx_connection.py
   ```

4. **启动服务**
   ```bash
   # 启动Dashboard
   python dashboard_app.py
   
   # 启动交易机器人
   python production_trading_bot.py
   ```

### 📋 常见代理服务

- 阿里云NAT网关
- 腾讯云代理服务
- 第三方代理服务
- 自建代理服务器

### ⚠️ 注意事项

1. 确保代理服务稳定可靠
2. 监控代理连接状态
3. 设置备用连接方案
4. 遵守相关法律法规
"""
    
    with open('CLOUD_DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ 部署指南已保存到 CLOUD_DEPLOYMENT_GUIDE.md")

def main():
    """主函数"""
    print("🚀 云服务器网络配置工具")
    print("=" * 50)
    print(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 创建各种配置文件
    create_proxy_config()
    create_env_template()
    create_okx_with_proxy()
    create_deployment_guide()
    
    print("\n" + "=" * 50)
    print("🎉 云服务器配置文件生成完成！")
    print("=" * 50)
    
    print("\n📁 生成的文件:")
    print("1. proxy_configs.json - 代理配置模板")
    print("2. .env.cloud - 环境变量模板")
    print("3. okx_proxy_client.py - 支持代理的OKX客户端")
    print("4. CLOUD_DEPLOYMENT_GUIDE.md - 详细部署指南")
    
    print("\n🔧 下一步操作:")
    print("1. 阅读部署指南")
    print("2. 配置代理服务器")
    print("3. 测试网络连接")
    print("4. 部署交易机器人")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
