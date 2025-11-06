#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OKX中国API端点测试脚本
测试多个可能的OKX中国API端点，找到可用的连接
"""

import ccxt
import requests
import time
from datetime import datetime
import json
import ssl
import urllib.request

def test_multiple_endpoints():
    """测试多个OKX API端点"""
    print("🔍 测试OKX中国API端点")
    print("=" * 60)
    
    # 候选端点列表
    endpoints = [
        {
            'name': 'OKX国际主站',
            'base_url': 'https://www.okx.com',
            'api_path': '/api/v5/public/time',
            'priority': 1
        },
        {
            'name': 'OKX API直连',
            'base_url': 'https://api.okx.com',
            'api_path': '/api/v5/public/time',
            'priority': 2
        },
        {
            'name': 'OKEX旧域名',
            'base_url': 'https://www.okex.cn',
            'api_path': '/api/v5/public/time',
            'priority': 3
        },
        {
            'name': 'OKEX API旧域名',
            'base_url': 'https://api.okex.cn',
            'api_path': '/api/v5/public/time',
            'priority': 4
        },
        {
            'name': 'OKX中国域名',
            'base_url': 'https://www.okx.com.cn',
            'api_path': '/api/v5/public/time',
            'priority': 5
        },
        {
            'name': 'OKX中国API',
            'base_url': 'https://api.okx.com.cn',
            'api_path': '/api/v5/public/time',
            'priority': 6
        }
    ]
    
    working_endpoints = []
    
    for endpoint in endpoints:
        print(f"\n📡 测试端点: {endpoint['name']}")
        print(f"🔗 URL: {endpoint['base_url']}{endpoint['api_path']}")
        
        success, response_time, error = test_endpoint(endpoint)
        
        if success:
            print(f"✅ 成功！响应时间: {response_time:.2f}秒")
            working_endpoints.append({
                'name': endpoint['name'],
                'base_url': endpoint['base_url'],
                'api_path': endpoint['api_path'],
                'priority': endpoint['priority'],
                'response_time': response_time
            })
        else:
            print(f"❌ 失败: {error}")
    
    return working_endpoints

def test_endpoint(endpoint):
    """测试单个端点"""
    try:
        # 构建完整URL
        url = f"{endpoint['base_url']}{endpoint['api_path']}"
        
        # 设置请求头
        headers = {
            'User-Agent': 'AI-Trading-Bot/1.0',
            'Content-Type': 'application/json',
        }
        
        # 记录开始时间
        start_time = time.time()
        
        # 发送请求
        response = requests.get(
            url, 
            headers=headers, 
            timeout=10,
            verify=False  # 临时禁用SSL验证
        )
        
        # 计算响应时间
        response_time = time.time() - start_time
        
        # 检查响应
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                return True, response_time, None
            else:
                return False, response_time, "响应格式异常"
        else:
            return False, response_time, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, 0, "请求超时"
    except requests.exceptions.ConnectionError:
        return False, 0, "连接错误"
    except Exception as e:
        return False, 0, str(e)

def test_with_ccxt():
    """使用ccxt库测试端点"""
    print("\n🔧 使用ccxt库测试配置")
    print("=" * 40)
    
    working_configs = []
    
    # ccxt配置变体
    ccxt_configs = [
        {
            'name': '默认OKX配置',
            'config': {
                'options': {
                    'defaultType': 'swap',
                    'adjustForTimeDifference': True,
                },
                'timeout': 30,
                'rateLimit': 100,
                'enableRateLimit': True,
                'verify': False,
                'headers': {
                    'User-Agent': 'AI-Trading-Bot/1.0',
                    'Content-Type': 'application/json',
                },
            }
        },
        {
            'name': '自定义端点配置',
            'config': {
                'urls': {
                    'api': {
                        'public': 'https://www.okx.com/api/v5',
                        'private': 'https://www.okx.com/api/v5',
                    }
                },
                'options': {
                    'defaultType': 'swap',
                    'adjustForTimeDifference': True,
                },
                'timeout': 30,
                'rateLimit': 100,
                'enableRateLimit': True,
                'verify': False,
                'headers': {
                    'User-Agent': 'AI-Trading-Bot/1.0',
                    'Content-Type': 'application/json',
                },
            }
        }
    ]
    
    for config in ccxt_configs:
        print(f"\n📊 测试配置: {config['name']}")
        
        try:
            exchange = ccxt.okx(config['config'])
            
            # 测试获取服务器时间
            start_time = time.time()
            server_time = exchange.fetch_time()
            response_time = time.time() - start_time
            
            print(f"✅ 成功！响应时间: {response_time:.2f}秒")
            print(f"🕐 服务器时间: {datetime.fromtimestamp(server_time/1000)}")
            
            # 测试获取价格
            start_time = time.time()
            ticker = exchange.fetch_ticker('BTC/USDT')
            price_time = time.time() - start_time
            
            print(f"💰 BTC价格: ${ticker['last']:,.2f} (获取时间: {price_time:.2f}秒)")
            
            working_configs.append({
                'name': config['name'],
                'config': config['config'],
                'response_time': response_time,
                'price_time': price_time
            })
            
        except Exception as e:
            print(f"❌ 失败: {e}")
    
    return working_configs

def create_optimized_config(working_endpoints, working_configs):
    """创建优化配置"""
    print("\n🎯 生成优化配置")
    print("=" * 40)
    
    if not working_endpoints and not working_configs:
        print("❌ 没有找到可用的端点")
        return None
    
    # 选择最佳配置
    best_config = None
    
    # 优先选择ccxt配置
    if working_configs:
        best_config = min(working_configs, key=lambda x: x['response_time'])
        print(f"🏆 最佳ccxt配置: {best_config['name']}")
        print(f"⏱️ 响应时间: {best_config['response_time']:.2f}秒")
    
    # 备用方案：直接端点
    elif working_endpoints:
        best_endpoint = min(working_endpoints, key=lambda x: x['response_time'])
        print(f"🏆 最佳端点: {best_endpoint['name']}")
        print(f"🔗 URL: {best_endpoint['base_url']}")
        print(f"⏱️ 响应时间: {best_endpoint['response_time']:.2f}秒")
        
        # 创建自定义配置
        custom_config = {
            'name': '最佳端点配置',
            'config': {
                'urls': {
                    'api': {
                        'public': f"{best_endpoint['base_url']}/api/v5",
                        'private': f"{best_endpoint['base_url']}/api/v5",
                    }
                },
                'options': {
                    'defaultType': 'swap',
                    'adjustForTimeDifference': True,
                },
                'timeout': 30,
                'rateLimit': 100,
                'enableRateLimit': True,
                'verify': False,
                'headers': {
                    'User-Agent': 'AI-Trading-Bot/1.0',
                    'Content-Type': 'application/json',
                },
            }
        }
        best_config = custom_config
    
    return best_config

def save_optimized_config(config):
    """保存优化配置"""
    if not config:
        return
    
    print(f"\n💾 保存优化配置: {config['name']}")
    
    # 保存到文件
    config_file = 'okx_optimized_config.json'
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config['config'], f, indent=2, ensure_ascii=False)
    
    print(f"✅ 配置已保存到: {config_file}")
    
    # 生成Python配置代码
    python_code = f'''# OKX优化配置
# 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OKX_OPTIMIZED_CONFIG = {json.dumps(config['config'], indent=4)}

def create_optimized_okx():
    """创建优化的OKX客户端"""
    import ccxt
    return ccxt.okx(OKX_OPTIMIZED_CONFIG)
'''
    
    with open('okx_optimized.py', 'w', encoding='utf-8') as f:
        f.write(python_code)
    
    print("✅ Python配置已保存到: okx_optimized.py")

def main():
    """主函数"""
    print("🤖 OKX中国API端点检测工具")
    print("=" * 60)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 测试基本端点
    working_endpoints = test_multiple_endpoints()
    
    # 测试ccxt配置
    working_configs = test_with_ccxt()
    
    # 生成优化配置
    best_config = create_optimized_config(working_endpoints, working_configs)
    
    # 保存配置
    if best_config:
        save_optimized_config(best_config)
        
        print("\n" + "=" * 60)
        print("🎉 检测完成！")
        print("✅ 已找到可用的OKX API配置")
        print("📁 配置文件已保存，可在交易机器人中使用")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 检测失败")
        print("🔧 未找到可用的OKX API端点")
        print("💡 建议使用代理或VPN")
        print("=" * 60)

if __name__ == "__main__":
    main()
