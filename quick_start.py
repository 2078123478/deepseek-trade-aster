#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速启动脚本
用于快速测试和启动AI交易机器人
"""

import os
import sys
import time
from datetime import datetime

def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("🤖 AI交易机器人 - 快速启动")
    print("=" * 60)
    print("功能特性:")
    print("✅ 多交易所支持 (OKX + Aster)")
    print("✅ DeepSeek AI分析引擎")
    print("✅ 完整技术指标分析")
    print("✅ 市场情绪集成")
    print("✅ 系统健康监控")
    print("✅ 完整数据记录")
    print("=" * 60)

def check_environment():
    """检查环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python版本过低，需要3.8+")
        return False
    
    # 检查当前目录
    if not os.path.exists('.env'):
        print("❌ 未找到.env文件")
        print("请确保在正确的目录运行脚本")
        return False
    
    print("✅ 环境检查通过")
    return True

def install_dependencies():
    """安装依赖"""
    print("\n📦 检查并安装依赖包...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                            capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖包安装成功")
            return True
        else:
            print(f"❌ 依赖包安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装依赖时出错: {e}")
        return False

def run_system_test():
    """运行系统测试"""
    print("\n🧪 运行系统测试...")
    
    try:
        import test_system
        success = test_system.run_full_test()
        return success
        
    except ImportError:
        print("❌ 无法导入测试模块")
        return False
    except Exception as e:
        print(f"❌ 系统测试失败: {e}")
        return False

def run_trading_bot():
    """运行交易机器人"""
    print("\n🚀 启动交易机器人...")
    print("注意: 请确保已正确配置所有API密钥")
    print("按 Ctrl+C 可以停止机器人")
    print("=" * 60)
    
    try:
        import deepseek_multi_exchange_带市场情绪_指标版本 as trading_bot
        trading_bot.main()
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户停止机器人")
    except Exception as e:
        print(f"❌ 交易机器人运行失败: {e}")
        return False
    
    return True

def show_menu():
    """显示菜单"""
    print("\n📋 请选择操作:")
    print("1. 安装依赖包")
    print("2. 运行系统测试")
    print("3. 启动交易机器人")
    print("4. 完整流程 (安装->测试->启动)")
    print("5. 退出")
    
    while True:
        try:
            choice = input("\n请输入选项 (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            else:
                print("❌ 无效选项，请重新输入")
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            sys.exit(0)

def main():
    """主函数"""
    print_banner()
    
    # 检查环境
    if not check_environment():
        input("\n按回车键退出...")
        return
    
    while True:
        choice = show_menu()
        
        if choice == 1:
            # 安装依赖
            install_dependencies()
            
        elif choice == 2:
            # 运行测试
            run_system_test()
            
        elif choice == 3:
            # 启动机器人
            run_trading_bot()
            
        elif choice == 4:
            # 完整流程
            print("\n🔄 执行完整启动流程...")
            
            if install_dependencies():
                print("\n⏱️ 等待2秒后开始测试...")
                time.sleep(2)
                
                if run_system_test():
                    print("\n⏱️ 等待2秒后启动机器人...")
                    time.sleep(2)
                    run_trading_bot()
                else:
                    print("\n❌ 系统测试失败，请检查配置")
            else:
                print("\n❌ 依赖安装失败")
                
        elif choice == 5:
            # 退出
            print("\n👋 再见！")
            break
        
        # 询问是否继续
        if choice != 5:
            try:
                continue_choice = input("\n是否继续使用菜单? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes', '是', '']:
                    print("\n👋 再见！")
                    break
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
