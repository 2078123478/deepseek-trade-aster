#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交易机器人启动脚本
支持不同环境的启动和配置管理
"""

import os
import sys
import argparse
from datetime import datetime
import shutil
from dotenv import load_dotenv

def backup_current_config():
    """备份当前配置"""
    if os.path.exists('.env'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'.env.backup_{timestamp}'
        shutil.copy('.env', backup_file)
        print(f"✅ 当前配置已备份到: {backup_file}")

def switch_environment(env_type):
    """切换环境配置"""
    config_files = {
        'production': '.env.production',
        'test': '.env.test',
        'current': '.env'
    }
    
    if env_type not in config_files:
        print(f"❌ 不支持的环境类型: {env_type}")
        print("支持的环境: production, test, current")
        return False
    
    source_file = config_files[env_type]
    
    if env_type in ['production', 'test']:
        # 切换到指定环境
        if not os.path.exists(source_file):
            print(f"❌ 配置文件不存在: {source_file}")
            return False
        
        # 备份当前配置
        if os.path.exists('.env'):
            backup_current_config()
        
        # 复制目标配置
        shutil.copy(source_file, '.env')
        print(f"✅ 已切换到{env_type}环境")
        return True
    
    else:
        # 恢复当前配置
        print("ℹ️ 使用当前配置")
        return True

def validate_environment(env_type):
    """验证环境配置"""
    if env_type == 'production':
        print("🚨 生产环境安全检查")
        
        # 检查关键配置
        required_vars = [
            'DEEPSEEK_API_KEY',
            'TRADING_EXCHANGE',
            'TRADING_ENABLED',
            'PRODUCTION_MODE',
            'ASTER_USER_ADDRESS',
            'ASTER_SIGNER_ADDRESS',
            'ASTER_PRIVATE_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
            return False
        
        # 检查生产模式设置
        if os.getenv('PRODUCTION_MODE', 'false').lower() != 'true':
            print("❌ 生产环境必须设置 PRODUCTION_MODE=true")
            return False
        
        if os.getenv('TRADING_ENABLED', 'false').lower() != 'true':
            print("❌ 生产环境必须设置 TRADING_ENABLED=true")
            return False
        
        if os.getenv('TRADING_EXCHANGE') != 'ASTER':
            print("❌ 生产环境必须设置 TRADING_EXCHANGE=ASTER")
            return False
        
        print("✅ 生产环境配置验证通过")
        return True
    
    elif env_type == 'test':
        print("🧪 测试环境检查")
        
        # 检查测试模式设置
        if os.getenv('TRADING_ENABLED', 'false').lower() != 'false':
            print("⚠️ 测试环境建议设置 TRADING_ENABLED=false")
        
        if os.getenv('PRODUCTION_MODE', 'false').lower() != 'false':
            print("⚠️ 测试环境应该设置 PRODUCTION_MODE=false")
        
        print("✅ 测试环境配置检查完成")
        return True
    
    return True

def start_bot(bot_type, env_type):
    """启动指定类型的交易机器人"""
    print(f"🚀 启动{bot_type}交易机器人")
    print(f"📊 环境: {env_type}")
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if bot_type == 'production':
        # 启动生产环境机器人
        try:
            from production_trading_bot import main as production_main
            production_main()
        except ImportError as e:
            print(f"❌ 无法导入生产环境模块: {e}")
            return False
        except Exception as e:
            print(f"❌ 生产环境启动失败: {e}")
            return False
    
    elif bot_type == 'original':
        # 启动原始机器人（带警告）
        print("⚠️ 启动原始交易机器人")
        print("⚠️ 注意：原始版本存在混合模式问题")
        print("⚠️ 建议使用生产环境版本")
        
        confirm = input("确认继续？(y/N): ")
        if confirm.lower() != 'y':
            print("❌ 已取消启动")
            return False
        
        try:
            from deepseek_multi_exchange_带市场情绪_指标版本 import main as original_main
            original_main()
        except ImportError as e:
            print(f"❌ 无法导入原始模块: {e}")
            return False
        except Exception as e:
            print(f"❌ 原始版本启动失败: {e}")
            return False
    
    elif bot_type == 'dashboard':
        # 启动Dashboard
        print("📱 启动交易Dashboard")
        try:
            from dashboard_app import main as dashboard_main
            dashboard_main()
        except ImportError as e:
            print(f"❌ 无法导入Dashboard模块: {e}")
            return False
        except Exception as e:
            print(f"❌ Dashboard启动失败: {e}")
            return False
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI交易机器人启动器')
    parser.add_argument(
        'command', 
        choices=['start', 'switch', 'status'],
        help='操作命令'
    )
    parser.add_argument(
        '--env', 
        choices=['production', 'test', 'current'],
        default='current',
        help='环境类型'
    )
    parser.add_argument(
        '--bot', 
        choices=['production', 'original', 'dashboard'],
        default='production',
        help='机器人类型'
    )
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='跳过配置验证'
    )
    
    args = parser.parse_args()
    
    # 在执行命令前重新加载环境变量
    if os.path.exists('.env'):
        load_dotenv('.env', override=True)
    
    if args.command == 'switch':
        # 切换环境
        print(f"🔄 切换到{args.env}环境")
        if switch_environment(args.env):
            print("✅ 环境切换成功")
        else:
            print("❌ 环境切换失败")
            sys.exit(1)
    
    elif args.command == 'status':
        # 显示当前状态
        print("📊 当前配置状态")
        print("=" * 40)
        
        # 显示环境变量
        key_vars = [
            'TRADING_EXCHANGE',
            'TRADING_ENABLED', 
            'PRODUCTION_MODE',
            'SIMULATION_MODE'
        ]
        
        for var in key_vars:
            value = os.getenv(var, '未设置')
            status = "✅" if value != '未设置' else "❌"
            print(f"{status} {var}: {value}")
        
        # 判断当前模式
        trading_enabled = os.getenv('TRADING_ENABLED', 'false').lower() == 'true'
        production_mode = os.getenv('PRODUCTION_MODE', 'false').lower() == 'true'
        
        if production_mode:
            print("🚨 当前模式: 生产环境")
        elif trading_enabled:
            print("⚠️ 当前模式: 实盘交易")
        else:
            print("🧪 当前模式: 测试/模拟")
    
    elif args.command == 'start':
        # 启动机器人
        env_type = args.env
        
        # 切换环境（如果不是current）
        if env_type != 'current':
            if not switch_environment(env_type):
                sys.exit(1)
        
        # 验证配置
        if not args.no_validate:
            if not validate_environment(env_type):
                print("❌ 环境验证失败")
                sys.exit(1)
        
        # 启动机器人
        if not start_bot(args.bot, env_type):
            print("❌ 机器人启动失败")
            sys.exit(1)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
