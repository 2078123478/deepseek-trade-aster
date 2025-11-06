#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能数据源选择器
当OKX不可用时，自动切换到其他可用的数据源
"""

import ccxt
import requests
import time
from datetime import datetime
import pandas as pd
import json

class IntelligentDataSource:
    """智能数据源管理器"""
    
    def __init__(self):
        self.data_sources = [
            {
                'name': 'OKX',
                'exchange_id': 'okx',
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
                },
                'priority': 1,
                'available': False
            },
            {
                'name': 'Binance',
                'exchange_id': 'binance',
                'config': {
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
                    },
                },
                'priority': 2,
                'available': False
            },
            {
                'name': 'Huobi',
                'exchange_id': 'huobi',
                'config': {
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
                    },
                },
                'priority': 3,
                'available': False
            },
            {
                'name': 'Gate.io',
                'exchange_id': 'gate',
                'config': {
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
                    },
                },
                'priority': 4,
                'available': False
            }
        ]
        
        self.current_source = None
        self.last_check_time = 0
        self.check_interval = 300  # 5分钟检查一次
        
    def test_data_source(self, source):
        """测试数据源是否可用"""
        try:
            print(f"🔍 测试数据源: {source['name']}")
            
            # 创建交易所实例
            exchange_class = getattr(ccxt, source['exchange_id'])
            exchange = exchange_class(source['config'])
            
            # 测试获取服务器时间
            start_time = time.time()
            server_time = exchange.fetch_time()
            response_time = time.time() - start_time
            
            # 测试获取BTC价格
            ticker = exchange.fetch_ticker('BTC/USDT')
            
            print(f"✅ {source['name']} 可用！响应时间: {response_time:.2f}秒")
            print(f"💰 BTC价格: ${ticker['last']:,.2f}")
            
            return True, response_time, {
                'server_time': server_time,
                'ticker': ticker
            }
            
        except Exception as e:
            print(f"❌ {source['name']} 不可用: {e}")
            return False, 0, None
    
    def find_best_source(self):
        """找到最佳可用数据源"""
        print("🔍 搜索最佳数据源...")
        print("=" * 50)
        
        available_sources = []
        
        # 按优先级测试所有数据源
        for source in sorted(self.data_sources, key=lambda x: x['priority']):
            success, response_time, data = self.test_data_source(source)
            
            if success:
                source['available'] = True
                source['response_time'] = response_time
                source['last_test_time'] = time.time()
                available_sources.append(source)
            else:
                source['available'] = False
                source['last_test_time'] = time.time()
        
        if available_sources:
            # 选择响应时间最快的
            best_source = min(available_sources, key=lambda x: x['response_time'])
            print(f"\n🏆 选择最佳数据源: {best_source['name']}")
            print(f"⏱️ 响应时间: {best_source['response_time']:.2f}秒")
            print(f"📊 优先级: {best_source['priority']}")
            
            self.current_source = best_source
            return best_source
        else:
            print("\n❌ 所有数据源都不可用")
            self.current_source = None
            return None
    
    def get_current_data_source(self):
        """获取当前数据源"""
        current_time = time.time()
        
        # 如果没有当前源，或者需要重新检查
        if (not self.current_source or 
            current_time - self.last_check_time > self.check_interval or
            not self.current_source.get('available', False)):
            
            return self.find_best_source()
        
        return self.current_source
    
    def create_exchange_client(self):
        """创建交易所客户端"""
        source = self.get_current_data_source()
        
        if not source:
            raise Exception("没有可用的数据源")
        
        try:
            exchange_class = getattr(ccxt, source['exchange_id'])
            exchange = exchange_class(source['config'])
            
            print(f"📡 使用数据源: {source['name']}")
            return exchange, source['name']
            
        except Exception as e:
            print(f"❌ 创建交易所客户端失败: {e}")
            # 尝试下一个数据源
            self.current_source['available'] = False
            return self.create_exchange_client()
    
    def get_btc_market_data(self):
        """获取BTC市场数据"""
        max_retries = 2  # 减少重试次数，避免浪费时间
        
        for attempt in range(max_retries):
            try:
                exchange, source_name = self.create_exchange_client()
                
                print(f"📊 从 {source_name} 获取BTC市场数据...")
                
                # 获取K线数据
                ohlcv = exchange.fetch_ohlcv('BTC/USDT', '15m', limit=96)
                print(f"✅ 成功获取{len(ohlcv)}条K线数据")
                
                # 创建DataFrame
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                # 计算技术指标
                df = self.calculate_technical_indicators(df)
                
                current_data = df.iloc[-1]
                previous_data = df.iloc[-2]
                
                result = {
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
                    'data_source': source_name
                }
                
                print(f"🎯 数据来源: {source_name}")
                print(f"💎 BTC价格: ${result['price']:,.2f} ({result['price_change']:+.2f}%)")
                
                return result
                
            except Exception as e:
                print(f"❌ 第{attempt + 1}次尝试失败: {e}")
                if attempt < max_retries - 1:
                    print("⏳ 2秒后重试其他数据源...")
                    time.sleep(2)
                    # 标记当前源不可用
                    if self.current_source:
                        self.current_source['available'] = False
                    continue
                else:
                    print("❌ 所有数据源都失败")
                    return None
    
    def calculate_technical_indicators(self, df):
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
    
    def get_status_report(self):
        """获取数据源状态报告"""
        print("\n📊 数据源状态报告")
        print("=" * 50)
        
        for source in self.data_sources:
            status = "✅ 可用" if source.get('available', False) else "❌ 不可用"
            response_time = source.get('response_time', 0)
            last_test = source.get('last_test_time', 0)
            
            if last_test > 0:
                last_test_time = datetime.fromtimestamp(last_test).strftime('%H:%M:%S')
            else:
                last_test_time = "未测试"
            
            print(f"{source['name']:10} | {status:8} | 响应: {response_time:5.2f}s | 测试: {last_test_time}")
        
        print("=" * 50)
        if self.current_source:
            print(f"🎯 当前使用: {self.current_source['name']}")
        else:
            print("❌ 当前无可用数据源")

def test_intelligent_source():
    """测试智能数据源选择器"""
    print("🤖 智能数据源测试")
    print("=" * 50)
    
    # 创建智能数据源管理器
    data_manager = IntelligentDataSource()
    
    # 显示状态报告
    data_manager.get_status_report()
    
    # 测试获取数据
    print("\n📈 测试获取市场数据...")
    data = data_manager.get_btc_market_data()
    
    if data:
        print("\n🎉 数据获取成功！")
        print(f"📊 数据源: {data['data_source']}")
        print(f"💰 价格: ${data['price']:,.2f}")
        print(f"📈 变化: {data['price_change']:+.2f}%")
        print(f"🔍 RSI: {data['technical_data']['rsi']:.1f}")
        return True
    else:
        print("\n❌ 数据获取失败")
        return False

if __name__ == "__main__":
    test_intelligent_source()
