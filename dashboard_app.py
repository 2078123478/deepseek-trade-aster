#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI交易机器人 Dashboard
用于可视化展示交易数据、持仓信息和分析结果
"""

# 设置UTF-8编码（Windows兼容）
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 启用eventlet异步支持 - 必须在其他导入之前
import eventlet
eventlet.monkey_patch()

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import plotly.graph_objs as go
import plotly.utils

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

class DashboardManager:
    """Dashboard数据管理器 - 使用database_manager中的数据"""
    
    def __init__(self, db_path: str = "dashboard.db"):
        from database_manager import db_manager
        self.db_manager = db_manager
    
    def get_account_info(self, limit: int = 10) -> List[Dict]:
        """获取账户信息 - 使用database_manager"""
        # 从数据库获取账户信息
        conn = sqlite3.connect(self.db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM accounts 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data
    
    def get_position_info(self, limit: int = 10) -> List[Dict]:
        """获取持仓信息 - 使用database_manager"""
        # 从数据库获取最新持仓
        conn = sqlite3.connect(self.db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM positions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data
    
    def get_equity_history(self, hours: int = 24) -> List[Dict]:
        """获取净值历史 - 使用database_manager"""
        # 从数据库获取净值历史
        conn = sqlite3.connect(self.db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM equity_history 
            WHERE timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp ASC
        '''.format(hours))
        
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data
    
    def get_trading_actions(self, limit: int = 20) -> List[Dict]:
        """获取交易动作 - 使用database_manager"""
        return self.db_manager.get_recent_trades(limit)
    
    def get_ai_analysis(self, limit: int = 5) -> List[Dict]:
        """获取AI分析结果 - 使用database_manager"""
        return self.db_manager.get_recent_analysis(limit)
    
    def get_latest_position(self) -> Optional[Dict]:
        """获取最新持仓 - 使用database_manager"""
        return self.db_manager.get_current_position()

# 初始化Dashboard管理器
dashboard = DashboardManager()

@app.route('/')
def index():
    """主页"""
    return render_template('dashboard.html')

@app.route('/api/account_info')
def api_account_info():
    """获取账户信息API"""
    data = dashboard.get_account_info()
    return jsonify(data)

@app.route('/api/position_info')
def api_position_info():
    """获取持仓信息API"""
    data = dashboard.get_position_info()
    return jsonify(data)

@app.route('/api/equity_history')
def api_equity_history():
    """获取净值历史API"""
    hours = request.args.get('hours', 24, type=int)
    data = dashboard.get_equity_history(hours)
    return jsonify(data)

@app.route('/api/trading_actions')
def api_trading_actions():
    """获取交易动作API"""
    data = dashboard.get_trading_actions()
    return jsonify(data)

@app.route('/api/ai_analysis')
def api_ai_analysis():
    """获取AI分析API"""
    data = dashboard.get_ai_analysis()
    return jsonify(data)

@app.route('/api/current_position')
def api_current_position():
    """获取当前持仓API"""
    data = dashboard.get_latest_position()
    return jsonify(data)

@app.route('/api/equity_chart')
def api_equity_chart():
    """获取净值图表数据"""
    hours = request.args.get('hours', 24, type=int)
    data = dashboard.get_equity_history(hours)
    
    if not data:
        return jsonify({'timestamps': [], 'equity': [], 'pnl': []})
    
    timestamps = [item['timestamp'] for item in data]
    equity = [item['equity'] for item in data]
    pnl = [item['total_pnl'] for item in data]
    
    return jsonify({
        'timestamps': timestamps,
        'equity': equity,
        'pnl': pnl
    })

@app.route('/api/webhook', methods=['POST'])
def api_webhook():
    """接收WebSocket推送的webhook端点"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        event_type = data.get('event')
        payload_data = data.get('data')
        
        if not event_type or not payload_data:
            return jsonify({'error': 'Missing event or data'}), 400
        
        # 根据事件类型推送到对应的WebSocket客户端
        if event_type == 'signal_update':
            socketio.emit('signal_update', {
                'data': [payload_data],  # 包装成列表格式
                'timestamp': data.get('timestamp')
            }, room='default')
        elif event_type == 'position_update':
            socketio.emit('position_update', {
                'data': payload_data,
                'timestamp': data.get('timestamp')
            }, room='default')
        elif event_type == 'account_update':
            # 获取最新账户信息
            account_data = dashboard.get_account_info(limit=1)
            socketio.emit('account_update', {
                'data': account_data,
                'timestamp': data.get('timestamp')
            }, room='default')
        elif event_type == 'trading_update':
            # 获取最新交易记录
            trading_data = dashboard.get_trading_actions(limit=1)
            socketio.emit('trading_update', {
                'data': trading_data,
                'timestamp': data.get('timestamp')
            }, room='default')
        elif event_type == 'system_update':
            socketio.emit('system_status', {
                'data': payload_data,
                'timestamp': data.get('timestamp')
            }, room='default')
        
        return jsonify({'success': True, 'message': f'Event {event_type} pushed successfully'})
        
    except Exception as e:
        print(f"Webhook处理失败: {e}")
        return jsonify({'error': str(e)}), 500

# WebSocket事件处理器
@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    print(f'客户端连接: {request.sid}')
    emit('connected', {
        'message': 'WebSocket连接成功', 
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开"""
    print(f'客户端断开: {request.sid}')

@socketio.on('subscribe')
def handle_subscribe(data):
    """客户端订阅数据更新"""
    trader_id = data.get('trader_id', 'default')
    join_room(trader_id)
    emit('subscribed', {
        'trader_id': trader_id, 
        'message': '订阅成功'
    })
    print(f'客户端订阅: {trader_id}')

def main():
    """主函数"""
    print("🚀 启动AI交易机器人 Dashboard")
    print("=" * 50)
    
    # 创建HTML模板
    print("✅ Dashboard模板已存在，跳过创建")
    
    # 检查数据库
    try:
        dashboard = DashboardManager()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    # 启动Web服务器
    print("🌐 启动Web服务器...")
    print("📱 Dashboard地址: http://localhost:5000")
    print("🔄 数据每60秒自动刷新")
    print("⏹️ 按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        print("🌐 启动WebSocket服务器...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n⏹️ Dashboard已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")

if __name__ == "__main__":
    main()
