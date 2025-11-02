#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统健康监控模块
用于监控系统运行状态和性能指标
"""

import os
import time
import psutil
import json
from datetime import datetime
from typing import Dict, List, Optional
from database_manager import db_manager

class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.api_call_count = 0
        self.api_success_count = 0
        self.api_response_times = []
        self.error_count = 0
        self.last_health_check = None
        
    def record_api_call(self, success: bool, response_time: float):
        """记录API调用"""
        self.api_call_count += 1
        if success:
            self.api_success_count += 1
        self.api_response_times.append(response_time)
        
        # 只保留最近100次的响应时间
        if len(self.api_response_times) > 100:
            self.api_response_times.pop(0)
    
    def record_error(self, error_type: str = "general"):
        """记录错误"""
        self.error_count += 1
        print(f"📊 系统错误记录: {error_type} (总错误数: {self.error_count})")
    
    def get_system_metrics(self) -> Dict:
        """获取系统指标"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # API成功率
            api_success_rate = (self.api_success_count / self.api_call_count * 100) if self.api_call_count > 0 else 0
            
            # 平均响应时间
            avg_response_time = sum(self.api_response_times) / len(self.api_response_times) if self.api_response_times else 0
            
            # 运行时间
            uptime = (datetime.now() - self.start_time).total_seconds() / 3600  # 小时
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': round(cpu_usage, 2),
                'memory_usage': round(memory_usage, 2),
                'disk_usage': round(disk_usage, 2),
                'api_success_rate': round(api_success_rate, 2),
                'average_response_time': round(avg_response_time, 3),
                'api_call_count': self.api_call_count,
                'error_count': self.error_count,
                'uptime_hours': round(uptime, 2)
            }
            
        except Exception as e:
            print(f"❌ 获取系统指标失败: {e}")
            return {}
    
    def check_system_health(self) -> Dict:
        """检查系统健康状态"""
        metrics = self.get_system_metrics()
        health_status = "HEALTHY"
        warnings = []
        
        # 检查CPU使用率
        if metrics.get('cpu_usage', 0) > 80:
            health_status = "WARNING"
            warnings.append(f"CPU使用率过高: {metrics['cpu_usage']}%")
        
        # 检查内存使用率
        if metrics.get('memory_usage', 0) > 85:
            health_status = "WARNING"
            warnings.append(f"内存使用率过高: {metrics['memory_usage']}%")
        
        # 检查磁盘使用率
        if metrics.get('disk_usage', 0) > 90:
            health_status = "WARNING"
            warnings.append(f"磁盘使用率过高: {metrics['disk_usage']}%")
        
        # 检查API成功率
        if metrics.get('api_success_rate', 100) < 80:
            health_status = "ERROR" if metrics.get('api_success_rate', 100) < 50 else "WARNING"
            warnings.append(f"API成功率过低: {metrics['api_success_rate']}%")
        
        # 检查平均响应时间
        if metrics.get('average_response_time', 0) > 5:
            health_status = "WARNING"
            warnings.append(f"API响应时间过长: {metrics['average_response_time']}秒")
        
        # 检查错误率
        if self.api_call_count > 0:
            error_rate = (self.error_count / self.api_call_count) * 100
            if error_rate > 10:
                health_status = "ERROR" if error_rate > 20 else "WARNING"
                warnings.append(f"错误率过高: {error_rate:.1f}%")
        
        self.last_health_check = {
            'status': health_status,
            'warnings': warnings,
            'metrics': metrics
        }
        
        return self.last_health_check
    
    def save_health_data(self):
        """保存健康数据到数据库"""
        try:
            metrics = self.get_system_metrics()
            health_data = {
                'timestamp': metrics['timestamp'],
                'api_success_rate': metrics['api_success_rate'],
                'average_response_time': metrics['average_response_time'],
                'memory_usage': metrics['memory_usage'],
                'cpu_usage': metrics['cpu_usage'],
                'disk_usage': metrics['disk_usage'],
                'error_count': metrics['error_count']
            }
            
            db_manager.save_system_health(health_data)
            
        except Exception as e:
            print(f"❌ 保存健康数据失败: {e}")
    
    def print_health_status(self):
        """打印健康状态"""
        health = self.check_system_health()
        metrics = health['metrics']
        
        print("\n" + "=" * 50)
        print("🏥 系统健康状态检查")
        print("=" * 50)
        print(f"状态: {health['status']}")
        print(f"运行时间: {metrics.get('uptime_hours', 0):.1f} 小时")
        print(f"API调用: {metrics.get('api_call_count', 0)} 次")
        print(f"API成功率: {metrics.get('api_success_rate', 0):.1f}%")
        print(f"平均响应时间: {metrics.get('average_response_time', 0):.3f} 秒")
        print(f"CPU使用率: {metrics.get('cpu_usage', 0):.1f}%")
        print(f"内存使用率: {metrics.get('memory_usage', 0):.1f}%")
        print(f"磁盘使用率: {metrics.get('disk_usage', 0):.1f}%")
        print(f"错误次数: {metrics.get('error_count', 0)}")
        
        if health['warnings']:
            print("\n⚠️ 警告:")
            for warning in health['warnings']:
                print(f"  - {warning}")
        
        print("=" * 50)
    
    def get_performance_summary(self) -> str:
        """获取性能摘要"""
        metrics = self.get_system_metrics()
        
        return f"""
📊 系统性能摘要
- 运行时间: {metrics.get('uptime_hours', 0):.1f} 小时
- API成功率: {metrics.get('api_success_rate', 0):.1f}%
- 平均响应时间: {metrics.get('average_response_time', 0):.3f}秒
- CPU使用率: {metrics.get('cpu_usage', 0):.1f}%
- 内存使用率: {metrics.get('memory_usage', 0):.1f}%
- 错误次数: {metrics.get('error_count', 0)}
        """.strip()

# 全局监控实例
system_monitor = SystemMonitor()

def safe_api_call(api_func, *args, **kwargs):
    """安全的API调用包装器"""
    start_time = time.time()
    success = False
    
    try:
        result = api_func(*args, **kwargs)
        success = True
        return result
        
    except Exception as e:
        system_monitor.record_error(f"API_ERROR: {str(e)}")
        raise e
        
    finally:
        response_time = time.time() - start_time
        system_monitor.record_api_call(success, response_time)

def validate_config() -> Dict:
    """验证配置完整性"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_configs = {
        'DEEPSEEK_API_KEY': 'DeepSeek API密钥',
        'TRADING_EXCHANGE': '交易所模式',
        'TRADING_SYMBOLS': '交易对'
    }
    
    optional_configs = {
        'OKX_API_KEY': 'OKX API密钥',
        'OKX_SECRET': 'OKX Secret',
        'OKX_PASSWORD': 'OKX密码',
        'ASTER_USER_ADDRESS': 'Aster用户地址',
        'ASTER_SIGNER_ADDRESS': 'Aster签名地址',
        'ASTER_PRIVATE_KEY': 'Aster私钥',
        'ASTER_SIGNATURE_METHOD': 'Aster签名方法'
    }
    
    missing_required = []
    missing_optional = []
    
    # 检查必需配置
    for key, description in required_configs.items():
        if not os.getenv(key):
            missing_required.append(f"{key} ({description})")
    
    # 检查可选配置（根据交易所模式）
    trading_exchange = os.getenv('TRADING_EXCHANGE', 'OKX')
    
    if trading_exchange in ['OKX', 'HYBRID']:
        for key in ['OKX_API_KEY', 'OKX_SECRET', 'OKX_PASSWORD']:
            if not os.getenv(key):
                missing_optional.append(f"{key} ({optional_configs[key]})")
    
    if trading_exchange in ['ASTER', 'HYBRID']:
        for key in ['ASTER_USER_ADDRESS', 'ASTER_SIGNER_ADDRESS', 'ASTER_PRIVATE_KEY']:
            if not os.getenv(key):
                missing_optional.append(f"{key} ({optional_configs[key]})")
    
    return {
        'valid': len(missing_required) == 0,
        'missing_required': missing_required,
        'missing_optional': missing_optional,
        'trading_exchange': trading_exchange
    }

if __name__ == "__main__":
    # 测试系统监控
    print("🧪 测试系统监控模块")
    print("=" * 50)
    
    # 测试配置验证
    print("1. 配置验证:")
    config_status = validate_config()
    if config_status['valid']:
        print("✅ 配置验证通过")
    else:
        print("❌ 配置验证失败:")
        for missing in config_status['missing_required']:
            print(f"  - 缺少必需配置: {missing}")
        for missing in config_status['missing_optional']:
            print(f"  - 缺少可选配置: {missing}")
    
    # 测试系统指标
    print("\n2. 系统指标:")
    system_monitor.print_health_status()
    
    # 测试数据保存
    print("\n3. 数据保存测试:")
    try:
        system_monitor.save_health_data()
        print("✅ 健康数据保存成功")
    except Exception as e:
        print(f"❌ 健康数据保存失败: {e}")
    
    print("\n系统监控模块测试完成！")
