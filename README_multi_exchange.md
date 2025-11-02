# 多交易所交易机器人 🤖

基于DeepSeek AI的智能交易机器人，支持OKX和Aster交易所的混合交易模式。

## 功能特性 ✨

- **多交易所支持**: 支持OKX、Aster交易所，可配置混合模式
- **AI决策引擎**: 使用DeepSeek API进行市场分析和交易决策
- **技术指标丰富**: 包含移动平均线、MACD、RSI、布林带等完整技术指标
- **市场情绪集成**: 通过CryptoOracle API获取社区情绪数据
- **风险管理完善**: 包含止损止盈、仓位控制、防频繁交易机制
- **单向持仓模式**: 避免多空同时持仓的风险

## 交易所模式选择

### 1. OKX模式 (默认)
- 在OKX获取数据并在OKX交易
- 保持原有功能不变

### 2. Aster模式
- 在Aster获取数据并在Aster交易
- 使用Aster交易所的API

### 3. 混合模式 (推荐)
- **从OKX获取数据**：利用OKX丰富的市场数据
- **在Aster交易**：通过Aster交易所执行交易
- 结合两个交易所的优势

## 快速开始 🚀

### 1. 环境配置

```bash
# 复制环境配置文件
cp .env.example .env
```

编辑 `.env` 文件，配置以下参数：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=你的deepseek api密钥

# 交易所选择配置: OKX | ASTER | HYBRID
TRADING_EXCHANGE=HYBRID

# OKX交易所配置
OKX_API_KEY=你的okx api密钥
OKX_SECRET=你的okx secret
OKX_PASSWORD=你的okx交易密码

# Aster交易所配置
ASTER_USER_ADDRESS=你的主钱包地址
ASTER_SIGNER_ADDRESS=你的API钱包地址
ASTER_PRIVATE_KEY=你的私钥

# 交易参数配置
TRADING_SYMBOLS=BTCUSDT
TRADING_ENABLED=false  # 首次运行建议设为false进行测试
MAX_POSITION_SIZE=0.1
LEVERAGE=10
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行程序

```bash
# 运行多交易所版本
python deepseek_multi_exchange_带市场情绪+指标版本.py

# 或运行原版（仅OKX）
python deepseek_ok_带市场情绪+指标版本.py
```

## 系统架构 🏗️

```
数据源选择 → 技术指标分析 → DeepSeek AI决策 → 交易所选择执行
    ↓              ↓              ↓              ↓
  OKX/Aster     保持不变        保持不变       OKX/Aster
```

## 交易策略 📈

### 技术指标权重
- **趋势分析** (均线排列) > RSI > MACD > 布林带
- **价格突破** 关键支撑/阻力位是重要信号

### 风险管理
- **止损止盈**: 自动设置止损止盈价格
- **仓位控制**: 限制最大持仓数量
- **防频繁交易**: 避免频繁反转仓位
- **信心控制**: 低信心信号不执行

### 市场情绪辅助
- 情绪数据用于验证技术信号
- 情绪与技术同向 → 增强信号信心
- 情绪与技术背离 → 以技术分析为主

## 文件说明 📁

- `deepseek_multi_exchange_带市场情绪+指标版本.py` - 多交易所版本（推荐）
- `deepseek_ok_带市场情绪+指标版本.py` - 原版（仅OKX）
- `aster_client.py` - Aster交易所客户端
- `.env.example` - 环境配置示例

## 安全注意事项 ⚠️

1. **私钥安全**: 永远不要将私钥提交到版本控制系统
2. **测试环境**: 首次运行请在测试环境中进行
3. **交易开关**: 默认交易功能关闭，需要手动启用
4. **风险控制**: 设置合理的仓位限制和杠杆

## 故障排除 🔧

### 常见问题

1. **交易所连接失败**
   - 检查API密钥和密码配置
   - 确认网络连接正常

2. **DeepSeek API连接失败**
   - 检查API密钥是否正确
   - 确认API调用额度充足

3. **交易执行失败**
   - 检查账户余额是否充足
   - 确认交易对符号正确
   - 检查最小交易数量限制

## 开发指南 🛠️

### 添加新的交易所

1. 在 `aster_client.py` 基础上创建新的交易所客户端
2. 在配置文件中添加新的交易所选择
3. 在交易执行函数中添加新的交易所支持

### 扩展功能

- **新的数据源**: 添加新的市场数据获取方式
- **新的策略**: 修改DeepSeek提示词逻辑
- **新的监控指标**: 添加更多的技术指标分析

## 许可证 📄

本项目仅供学习和研究使用，请遵守相关法律法规。

---

**重要提示**: 加密货币交易具有高风险，请在充分了解风险的情况下使用本系统。建议先在测试环境中充分测试。
