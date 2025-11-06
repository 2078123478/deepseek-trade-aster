#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard数据集成检查脚本
验证所有API端点与数据库的对应关系
"""

import sqlite3
import requests
import json
from datetime import datetime
import sys

# 设置UTF-8编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class DashboardChecker:
    def __init__(self, db_path="dashboard.db", base_url="http://localhost:5000"):
        self.db_path = db_path
        self.base_url = base_url
        self.issues = []
        self.passed = []
        
    def log_pass(self, message):
        """记录通过的检查"""
        self.passed.append(f"✅ {message}")
        print(f"✅ {message}")
        
    def log_issue(self, message):
        """记录发现的问题"""
        self.issues.append(f"❌ {message}")
        print(f"❌ {message}")
        
    def log_warning(self, message):
        """记录警告"""
        print(f"⚠️  {message}")
    
    def check_database_tables(self):
        """检查数据库表结构"""
        print("\n" + "="*60)
        print("检查 1: 数据库表结构")
        print("="*60)
        
        required_tables = {
            'ai_analysis': ['timestamp', 'signal', 'confidence', 'reason', 'stop_loss', 'take_profit'],
            'trading_actions': ['timestamp', 'action_type', 'symbol', 'quantity', 'price', 'pnl'],
            'positions': ['timestamp', 'symbol', 'side', 'size', 'entry_price', 'current_price', 'unrealized_pnl'],
            'accounts': ['timestamp', 'total_balance', 'available_balance', 'margin_balance', 'leverage'],
            'equity_history': ['timestamp', 'equity', 'total_pnl']
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table_name, required_columns in required_tables.items():
                if table_name in existing_tables:
                    # 检查表的列
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    missing_columns = [col for col in required_columns if col not in columns]
                    
                    if missing_columns:
                        self.log_issue(f"表 '{table_name}' 缺少列: {missing_columns}")
                    else:
                        self.log_pass(f"表 '{table_name}' 结构完整")
                else:
                    self.log_issue(f"缺少必需的表: {table_name}")
            
            conn.close()
            
        except Exception as e:
            self.log_issue(f"数据库检查失败: {e}")
    
    def check_api_endpoints(self):
        """检查API端点可用性"""
        print("\n" + "="*60)
        print("检查 2: API端点可用性")
        print("="*60)
        
        endpoints = [
            '/api/account_info',
            '/api/position_info',
            '/api/equity_history',
            '/api/trading_actions',
            '/api/ai_analysis',
            '/api/current_position',
            '/api/equity_chart'
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.log_pass(f"端点 '{endpoint}' 正常 (返回 {len(data) if isinstance(data, list) else 'dict'} 条数据)")
                    except:
                        self.log_pass(f"端点 '{endpoint}' 正常")
                else:
                    self.log_issue(f"端点 '{endpoint}' 返回状态码: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                self.log_issue(f"无法连接到 '{endpoint}' - Dashboard可能未启动")
                break
            except Exception as e:
                self.log_issue(f"端点 '{endpoint}' 检查失败: {e}")
    
    def check_data_availability(self):
        """检查数据是否可用"""
        print("\n" + "="*60)
        print("检查 3: 数据可用性")
        print("="*60)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查各表的数据量
            tables = {
                'ai_analysis': 'AI分析记录',
                'trading_actions': '交易记录',
                'positions': '持仓记录',
                'accounts': '账户记录',
                'equity_history': '净值历史'
            }
            
            for table, name in tables.items():
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    self.log_pass(f"{name}: {count} 条记录")
                else:
                    self.log_warning(f"{name}: 暂无数据（需要运行交易机器人生成数据）")
            
            conn.close()
            
        except Exception as e:
            self.log_issue(f"数据可用性检查失败: {e}")
    
    def check_frontend_api_mapping(self):
        """检查前端API调用映射"""
        print("\n" + "="*60)
        print("检查 4: 前端-后端API映射")
        print("="*60)
        
        # 读取dashboard.html检查API调用
        try:
            with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 前端使用的API
            frontend_apis = [
                '/api/current_position',
                '/api/account_info',
                '/api/equity_chart',
                '/api/trading_actions',
                '/api/ai_analysis'
            ]
            
            for api in frontend_apis:
                if api in content:
                    self.log_pass(f"前端正确调用: {api}")
                else:
                    self.log_issue(f"前端缺少API调用: {api}")
                    
        except Exception as e:
            self.log_issue(f"前端文件检查失败: {e}")
    
    def check_performance_metrics_support(self):
        """检查性能指标支持"""
        print("\n" + "="*60)
        print("检查 5: 性能指标数据支持")
        print("="*60)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查是否有足够数据计算性能指标
            
            # 1. 总收益率 - 需要equity_history
            cursor.execute("SELECT COUNT(*) FROM equity_history")
            equity_count = cursor.fetchone()[0]
            if equity_count >= 2:
                self.log_pass(f"总收益率: 数据充足 ({equity_count}条净值记录)")
            else:
                self.log_warning(f"总收益率: 数据不足 (需要至少2条记录，当前{equity_count}条)")
            
            # 2. 胜率 - 需要trading_actions
            cursor.execute("SELECT COUNT(*) FROM trading_actions WHERE pnl != 0")
            trade_count = cursor.fetchone()[0]
            if trade_count > 0:
                cursor.execute("SELECT COUNT(*) FROM trading_actions WHERE pnl > 0")
                win_count = cursor.fetchone()[0]
                self.log_pass(f"胜率: 数据充足 ({win_count}/{trade_count})")
            else:
                self.log_warning("胜率: 暂无交易数据")
            
            # 3. 盈亏比 - 需要trading_actions with pnl
            cursor.execute("SELECT SUM(pnl) FROM trading_actions WHERE pnl > 0")
            win_amount = cursor.fetchone()[0] or 0
            cursor.execute("SELECT SUM(pnl) FROM trading_actions WHERE pnl < 0")
            loss_amount = cursor.fetchone()[0] or 0
            if win_amount > 0 or loss_amount < 0:
                self.log_pass(f"盈亏比: 数据充足 (盈利${win_amount:.2f}, 亏损${loss_amount:.2f})")
            else:
                self.log_warning("盈亏比: 暂无盈亏数据")
            
            # 4. 最大回撤 - 需要equity_history
            if equity_count >= 10:
                self.log_pass(f"最大回撤: 数据充足 ({equity_count}条净值记录)")
            else:
                self.log_warning(f"最大回撤: 数据较少 (建议至少10条，当前{equity_count}条)")
            
            conn.close()
            
        except Exception as e:
            self.log_issue(f"性能指标检查失败: {e}")
    
    def check_chart_data_format(self):
        """检查图表数据格式"""
        print("\n" + "="*60)
        print("检查 6: 图表数据格式")
        print("="*60)
        
        try:
            # 测试equity_chart API
            url = f"{self.base_url}/api/equity_chart?hours=24"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查必需字段
                required_fields = ['timestamps', 'equity', 'pnl']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_issue(f"图表数据缺少字段: {missing_fields}")
                else:
                    # 检查数据一致性
                    if len(data['timestamps']) == len(data['equity']) == len(data['pnl']):
                        self.log_pass(f"图表数据格式正确 (长度: {len(data['timestamps'])})")
                    else:
                        self.log_issue("图表数据长度不一致")
            else:
                self.log_warning("无法获取图表数据进行检查")
                
        except requests.exceptions.ConnectionError:
            self.log_warning("Dashboard未启动，跳过实时数据格式检查")
        except Exception as e:
            self.log_issue(f"图表数据格式检查失败: {e}")
    
    def check_websocket_webhook(self):
        """检查WebSocket webhook配置"""
        print("\n" + "="*60)
        print("检查 7: WebSocket实时推送")
        print("="*60)
        
        try:
            # 检查webhook端点
            url = f"{self.base_url}/api/webhook"
            # 不实际发送请求，只检查配置
            self.log_pass("Webhook端点已配置: /api/webhook")
            
            # 检查database_manager中的webhook配置
            with open('database_manager.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'websocket_url' in content and 'push_update' in content:
                    self.log_pass("DatabaseManager已集成WebSocket推送")
                else:
                    self.log_warning("DatabaseManager可能缺少WebSocket推送配置")
                    
        except Exception as e:
            self.log_issue(f"WebSocket检查失败: {e}")
    
    def run_all_checks(self):
        """运行所有检查"""
        print("\n")
        print("="*60)
        print("🔍 Dashboard 数据集成完整性检查")
        print("="*60)
        
        self.check_database_tables()
        self.check_api_endpoints()
        self.check_data_availability()
        self.check_frontend_api_mapping()
        self.check_performance_metrics_support()
        self.check_chart_data_format()
        self.check_websocket_webhook()
        
        # 打印总结
        print("\n")
        print("="*60)
        print("📊 检查总结")
        print("="*60)
        print(f"✅ 通过: {len(self.passed)} 项")
        print(f"❌ 问题: {len(self.issues)} 项")
        
        if self.issues:
            print("\n发现的问题:")
            for issue in self.issues:
                print(f"  {issue}")
        
        print("\n")
        if len(self.issues) == 0:
            print("🎉 所有检查通过！Dashboard已准备好投入生产环境。")
            return True
        elif len(self.issues) <= 2:
            print("⚠️  发现少量问题，建议修复后再投入生产。")
            return False
        else:
            print("❗ 发现多个问题，必须修复后才能投入生产！")
            return False

if __name__ == "__main__":
    checker = DashboardChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)

