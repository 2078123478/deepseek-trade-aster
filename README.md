# 🤖 AI交易机器人 - 多交易所智能交易系统

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 📋 项目简介

这是一个基于AI的智能交易机器人系统，支持多交易所交易，具有实时Dashboard监控功能。系统使用DeepSeek AI进行市场分析，从OKX获取数据，在Aster交易所执行交易。

## ✨ 主要特性

### 🧠 AI驱动交易
- **DeepSeek AI分析**: 使用先进的AI模型进行市场分析和交易决策
- **技术指标集成**: RSI、MACD、布林带等多种技术指标
- **智能信号生成**: 基于AI分析生成BUY/SELL/HOLD信号
- **风险评估**: 自动计算止损止盈价格

### 💰 多交易所支持
- **OKX**: 作为市场数据源
- **Aster**: 作为交易执行平台
- **统一接口**: 简化多交易所操作

### 📊 实时Dashboard
- **WebSocket实时推送**: 交易信号、持仓变化实时更新
- **可视化图表**: 净值曲线、技术指标图表
- **交易历史**: 完整的交易记录和性能分析
- **系统监控**: API状态、系统健康度监控

### 🔒 安全特性
- **生产环境安全**: 多层安全检查和风险控制
- **配置验证**: 自动验证交易配置的安全性
- **紧急停止**: 自动风险控制和紧急停止机制
- **数据加密**: 敏感信息加密存储

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/huojichuanqi/ds.git
cd ds

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

复制环境变量模板并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：

```env
# DeepSeek AI
DEEPSEEK_API_KEY=your_deepseek_api_key

# Aster交易所配置
ASTER_USER_ADDRESS=your_aster_user_address
ASTER_SIGNER_ADDRESS=your_aster_signer_address
ASTER_PRIVATE_KEY=your_aster_private_key
ASTER_SIGNATURE_METHOD=hmac

# 交易配置
TRADING_EXCHANGE=ASTER
TRADING_ENABLED=true
PRODUCTION_MODE=false
MAX_POSITION_SIZE=0.01
LEVERAGE=5
MAX_DAILY_LOSS=100

# 其他配置
MIN_CONFIDENCE_LEVEL=MEDIUM
ENABLE_EMERGENCY_STOP=true
```

### 3. 启动系统

#### 方式一：快速启动
```bash
python quick_start.py
```

#### 方式二：分别启动
```bash
# 启动Dashboard (终端1)
python dashboard_app.py

# 启动交易机器人 (终端2)
python production_trading_bot.py
```

### 4. 访问Dashboard

打开浏览器访问：http://localhost:5000

## 📁 项目结构

```
├── README.md                    # 项目说明
├── requirements.txt             # Python依赖
├── .env.example                 # 环境变量模板
├── .gitignore                   # Git忽略文件
├── production_trading_bot.py    # 生产环境交易机器人
├── dashboard_app.py             # Dashboard应用
├── database_manager.py          # 数据库管理
├── system_monitor.py            # 系统监控
├── aster_client_trading.py      # Aster交易客户端
├── quick_start.py              # 快速启动脚本
├── templates/                  # HTML模板
│   └── dashboard.html          # Dashboard页面
├── api-docs/                   # API文档
└── nofx/                       # Go语言版本(可选)
```

## 🔧 配置说明

### 交易模式

1. **模拟模式 (SIMULATION)**
   - 不执行真实交易
   - 仅记录交易决策
   - 适合测试和学习

2. **实盘模式 (LIVE_TRADING)**
   - 执行真实交易
   - 需要配置交易所API
   - 具有风险控制机制

3. **生产模式 (PRODUCTION)**
   - 严格的安全检查
   - 完整的风险控制
   - 适合生产环境

### 风险控制

- **最大日亏损限制**: 自动停止当日交易
- **最大持仓数量**: 限制同时持仓数量
- **最低信心度要求**: 只执行高信心度交易
- **紧急停止机制**: 异常情况下自动停止

## 📊 Dashboard功能

### 实时监控
- 💰 账户余额和可用余额
- 📈 当前持仓和盈亏
- 📊 净值历史曲线
- 🎯 AI交易信号

### 交易记录
- 📋 完整交易历史
- 💸 盈亏统计
- 📈 成功率分析
- ⏰ 交易时间记录

### 系统状态
- 🔄 API连接状态
- 💾 系统资源使用
- 📡 WebSocket连接状态
- 🛡️ 安全检查结果

## 🛠️ API文档

详细的API文档请参考 `api-docs/` 目录：

- [Aster期货API V3](api-docs/aster-finance-futures-api-v3_CN.md)
- [Aster现货API](api-docs/aster-finance-spot-api_CN.md)
- [API集成指南](api-docs/README.md)

## 📈 性能监控

系统包含完整的性能监控：

- **交易性能**: 胜率、盈亏比、最大回撤
- **系统性能**: API响应时间、内存使用、错误率
- **AI性能**: 信号准确率、决策分析

## 🔒 安全审计

项目通过了完整的安全审计：

- ✅ API密钥安全存储
- ✅ 输入验证和清理
- ✅ 错误处理和日志记录
- ✅ 访问控制和权限管理

详细报告请参考 [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)

## 🚀 部署指南

### 开发环境
```bash
python quick_start.py
```

### 生产环境
详细的生产环境部署指南请参考 [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)

### Docker部署
```bash
# 构建镜像
docker build -t ai-trading-bot .

# 运行容器
docker run -d --name trading-bot -p 5000:5000 ai-trading-bot
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v2.0.0 (最新)
- ✨ 新增Aster交易所支持
- 🎯 集成DeepSeek AI分析
- 📊 完整的Dashboard系统
- 🔒 增强的安全机制
- 🛠️ 重构代码架构

### v1.0.0
- 🎉 初始版本发布
- 📈 基础交易功能
- 📊 简单的数据记录

## ⚠️ 免责声明

**重要提示**: 本项目仅供学习和研究使用。数字货币交易具有高风险，可能导致资金损失。使用本系统进行实际交易的风险由用户自行承担。开发者不对任何交易损失承担责任。

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 📞 联系方式

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/huojichuanqi/ds/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/huojichuanqi/ds/discussions)

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！
