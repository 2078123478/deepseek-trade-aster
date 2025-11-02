#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aster期货交易客户端
基于Aster交易所API v3
"""

import json
import math
import time
import requests
from eth_abi import encode
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class AsterFuturesClient:
    """Aster期货交易客户端"""
    
    def __init__(self, signature_method='hmac'):
        """
        初始化Aster期货客户端
        
        Args:
            signature_method: 签名方法，默认为'hmac'
        """
        self.signature_method = signature_method
        self.host = 'https://fapi.asterdex.com'
        
        # 从环境变量获取配置
        import os
        self.user = os.getenv('ASTER_USER_ADDRESS')
        self.signer = os.getenv('ASTER_SIGNER_ADDRESS')
        self.private_key = os.getenv('ASTER_PRIVATE_KEY')
        
        if not all([self.user, self.signer, self.private_key]):
            raise ValueError("Aster交易所配置不完整，请检查环境变量")
        
        # API密钥（可选）
        self.api_key = os.getenv('ASTER_API_KEY')
        self.secret_key = os.getenv('ASTER_SECRET_KEY')
        
        logger.info(f"Aster客户端初始化完成 - 用户: {self.user}")
    
    def _sign_request(self, params: Dict, nonce: int = None) -> Dict:
        """签名请求参数"""
        if nonce is None:
            nonce = math.trunc(time.time() * 1000000)
        
        # 过滤空值
        params = {key: value for key, value in params.items() if value is not None}
        params['recvWindow'] = 50000
        params['timestamp'] = int(round(time.time() * 1000))
        
        # 生成签名消息
        msg = self._trim_param(params, nonce)
        signable_message = encode_defunct(hexstr=msg)
        signed_message = Account.sign_message(signable_message=signable_message, private_key=self.private_key)
        
        # 添加签名信息
        params['nonce'] = nonce
        params['user'] = self.user
        params['signer'] = self.signer
        params['signature'] = '0x' + signed_message.signature.hex()
        
        return params
    
    def _trim_param(self, params: Dict, nonce: int) -> str:
        """处理参数并生成签名消息"""
        self._trim_dict(params)
        json_str = json.dumps(params, sort_keys=True).replace(' ', '').replace('\'', '\"')
        
        encoded = encode(['string', 'address', 'address', 'uint256'], 
                        [json_str, self.user, self.signer, nonce])
        keccak_hex = Web3.keccak(encoded).hex()
        
        return keccak_hex
    
    def _trim_dict(self, params: Dict) -> Dict:
        """递归处理字典参数"""
        for key in params:
            value = params[key]
            if isinstance(value, list):
                new_value = []
                for item in value:
                    if isinstance(item, dict):
                        new_value.append(json.dumps(self._trim_dict(item)))
                    else:
                        new_value.append(str(item))
                params[key] = json.dumps(new_value)
                continue
            if isinstance(value, dict):
                params[key] = json.dumps(self._trim_dict(value))
                continue
            params[key] = str(value)
        return params
    
    def _make_request(self, url: str, method: str, params: Dict = None) -> Dict:
        """发送HTTP请求"""
        full_url = self.host + url
        
        try:
            if method == 'GET':
                response = requests.get(full_url, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(full_url, data=params, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(full_url, data=params, timeout=30)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"响应解析失败: {e}")
            raise
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: float = None, **kwargs) -> Dict:
        """下单"""
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': str(quantity),
            'positionSide': kwargs.get('positionSide', 'BOTH'),
        }
        
        if order_type == 'LIMIT':
            if price is None:
                raise ValueError("限价单必须指定价格")
            params['price'] = str(price)
            params['timeInForce'] = kwargs.get('timeInForce', 'GTC')
        
        # 其他可选参数
        optional_params = ['reduceOnly', 'stopPrice', 'closePosition']
        for param in optional_params:
            if param in kwargs and kwargs[param] is not None:
                params[param] = kwargs[param]
        
        # 签名并发送请求
        signed_params = self._sign_request(params)
        
        logger.info(f"下单请求: {symbol} {side} {quantity} @ {price}")
        return self._make_request('/fapi/v3/order', 'POST', signed_params)
    
    def get_positions(self, symbol: str = None) -> List[Dict]:
        """获取持仓信息"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        # 签名并发送请求
        signed_params = self._sign_request(params)
        
        logger.info(f"获取持仓信息: {symbol or '全部'}")
        response = self._make_request('/fapi/v3/positionRisk', 'GET', signed_params)
        
        # 处理响应格式
        if isinstance(response, dict) and 'data' in response:
            return response['data']
        elif isinstance(response, list):
            return response
        else:
            return []
    
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        params = {}
        signed_params = self._sign_request(params)
        
        logger.info("获取账户信息")
        return self._make_request('/fapi/v3/account', 'GET', signed_params)
    
    def cancel_order(self, symbol: str, order_id: int = None, **kwargs) -> Dict:
        """取消订单"""
        params = {'symbol': symbol}
        
        if order_id:
            params['orderId'] = order_id
        
        # 其他可选参数
        optional_params = ['origClientOrderId']
        for param in optional_params:
            if param in kwargs and kwargs[param] is not None:
                params[param] = kwargs[param]
        
        signed_params = self._sign_request(params)
        
        logger.info(f"取消订单: {symbol} #{order_id}")
        return self._make_request('/fapi/v3/order', 'DELETE', signed_params)
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """获取当前挂单"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        signed_params = self._sign_request(params)
        
        logger.info(f"获取挂单: {symbol or '全部'}")
        response = self._make_request('/fapi/v3/openOrders', 'GET', signed_params)
        
        # 处理响应格式
        if isinstance(response, dict) and 'data' in response:
            return response['data']
        elif isinstance(response, list):
            return response
        else:
            return []
