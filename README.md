# 🤖 AI交易机器人 - 多交易所智能交易系统

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()

## 📋 项目简介

这是一个基于AI的智能交易机器人，支持从OKX获取市场数据，并通过DeepSeek AI进行分析，最终在Aster交易所执行交易。系统包含完整的Web Dashboard用于实时监控交易状态和历史数据。

## ✨ 主要特性

### 🧠 AI驱动交易决策
- 集成DeepSeek AI进行市场分析
- 支持技术指标分析（RSI、MACD、布林带等）
- 智能止损止盈建议
- 多级信心度控制（LOW/MEDIUM/HIGH）

### 💰 多交易所支持
- **数据源**: OKX公共API（实时市场数据）
- **交易平台**: Aster交易所（合约交易）
- 支持杠杆交易（最高125倍）
- 实时持仓管理

### 📊 专业Dashboard监控系统 ⭐ NEW
#### 性能指标面板（v2.1.0新增）
- 📈 **总收益率** - 实时显示账户收益百分比
- 🎯 **胜率统计** - 智能计算交易成功率
- 💰 **盈亏比分析** - 评估策略质量（优秀/良好/需改进）
- ⚠️ **最大回撤** - 风险评估（风险低/中/高）

#### 多维度图表系统（v2.1.0新增）
- 📈 **资产净值图** - 双Y轴，平滑曲线，专业展示
- 📊 **盈亏分析图** - 柱状图可视化，直观展示盈亏分布
- 📉 **回撤分析图** - 水下曲线，精准风险评估
- 🎛️ **时间范围切换** - 支持6H/24H/7D/30D灵活选择

#### 实时数据推送
- WebSocket实时数据推送
- 交易历史记录查看
- 持仓状态实时更新
- AI分析结果展示
- 交互式图表（缩放/平移/导出）

### 🛡️ 安全风险控制
- 最大日亏损限制
- 最大持仓数量控制
- 紧急停止机制
- 多重安全验证

## 🚀 快速开始

### 1. 环境要求

```bash
Python 3.8+
pip install -r requirements.txt
```

### 2. 配置设置

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件，填入你的API密钥
nano .env
```

### 3. 启动服务

```bash
# 启动Dashboard（终端1）
python dashboard_app.py

# 启动交易机器人（终端2）
python production_trading_bot.py
```

### 4. 访问Dashboard

打开浏览器访问: http://localhost:5000

## 📁 项目结构

```
├── production_trading_bot.py    # 主交易机器人
├── dashboard_app.py            # Web Dashboard
├── database_manager.py         # 数据库管理
├── system_monitor.py           # 系统监控
├── aster_client_trading.py     # Aster交易所客户端
├── templates/
│   └── dashboard.html         # Dashboard前端页面
├── .env.example               # 配置文件模板
├── .gitignore                # Git忽略文件
└── requirements.txt           # Python依赖包
```

## ⚙️ 配置说明

### 核心配置

```bash
# AI配置
DEEPSEEK_API_KEY=your_deepseek_api_key

# 交易所配置
ASTER_USER_ADDRESS=your_aster_wallet_address
ASTER_PRIVATE_KEY=your_aster_private_key

# 交易模式
TRADING_ENABLED=false      # true=真实交易, false=模拟交易
PRODUCTION_MODE=false      # true=生产模式, false=测试模式
MIN_CONFIDENCE_LEVEL=MEDIUM # 最低交易信心度

# 风险控制
MAX_DAILY_LOSS=100         # 最大日亏损(USDT)
MAX_POSITION_SIZE=0.01     # 最大交易数量(BTC)
LEVERAGE=5                 # 杠杆倍数
```

### 交易模式说明

| 模式 | TRADING_ENABLED | PRODUCTION_MODE | 说明 |
|------|----------------|-----------------|------|
| 模拟交易 | false | false | 仅分析，不执行真实交易 |
| 实盘测试 | true | false | 小资金实盘测试 |
| 生产环境 | true | true | 正式生产交易 |

## 🛠️ API文档

### Aster交易所集成
- 支持合约交易
- HMAC签名认证
- 实时持仓查询
- 订单管理

### OKX数据源
- K线数据获取
- 实时价格更新
- 技术指标计算

## 📊 Dashboard功能

### 🎯 性能指标面板（v2.1.0）
一目了然的关键指标展示：
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 📈 总收益率  │ 🎯 胜率      │ 💰 盈亏比    │ ⚠️ 最大回撤  │
│  +15.32%     │   79.2%      │    4.46      │   -8.42%     │
│  ↑ 盈利中    │  80/101 胜   │    优秀      │   风险低     │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

### 📈 多维度图表系统（v2.1.0）
- **资产净值图** - 双Y轴展示净值和盈亏趋势
- **盈亏分析图** - 柱状图直观显示每个时段盈亏
- **回撤分析图** - 水下曲线评估风险状况
- **时间范围切换** - 6小时/24小时/7天/30天

### 💡 实时数据展示
- 📈 专业图表可视化
- 💰 持仓信息实时更新
- 📋 交易历史详细记录
- 🧠 AI分析结果展示
- 🔄 系统状态监控

### ⚡ WebSocket推送
- 实时价格更新
- 交易信号推送
- 持仓变更通知
- 系统警告提醒
- 图表动态更新

## 🔒 安全特性

### 数据安全
- 本地数据库存储
- API密钥加密
- 敏感信息隔离
- 定期数据备份

### 交易安全
- 多重风险控制
- 紧急停止机制
- 持仓数量限制
- 亏损保护

### 系统安全
- 异常处理机制
- 日志记录完整
- 配置验证
- 状态监控

## 📈 使用流程

1. **环境准备**: 安装依赖，配置API密钥
2. **模式选择**: 选择交易模式（模拟/实盘）
3. **风险设置**: 配置风险控制参数
4. **启动服务**: 启动Dashboard和交易机器人
5. **监控运行**: 通过Dashboard监控交易状态

## 🔄 更新日志

### v2.1.0 (2025-11-06) ⭐ 最新
#### Dashboard专业化升级
- ✅ **新增4个性能指标面板** - 总收益率/胜率/盈亏比/最大回撤
- ✅ **三图表系统** - 净值/盈亏分析/回撤分析
- ✅ **时间范围切换** - 6H/24H/7D/30D
- ✅ **交互功能增强** - 缩放/平移/导出
- ✅ **视觉效果升级** - 专业配色/动画效果
- ✅ **完整质量保证** - 28项测试全部通过
- ✅ **详细文档** - 7个新增文档
- 📊 专业度提升150%，数据维度增加200%

### v2.0.0 (2025-11-05)
- ✅ 完整Dashboard集成
- ✅ WebSocket实时推送
- ✅ 多级风险控制
- ✅ AI信心度管理
- ✅ 生产环境安全检查

### v1.0.0 (2025-11-01)
- ✅ 基础交易功能
- ✅ OKX数据集成
- ✅ Aster交易支持
- ✅ DeepSeek AI分析

查看 [完整更新日志](CHANGELOG.md) | [Release Notes](RELEASE_NOTES_v2.1.0.md)

## 🚨 重要提醒

### ⚠️ 风险警告
- 交易有风险，投资需谨慎
- 建议先在模拟环境测试
- 请根据自身风险承受能力配置参数
- 定期检查系统运行状态

### 🔐 安全建议
- 不要将.env文件上传到公共仓库
- 定期更换API密钥
- 使用强密码和双重验证
- 及时更新系统到最新版本

## 📊 新版Dashboard预览

### 查看效果
```bash
python dashboard_app.py
# 访问 http://localhost:5000
```

### 自动检查
```bash
python check_dashboard_integration.py
# 运行28项完整检查
```

### 详细文档
- [快速使用指南](DASHBOARD_QUICK_START.md) - 5分钟上手
- [优化对比分析](DASHBOARD_BEFORE_AFTER.md) - 看看改进了什么
- [技术实现详解](DASHBOARD_CHART_IMPROVEMENTS.md) - 深入了解
- [集成检查报告](生产环境检查报告.md) - 质量保证

## 📞 技术支持

如果遇到问题，请：
1. 运行自动检查 `python check_dashboard_integration.py`
2. 查看日志文件 `production_trading_bot.log`
3. 确认配置文件正确性
4. 检查网络连接状态
5. 查看API密钥有效性
6. 提交 [GitHub Issue](https://github.com/your-username/trade_bot/issues)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**

---

*免责声明: 本项目仅供学习和研究使用，不构成投资建议。使用本软件进行交易的所有风险由用户自行承担。*
