#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本地数据库管理模块
用于替代缺失的dashboard模块，提供数据存储功能
增强版：集成WebSocket实时推送功能
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Optional, List
import os
import threading
import time
import requests

class DatabaseManager:
    """数据库管理器 - 增强版：集成WebSocket推送"""
    
    def __init__(self, db_path: str = "dashboard.db"):
        self.db_path = db_path
        self.websocket_url = "http://localhost:5000"
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建AI分析结果表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    signal TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    reason TEXT,
                    technical_data TEXT,
                    sentiment_data TEXT,
                    stop_loss REAL,
                    take_profit REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建交易动作表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    pnl REAL DEFAULT 0,
                    exchange TEXT NOT NULL,
                    signal TEXT,
                    confidence TEXT,
                    is_simulated BOOLEAN DEFAULT FALSE,
                    position_status TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建持仓信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    size REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    unrealized_pnl REAL DEFAULT 0,
                    leverage REAL NOT NULL,
                    exchange TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建账户信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_balance REAL NOT NULL,
                    available_balance REAL NOT NULL,
                    unrealized_pnl REAL DEFAULT 0,
                    margin_balance REAL NOT NULL,
                    exchange TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    leverage REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建净值历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS equity_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    equity REAL NOT NULL,
                    total_pnl REAL DEFAULT 0,
                    daily_pnl REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建系统健康监控表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    api_success_rate REAL,
                    average_response_time REAL,
                    memory_usage REAL,
                    cpu_usage REAL,
                    disk_usage REAL,
                    error_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ 数据库初始化成功")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            raise
    
    def _push_websocket_update(self, event_type: str, data: Dict):
        """推送WebSocket更新到Dashboard"""
        try:
            payload = {
                'event': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            # 使用requests发送POST请求到Dashboard
            response = requests.post(
                f"{self.websocket_url}/api/webhook",
                json=payload,
                timeout=1,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print(f"✅ WebSocket推送成功: {event_type}")
            else:
                print(f"⚠️ WebSocket推送失败: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ WebSocket推送异常: {e}")
            # 静默失败，不影响主程序运行

    def save_ai_analysis(self, analysis_data: Dict):
        """保存AI分析结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ai_analysis 
                (timestamp, signal, confidence, reason, technical_data, sentiment_data, stop_loss, take_profit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_data.get('timestamp', datetime.now().isoformat()),
                analysis_data.get('signal', 'HOLD'),
                analysis_data.get('confidence', 'MEDIUM'),
                analysis_data.get('reason', ''),
                json.dumps(analysis_data.get('technical_data', {})),
                json.dumps(analysis_data.get('sentiment_data', {})),
                analysis_data.get('stop_loss', 0),
                analysis_data.get('take_profit', 0)
            ))
            
            conn.commit()
            conn.close()
            
            # 推送WebSocket更新
            self._push_websocket_update('signal_update', analysis_data)
            
        except Exception as e:
            print(f"❌ 保存AI分析失败: {e}")
            raise
    
    def save_trading_action(self, action_data: Dict):
        """保存交易动作"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trading_actions 
                (timestamp, action_type, symbol, quantity, price, pnl, exchange, signal, confidence, is_simulated, position_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                action_data.get('timestamp', datetime.now().isoformat()),
                action_data.get('action_type', ''),
                action_data.get('symbol', 'BTCUSDT'),
                action_data.get('quantity', 0),
                action_data.get('price', 0),
                action_data.get('pnl', 0),
                action_data.get('exchange', 'ASTER'),
                action_data.get('signal', ''),
                action_data.get('confidence', ''),
                action_data.get('is_simulated', False),
                action_data.get('position_status', 'UNKNOWN')
            ))
            
            conn.commit()
            conn.close()
            
            # 推送WebSocket更新
            self._push_websocket_update('trading_update', action_data)
            
        except Exception as e:
            print(f"❌ 保存交易动作失败: {e}")
            raise
    
    def save_position_info(self, position_data: Dict):
        """保存持仓信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO positions 
                (timestamp, symbol, side, size, entry_price, current_price, unrealized_pnl, leverage, exchange, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position_data.get('timestamp', datetime.now().isoformat()),
                position_data.get('symbol', 'BTCUSDT'),
                position_data.get('side', 'none'),
                position_data.get('size', 0),
                position_data.get('entry_price', 0),
                position_data.get('current_price', 0),
                position_data.get('unrealized_pnl', 0),
                position_data.get('leverage', 1),
                position_data.get('exchange', 'Aster'),
                position_data.get('status', 'NO_POSITION')
            ))
            
            conn.commit()
            conn.close()
            
            # 推送WebSocket更新
            self._push_websocket_update('position_update', position_data)
            
        except Exception as e:
            print(f"❌ 保存持仓信息失败: {e}")
            raise
    
    def save_account_info(self, account_data: Dict):
        """保存账户信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO accounts 
                (timestamp, total_balance, available_balance, unrealized_pnl, margin_balance, exchange, symbol, leverage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                account_data.get('timestamp', datetime.now().isoformat()),
                account_data.get('total_balance', 0),
                account_data.get('available_balance', 0),
                account_data.get('unrealized_pnl', 0),
                account_data.get('margin_balance', 0),
                account_data.get('exchange', 'Aster'),
                account_data.get('symbol', 'BTCUSDT'),
                account_data.get('leverage', 1)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ 保存账户信息失败: {e}")
            raise
    
    def save_equity_history(self, equity_data: Dict):
        """保存净值历史"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO equity_history 
                (timestamp, equity, total_pnl, daily_pnl)
                VALUES (?, ?, ?, ?)
            ''', (
                equity_data.get('timestamp', datetime.now().isoformat()),
                equity_data.get('equity', 0),
                equity_data.get('total_pnl', 0),
                equity_data.get('daily_pnl', 0)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ 保存净值历史失败: {e}")
            raise
    
    def save_system_health(self, health_data: Dict):
        """保存系统健康数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_health 
                (timestamp, api_success_rate, average_response_time, memory_usage, cpu_usage, disk_usage, error_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                health_data.get('timestamp', datetime.now().isoformat()),
                health_data.get('api_success_rate', 0),
                health_data.get('average_response_time', 0),
                health_data.get('memory_usage', 0),
                health_data.get('cpu_usage', 0),
                health_data.get('disk_usage', 0),
                health_data.get('error_count', 0)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ 保存系统健康数据失败: {e}")
            raise
    
    def get_recent_analysis(self, limit: int = 10) -> List[Dict]:
        """获取最近的AI分析结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM ai_analysis 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                # 解析JSON字段
                if result.get('technical_data'):
                    result['technical_data'] = json.loads(result['technical_data'])
                if result.get('sentiment_data'):
                    result['sentiment_data'] = json.loads(result['sentiment_data'])
                results.append(result)
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"❌ 获取分析结果失败: {e}")
            return []
    
    def get_recent_trades(self, limit: int = 10) -> List[Dict]:
        """获取最近的交易记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM trading_actions 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"❌ 获取交易记录失败: {e}")
            return []
    
    def get_current_position(self) -> Optional[Dict]:
        """获取当前持仓信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM positions 
                WHERE status = 'ACTIVE'
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            
            if row:
                result = dict(zip(columns, row))
                conn.close()
                return result
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"❌ 获取当前持仓失败: {e}")
            return None
    
    def get_account_info(self, limit: int = 10) -> List[Dict]:
        """获取账户信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM accounts 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"❌ 获取账户信息失败: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 30):
        """清理旧数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 删除30天前的数据
            cursor.execute('''
                DELETE FROM ai_analysis WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            
            cursor.execute('''
                DELETE FROM trading_actions WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            
            cursor.execute('''
                DELETE FROM positions WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            
            cursor.execute('''
                DELETE FROM accounts WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            
            cursor.execute('''
                DELETE FROM equity_history WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            
            cursor.execute('''
                DELETE FROM system_health WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            
            conn.commit()
            conn.close()
            print(f"✅ 已清理 {days} 天前的旧数据")
            
        except Exception as e:
            print(f"❌ 清理旧数据失败: {e}")

# 全局数据库实例
db_manager = DatabaseManager()

# 兼容性函数，保持与原dashboard模块的接口一致
def save_account_info(account_data: Dict):
    """保存账户信息 - 兼容性函数"""
    db_manager.save_account_info(account_data)

def save_position_info(position_data: Dict):
    """保存持仓信息 - 兼容性函数"""
    db_manager.save_position_info(position_data)

def save_equity_history(equity_data: Dict):
    """保存净值历史 - 兼容性函数"""
    db_manager.save_equity_history(equity_data)

def save_to_dashboard(analysis_data: Optional[Dict] = None, action_data: Optional[Dict] = None):
    """保存数据到dashboard - 兼容性函数"""
    if analysis_data:
        db_manager.save_ai_analysis(analysis_data)
    if action_data:
        db_manager.save_trading_action(action_data)

if __name__ == "__main__":
    # 测试数据库功能
    print("🧪 测试数据库管理模块")
    print("=" * 50)
    
    # 测试保存和读取数据
    test_analysis = {
        'timestamp': datetime.now().isoformat(),
        'signal': 'BUY',
        'confidence': 'HIGH',
        'reason': '测试分析',
        'technical_data': {'rsi': 50, 'macd': 0.1},
        'sentiment_data': {'positive': 0.6, 'negative': 0.4},
        'stop_loss': 40000,
        'take_profit': 45000
    }
    
    save_account_info(test_analysis)
    print("✅ 测试数据保存成功")
    
    # 获取最近的分析结果
    recent = db_manager.get_recent_analysis(1)
    if recent:
        print(f"✅ 测试数据读取成功: {recent[0]['signal']}")
    
    print("数据库管理模块测试完成！")
