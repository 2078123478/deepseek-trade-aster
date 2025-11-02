#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生产环境交易机器人 - 修复混合模式问题
确保单一交易所和明确的交易模式
"""

import os
import time
import schedule
from openai import OpenAI
import ccxt
import pandas as pd
import re
from dotenv import load_dotenv
import json
import requests
from datetime import datetime, timedelta
from aster_client_trading import AsterFuturesClient
import sqlite3
import sys
import os
import logging
from typing import Dict, Optional, List
from database_manager import save_account_info, save_position_info, save_equity_history, save_to_dashboard
from system_monitor import system_monitor, safe_api_call, validate_config

# 生产环境配置管理
class ProductionConfig:
    """生产环境配置管理类"""
    
    def __init__(self, env_file=None):
        """初始化配置，支持指定配置文件"""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # 交易模式配置
        self.trading_exchange = os.getenv('TRADING_EXCHANGE', 'ASTER')
        self.trading_enabled = os.getenv('TRADING_ENABLED', 'false').lower() == 'true'
        self.production_mode = os.getenv('PRODUCTION_MODE', 'false').lower() == 'true'
        
        # 安全配置
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', 100))
        self.max_position_count = int(os.getenv('MAX_POSITION_COUNT', 1))
        self.min_confidence_level = os.getenv('MIN_CONFIDENCE_LEVEL', 'MEDIUM')
        self.emergency_stop_enabled = os.getenv('ENABLE_EMERGENCY_STOP', 'true').lower() == 'true'
        
        # 交易参数
        self.amount = float(os.getenv('MAX_POSITION_SIZE', 0.01))
        self.leverage = int(os.getenv('LEVERAGE', 5))
        self.symbol = 'BTCUSDT'
        
        # 数据库配置
        self.database_path = os.getenv('DATABASE_PATH', 'production_dashboard.db')
        self.backup_enabled = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
        
        # 安全检查
        self._validate_config()
    
    def _validate_config(self):
        """验证配置安全性"""
        if self.production_mode:
            print("🚨 生产模式安全检查")
            
            # 检查交易模式
            if self.trading_exchange != 'ASTER':
                raise ValueError("生产环境仅支持ASTER交易所")
            
            # 检查交易启用状态
            if not self.trading_enabled:
                raise ValueError("生产模式必须启用交易")
            
            # 检查单一交易所
            if self.trading_exchange in ['HYBRID', 'OKX']:
                raise ValueError("生产环境禁止使用混合模式")
            
            print("✅ 生产模式配置验证通过")
        else:
            print("🧪 测试模式")
    
    def get_trading_mode(self):
        """获取明确的交易模式"""
        if self.production_mode:
            return 'PRODUCTION'
        elif self.trading_enabled:
            return 'LIVE_TRADING'
        else:
            return 'SIMULATION'
    
    def is_real_trading(self):
        """是否真实交易"""
        return self.trading_enabled  # 生产模式下也是真实交易
    
    def should_execute_trade(self, confidence):
        """判断是否应该执行交易"""
        if not self.trading_enabled:
            return False, "交易未启用"
        
        confidence_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
        required_level = confidence_levels.get(self.min_confidence_level, 2)
        current_level = confidence_levels.get(confidence, 0)
        
        if current_level < required_level:
            return False, f"信心度不足: {confidence} < {self.min_confidence_level}"
        
        return True, "可以执行交易"

# 全局配置
config = ProductionConfig()

# 初始化DeepSeek客户端
deepseek_client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# 初始化交易所客户端（仅Aster）
aster_client = None

if config.trading_exchange == 'ASTER':
    try:
        aster_user = os.getenv('ASTER_USER_ADDRESS')
        aster_signer = os.getenv('ASTER_SIGNER_ADDRESS')
        aster_private = os.getenv('ASTER_PRIVATE_KEY')
        
        if not all([aster_user, aster_signer, aster_private]):
            raise ValueError("Aster交易所配置不完整")
        
        signature_method = os.getenv('ASTER_SIGNATURE_METHOD', 'hmac')
        aster_client = AsterFuturesClient(signature_method=signature_method)
        print(f"✅ Aster交易所初始化成功 (签名方法: {signature_method})")
        
    except Exception as e:
        print(f"❌ Aster交易所初始化失败: {e}")
        if config.production_mode:
            raise RuntimeError("生产环境必须成功初始化交易所")
        aster_client = None
else:
    raise ValueError(f"不支持的交易所: {config.trading_exchange}")

# 交易参数配置
TRADE_CONFIG = {
    'symbol': config.symbol,
    'amount': config.amount,
    'leverage': config.leverage,
    'timeframe': '15m',
    'data_points': 96,
}

# 全局变量
price_history = []
signal_history = []
position = None
daily_loss = 0
daily_trade_count = 0

# 设置日志系统
def setup_logging():
    """设置日志系统"""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('production_trading_bot.log'),
            logging.StreamHandler()
        ]
    )
    
    # 记录启动信息
    logger = logging.getLogger(__name__)
    logger.info(f"生产环境交易机器人启动")
    logger.info(f"交易模式: {config.get_trading_mode()}")
    logger.info(f"交易所: {config.trading_exchange}")
    logger.info(f"交易启用: {config.trading_enabled}")
    logger.info(f"生产模式: {config.production_mode}")

# 初始化日志
setup_logging()

def get_safe_trading_status():
    """获取安全的交易状态"""
    status = {
        'mode': config.get_trading_mode(),
        'real_trading': config.is_real_trading(),
        'exchange': config.trading_exchange,
        'emergency_stop': False,
        'daily_loss': daily_loss,
        'daily_trade_count': daily_trade_count,
        'max_daily_loss': config.max_daily_loss,
        'max_position_count': config.max_position_count
    }
    
    # 紧急停止检查
    if config.emergency_stop_enabled and daily_loss >= config.max_daily_loss:
        status['emergency_stop'] = True
        status['reason'] = f"达到最大日亏损限制: {config.max_daily_loss} USDT"
    
    return status

def get_btc_market_data():
    """获取BTC市场数据 - 使用OKX作为数据源"""
    try:
        # 使用OKX作为数据源（仅数据获取，不交易）
        okx_config = {
            'options': {
                'defaultType': 'swap',
                'adjustForTimeDifference': True,
            },
            'timeout': 30000,
            'rateLimit': 1000,
            'enableRateLimit': True,
            'verify': False,
        }
        
        exchange = ccxt.okx(okx_config)
        
        # 获取K线数据
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', '15m', limit=96)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # 计算技术指标
        df = calculate_technical_indicators(df)
        
        current_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        return {
            'price': float(current_data['close']),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'high': float(current_data['high']),
            'low': float(current_data['low']),
            'volume': float(current_data['volume']),
            'price_change': float(((current_data['close'] - previous_data['close']) / previous_data['close']) * 100),
            'technical_data': {
                'sma_5': float(current_data.get('sma_5', 0)),
                'sma_20': float(current_data.get('sma_20', 0)),
                'sma_50': float(current_data.get('sma_50', 0)),
                'rsi': float(current_data.get('rsi', 0)),
                'macd': float(current_data.get('macd', 0)),
                'macd_signal': float(current_data.get('macd_signal', 0)),
                'bb_upper': float(current_data.get('bb_upper', 0)),
                'bb_lower': float(current_data.get('bb_lower', 0)),
            },
            'kline_data': df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].tail(5).to_dict('records'),
            'data_source': 'okx'
        }
        
    except Exception as e:
        print(f"❌ 市场数据获取失败: {e}")
        return None

def calculate_technical_indicators(df):
    """计算技术指标"""
    try:
        # 移动平均线
        df['sma_5'] = df['close'].rolling(window=5, min_periods=1).mean()
        df['sma_20'] = df['close'].rolling(window=20, min_periods=1).mean()
        df['sma_50'] = df['close'].rolling(window=50, min_periods=1).mean()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()

        # 布林带
        df['bb_middle'] = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)

        return df.bfill().ffill()
    except Exception as e:
        print(f"技术指标计算失败: {e}")
        return df

def get_current_position():
    """获取当前持仓（仅Aster）"""
    try:
        if not aster_client:
            return {'exchange': 'NONE', 'side': 'none', 'size': 0, 'status': 'NO_CLIENT'}
        
        positions = aster_client.get_positions(config.symbol)
        
        if isinstance(positions, list) and len(positions) > 0:
            for position in positions:
                symbol = position.get('symbol', '')
                position_amt = float(position.get('positionAmt', 0))
                
                if symbol == config.symbol and position_amt != 0:
                    return {
                        'exchange': 'Aster',
                        'side': 'long' if position_amt > 0 else 'short',
                        'size': abs(position_amt),
                        'entry_price': float(position.get('entryPrice', 0)),
                        'unrealized_pnl': float(position.get('unRealizedProfit', 0)),
                        'leverage': config.leverage,
                        'symbol': symbol,
                        'status': 'ACTIVE'
                    }
        
        return {
            'exchange': 'Aster',
            'side': 'none',
            'size': 0,
            'entry_price': 0,
            'unrealized_pnl': 0,
            'leverage': config.leverage,
            'symbol': config.symbol,
            'status': 'NO_POSITION'
        }
        
    except Exception as e:
        print(f"⚠️ 持仓获取失败: {e}")
        return {
            'exchange': 'Aster',
            'side': 'none',
            'size': 0,
            'entry_price': 0,
            'unrealized_pnl': 0,
            'leverage': config.leverage,
            'symbol': config.symbol,
            'status': 'API_FAILED',
            'error': str(e)
        }

def analyze_with_deepseek(price_data):
    """使用DeepSeek分析市场"""
    try:
        # 构建分析提示
        prompt = f"""
        你是一个专业的BTC/USDT交易分析师。基于以下数据进行分析：

        当前价格: ${price_data['price']:,.2f}
        价格变化: {price_data['price_change']:+.2f}%
        RSI: {price_data['technical_data']['rsi']:.1f}
        MACD: {price_data['technical_data']['macd']:.4f}
        信号线: {price_data['technical_data']['macd_signal']:.4f}

        交易模式: {config.get_trading_mode()}
        最低信心度要求: {config.min_confidence_level}

        请给出明确的交易信号，JSON格式：
        {{
            "signal": "BUY|SELL|HOLD",
            "reason": "分析理由",
            "stop_loss": 具体价格,
            "take_profit": 具体价格,
            "confidence": "HIGH|MEDIUM|LOW"
        }}
        """

        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"你是专业的BTC交易员，交易模式：{config.get_trading_mode()}"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        result = response.choices[0].message.content
        start_idx = result.find('{')
        end_idx = result.rfind('}') + 1

        if start_idx != -1 and end_idx != 0:
            json_str = result[start_idx:end_idx]
            signal_data = json.loads(json_str)
            
            # 添加时间戳
            signal_data['timestamp'] = price_data['timestamp']
            
            # 保存到历史
            signal_history.append(signal_data)
            if len(signal_history) > 30:
                signal_history.pop(0)
            
            return signal_data

        return {
            "signal": "HOLD",
            "reason": "分析失败，保守策略",
            "stop_loss": price_data['price'] * 0.98,
            "take_profit": price_data['price'] * 1.02,
            "confidence": "LOW"
        }

    except Exception as e:
        print(f"DeepSeek分析失败: {e}")
        return {
            "signal": "HOLD",
            "reason": "AI分析失败",
            "stop_loss": price_data['price'] * 0.98,
            "take_profit": price_data['price'] * 1.02,
            "confidence": "LOW"
        }

def execute_production_trade(signal_data, price_data):
    """执行生产环境交易"""
    global daily_loss, daily_trade_count
    
    # 获取交易状态
    status = get_safe_trading_status()
    
    # 紧急停止检查
    if status['emergency_stop']:
        print(f"🚨 紧急停止: {status['reason']}")
        return
    
    # 检查是否应该执行交易
    can_trade, reason = config.should_execute_trade(signal_data['confidence'])
    if not can_trade:
        print(f"🔒 交易限制: {reason}")
        return
    
    # 获取当前持仓
    current_position = get_current_position()
    
    # 记录交易决策
    trading_record = {
        'timestamp': datetime.now().isoformat(),
        'signal': signal_data['signal'],
        'confidence': signal_data['confidence'],
        'reason': signal_data['reason'],
        'mode': status['mode'],
        'real_trading': status['real_trading'],
        'exchange': status['exchange'],
        'current_position': current_position
    }
    
    print(f"📋 交易决策: {signal_data['signal']} | 信心: {signal_data['confidence']}")
    print(f"📊 当前价格: ${price_data['price']:,.2f} | 变化: {price_data['price_change']:+.2f}%")
    
    # 安全处理止损止盈价格显示
    stop_loss = signal_data.get('stop_loss', 0)
    take_profit = signal_data.get('take_profit', 0)
    if stop_loss is None:
        stop_loss = 0
    if take_profit is None:
        take_profit = 0
    print(f"🎯 止损: ${stop_loss:,.2f} | 止盈: ${take_profit:,.2f}")
    
    # 执行交易逻辑 - 修复持仓状态判断错误
    if config.trading_enabled:
        execute_real_trade(signal_data, price_data, current_position)
    elif not config.trading_enabled:
        print("🧪 模拟模式: 仅记录交易决策")
    
    # 保存交易记录
    save_trading_record(trading_record, signal_data, price_data)

def execute_real_trade(signal_data, price_data, current_position):
    """执行真实交易"""
    try:
        if not aster_client:
            print("❌ 交易所客户端未初始化")
            return
        
        # 执行交易逻辑
        if signal_data['signal'] == 'BUY':
            if current_position['side'] == 'short':
                # 平空开多
                print("🔄 平空仓，开多仓...")
                aster_client.place_order(config.symbol, 'BUY', 'MARKET', current_position['size'])
                time.sleep(1)
                aster_client.place_order(config.symbol, 'BUY', 'MARKET', config.amount)
            elif current_position['side'] == 'none':
                # 直接开多
                print("📈 开多仓...")
                aster_client.place_order(config.symbol, 'BUY', 'MARKET', config.amount)
            else:
                print("📊 已有多仓，保持")
        
        elif signal_data['signal'] == 'SELL':
            if current_position['side'] == 'long':
                # 平多开空
                print("🔄 平多仓，开空仓...")
                aster_client.place_order(config.symbol, 'SELL', 'MARKET', current_position['size'])
                time.sleep(1)
                aster_client.place_order(config.symbol, 'SELL', 'MARKET', config.amount)
            elif current_position['side'] == 'none':
                # 直接开空
                print("📉 开空仓...")
                aster_client.place_order(config.symbol, 'SELL', 'MARKET', config.amount)
            else:
                print("📊 已有空仓，保持")
        
        print("✅ 交易执行成功")
        
    except Exception as e:
        print(f"❌ 交易执行失败: {e}")

def save_trading_record(trading_record, signal_data, price_data):
    """保存标准化交易记录"""
    try:
        # 保存AI分析结果
        analysis_data = {
            'timestamp': trading_record['timestamp'],
            'signal': signal_data['signal'],
            'confidence': signal_data['confidence'],
            'reason': signal_data['reason'],
            'technical_data': price_data['technical_data'],
            'sentiment_data': {},
            'stop_loss': signal_data['stop_loss'],
            'take_profit': signal_data['take_profit']
        }
        save_to_dashboard(analysis_data)
        
        # 保存持仓信息
        position_data = {
            'timestamp': datetime.now().isoformat(),
            'symbol': config.symbol,
            'side': trading_record['current_position'].get('side', 'none'),
            'size': trading_record['current_position'].get('size', 0),
            'entry_price': trading_record['current_position'].get('entry_price', 0),
            'current_price': price_data['price'],
            'unrealized_pnl': trading_record['current_position'].get('unrealized_pnl', 0),
            'leverage': config.leverage,
            'exchange': trading_record['exchange'],
            'status': trading_record['current_position'].get('status', 'UNKNOWN')
        }
        save_position_info(position_data)
        
        # 保存账户信息
        account_data = {
            'timestamp': datetime.now().isoformat(),
            'total_balance': 10000,  # 默认余额，实际应该从交易所获取
            'available_balance': 10000 - (config.amount * price_data['price']),
            'unrealized_pnl': trading_record['current_position'].get('unrealized_pnl', 0),
            'margin_balance': config.amount * price_data['price'],
            'exchange': trading_record['exchange'],
            'symbol': config.symbol,
            'leverage': config.leverage
        }
        save_account_info(account_data)
        
        # 保存净值历史
        equity_data = {
            'timestamp': datetime.now().isoformat(),
            'equity': 10000 + trading_record['current_position'].get('unrealized_pnl', 0),
            'total_pnl': trading_record['current_position'].get('unrealized_pnl', 0),
            'daily_pnl': daily_loss
        }
        save_equity_history(equity_data)
        
        # 保存交易动作
        if signal_data['signal'] != 'HOLD':
            action_data = {
                'timestamp': datetime.now().isoformat(),
                'action_type': f"{signal_data['signal']}_ORDER",
                'symbol': config.symbol,
                'quantity': config.amount,
                'price': price_data['price'],
                'pnl': 0,
                'exchange': trading_record['exchange'],
                'signal': signal_data['signal'],
                'confidence': signal_data['confidence'],
                'is_simulated': not trading_record['real_trading'],
                'position_status': trading_record['current_position'].get('status', 'UNKNOWN'),
                'trading_mode': trading_record['mode']
            }
            save_to_dashboard(None, action_data)
        
        print("✅ 交易记录已保存到Dashboard")
        
    except Exception as e:
        print(f"❌ 交易记录保存失败: {e}")

def production_trading_bot():
    """生产环境主交易函数"""
    print("\n" + "=" * 60)
    print(f"🤖 生产环境交易机器人 - {config.get_trading_mode()}")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 交易所: {config.trading_exchange}")
    print(f"🎯 交易符号: {config.symbol}")
    print(f"📊 杠杆: {config.leverage}x | 数量: {config.amount} BTC")
    print("=" * 60)
    
    # 显示交易状态
    status = get_safe_trading_status()
    print(f"📋 交易状态: {status['mode']}")
    print(f"💸 真实交易: {'是' if status['real_trading'] else '否'}")
    print(f"📊 今日亏损: {status['daily_loss']:.2f}/{status['max_daily_loss']} USDT")
    print(f"🔢 今日交易: {status['daily_trade_count']} 次")
    
    if status['emergency_stop']:
        print(f"🚨 紧急停止: {status.get('reason', '未知原因')}")
        return
    
    # 获取市场数据
    price_data = get_btc_market_data()
    if not price_data:
        print("❌ 无法获取市场数据，跳过本轮")
        return
    
    print(f"💎 BTC价格: ${price_data['price']:,.2f} ({price_data['price_change']:+.2f}%)")
    
    # AI分析
    signal_data = analyze_with_deepseek(price_data)
    print(f"🧠 AI信号: {signal_data['signal']} | 信心: {signal_data['confidence']}")
    print(f"💭 理由: {signal_data['reason'][:100]}...")
    
    # 执行交易
    execute_production_trade(signal_data, price_data)
    
    print("✅ 本轮交易完成")

def main():
    """主函数"""
    print("🚀 生产环境AI交易机器人")
    print("=" * 50)
    
    # 配置验证
    try:
        print(f"交易模式: {config.get_trading_mode()}")
        print(f"交易所: {config.trading_exchange}")
        print(f"真实交易: {'是' if config.trading_enabled else '否'}")
        
        if config.production_mode:
            print("🚨 生产环境模式 - 请谨慎操作！")
            input("按Enter键确认开始生产交易...")
        else:
            print("🧪 测试/模拟模式")
        
    except Exception as e:
        print(f"❌ 配置错误: {e}")
        return
    
    # 主循环
    print("🔄 开始交易循环...")
    while True:
        try:
            production_trading_bot()
        except Exception as e:
            print(f"❌ 交易循环错误: {e}")
            import traceback
            traceback.print_exc()
        
        # 等待下一个周期（15分钟）
        time.sleep(900)  # 15分钟 = 900秒

if __name__ == "__main__":
    main()
