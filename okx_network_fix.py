#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OKX网络连接修复模块
解决DNS劫持、SSL证书验证和网络连接问题
"""

import requests
import socket
import ssl
import urllib3
import time
from datetime import datetime

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OKXNetworkFix:
    def __init__(self):
        self.okx_ips = [
            '18.167.46.29',
            '18.167.255.29', 
            '16.162.145.199'
        ]
        self.okx_domains = [
            'https://okx.com',
            'https://aws.okx.com',
            'https://www.okx.com'
        ]
        
    def test_dns_resolution(self):
        """测试DNS解析"""
        print("🔍 测试DNS解析...")
        
        domains_to_test = ['www.okx.com', 'okx.com', 'aws.okx.com']
        results = {}
        
        for domain in domains_to_test:
            try:
                ip = socket.gethostbyname(domain)
                results[domain] = {
                    'ip': ip,
                    'valid': not ip.startswith('169.254.'),
                    'is_local': ip.startswith('169.254.')
                }
                print(f"  {domain} -> {ip} {'✅' if not ip.startswith('169.254.') else '❌ (DNS劫持)'}")
            except Exception as e:
                results[domain] = {'error': str(e)}
                print(f"  {domain} -> ❌ {e}")
        
        return results
    
    def test_http_connection(self, url, timeout=10, verify_ssl=False):
        """测试HTTP连接"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                url + '/api/v5/public/time',
                headers=headers,
                timeout=timeout,
                verify=verify_ssl
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.SSLError as e:
            return {
                'success': False,
                'error': f"SSL错误: {e}",
                'type': 'ssl_error'
            }
        except requests.exceptions.Timeout as e:
            return {
                'success': False,
                'error': f"连接超时: {e}",
                'type': 'timeout'
            }
        except requests.exceptions.ConnectionError as e:
            return {
                'success': False,
                'error': f"连接错误: {e}",
                'type': 'connection_error'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"未知错误: {e}",
                'type': 'unknown_error'
            }
    
    def test_all_connections(self):
        """测试所有连接方式"""
        print("\n🌐 测试HTTP连接...")
        
        # 测试域名连接
        domain_results = {}
        for domain in self.okx_domains:
            print(f"  测试 {domain}...")
            result = self.test_http_connection(domain, verify_ssl=False)
            domain_results[domain] = result
            
            if result['success']:
                print(f"    ✅ 成功 ({result['response_time']:.2f}s)")
            else:
                print(f"    ❌ 失败: {result['error']}")
        
        # 测试IP直连
        print("\n🔗 测试IP直连...")
        ip_results = {}
        for ip in self.okx_ips:
            print(f"  测试 {ip}...")
            result = self.test_http_connection(f'https://{ip}', verify_ssl=False)
            ip_results[ip] = result
            
            if result['success']:
                print(f"    ✅ 成功 ({result['response_time']:.2f}s)")
            else:
                print(f"    ❌ 失败: {result['error']}")
        
        return domain_results, ip_results
    
    def get_working_connection(self):
        """获取可用的连接方式"""
        domain_results, ip_results = self.test_all_connections()
        
        # 优先使用域名连接
        for domain, result in domain_results.items():
            if result['success']:
                return {
                    'type': 'domain',
                    'url': domain,
                    'response_time': result['response_time']
                }
        
        # 备用IP连接
        for ip, result in ip_results.items():
            if result['success']:
                return {
                    'type': 'ip',
                    'url': f'https://{ip}',
                    'response_time': result['response_time']
                }
        
        return None
    
    def create_ccxt_config(self):
        """创建CCXT配置"""
        working_conn = self.get_working_connection()
        
        if not working_conn:
            print("❌ 没有可用的OKX连接")
            return None
        
        print(f"✅ 使用连接: {working_conn['url']} ({working_conn['response_time']:.2f}s)")
        
        config = {
            'options': {
                'defaultType': 'swap',
                'adjustForTimeDifference': True,
            },
            'timeout': 30000,
            'rateLimit': 1000,
            'enableRateLimit': True,
            'verify': False,  # 跳过SSL验证
        }
        
        # 如果是IP连接，需要设置自定义URL
        if working_conn['type'] == 'ip':
            config['urls'] = {
                'api': {
                    'public': working_conn['url'],
                    'private': working_conn['url'],
                }
            }
        
        return config

def test_okx_connection():
    """测试OKX连接的完整流程"""
    print("🚀 OKX网络连接诊断")
    print("=" * 50)
    
    fixer = OKXNetworkFix()
    
    # 1. DNS解析测试
    dns_results = fixer.test_dns_resolution()
    
    # 2. 连接测试
    working_conn = fixer.get_working_connection()
    
    # 3. 生成配置
    if working_conn:
        config = fixer.create_ccxt_config()
        print(f"\n✅ 连接配置生成成功")
        return config
    else:
        print(f"\n❌ 所有连接方式都失败")
        return None

if __name__ == "__main__":
    config = test_okx_connection()
    if config:
        print("\n🎯 可以使用以下CCXT配置:")
        print(config)
    else:
        print("\n⚠️ 需要检查网络环境或使用VPN")
