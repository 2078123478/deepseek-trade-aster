# 📦 升级指南 - v2.0.0 → v2.1.0

本指南帮助现有用户升级到最新版本 v2.1.0。

---

## 🚀 快速升级（Git用户）⭐ 推荐

如果你是通过 `git clone` 安装的：

```bash
# 1. 进入项目目录
cd deepseek-trade-aster

# 2. 停止正在运行的服务
# 按 Ctrl+C 停止 Dashboard 和交易机器人

# 3. 拉取最新代码
git pull origin main

# 4. 查看更新内容
git log --oneline -5

# 5. 更新依赖包
pip install -r requirements.txt

# 6. 运行检查（可选）
python check_dashboard_integration.py

# 7. 重启服务
python dashboard_app.py
```

**✅ 完成！** 你的Dashboard已升级到v2.1.0！

---

## 📥 手动升级（ZIP用户）

如果你之前是下载ZIP压缩包：

### 第1步：备份重要文件

**必须备份**：
```
📁 备份这些文件：
├── .env                    # 你的API密钥配置
├── dashboard.db            # 交易数据库
└── production_trading_bot.log  # 运行日志（可选）
```

**操作**：
```bash
# 创建备份文件夹
mkdir backup_v2.0.0

# 复制重要文件
copy .env backup_v2.0.0\
copy dashboard.db backup_v2.0.0\
copy production_trading_bot.log backup_v2.0.0\
```

### 第2步：下载新版本

1. 访问 [GitHub仓库](https://github.com/2078123478/deepseek-trade-aster)
2. 点击绿色的 **"Code"** 按钮
3. 选择 **"Download ZIP"**
4. 解压到新文件夹

### 第3步：恢复配置

```bash
# 将备份的文件复制回新目录
copy backup_v2.0.0\.env .
copy backup_v2.0.0\dashboard.db .
```

### 第4步：安装新依赖

```bash
# 安装更新的依赖
pip install -r requirements.txt
```

### 第5步：验证升级

```bash
# 运行检查脚本
python check_dashboard_integration.py

# 预期输出：✅ 28项测试全部通过
```

### 第6步：启动新版本

```bash
python dashboard_app.py
```

---

## 🆕 v2.1.0 新增功能

升级后你将获得：

### 1. 性能指标面板
打开 Dashboard，你会在顶部看到4个新的指标卡片：
- 📈 总收益率
- 🎯 胜率
- 💰 盈亏比  
- ⚠️ 最大回撤

### 2. 三图表系统
点击标签页可切换：
- 资产净值图
- 盈亏分析图
- 回撤分析图

### 3. 时间范围选择
右上角可选择：
- 6小时
- 24小时
- 7天
- 30天

### 4. 交互功能
- 鼠标滚轮：缩放
- 拖动：平移
- 工具栏：导出图片

---

## 🔍 验证升级成功

### 检查版本

访问 Dashboard 后检查：

1. **性能指标面板显示** ✅
   - 应该看到4个彩色指标卡片

2. **图表标签页** ✅
   - 应该看到3个可切换的标签

3. **时间范围选择器** ✅
   - 右上角应该有下拉菜单

4. **运行检查脚本** ✅
   ```bash
   python check_dashboard_integration.py
   ```
   应该显示：✅ 28项测试全部通过

---

## ⚠️ 常见问题

### Q1: 升级后Dashboard无法启动？

**原因**: 可能缺少新依赖

**解决**:
```bash
pip install plotly>=5.18.0
pip install flask>=3.0.0
pip install eventlet flask-socketio
```

### Q2: 性能指标显示"--"？

**原因**: 数据不足

**解决**: 
- 运行交易机器人生成数据
- 至少需要1笔交易记录
- 等待几分钟后自动显示

### Q3: 图表显示"暂无数据"？

**原因**: 
- 数据库为空
- 或选择的时间范围内无数据

**解决**:
1. 检查 `dashboard.db` 是否正确恢复
2. 选择较短的时间范围（6H或24H）
3. 运行交易机器人生成新数据

### Q4: Windows控制台乱码？

**原因**: UTF-8编码问题

**解决**: 已在v2.1.0中修复，重启Dashboard即可

### Q5: 升级后数据丢失？

**原因**: 忘记备份 `dashboard.db`

**解决**:
- 如果旧版本文件夹还在，复制过来
- 如果已删除，需要重新生成数据

---

## 🔄 回滚到旧版本

如果遇到问题想回到v2.0.0：

### Git用户：
```bash
git checkout v2.0.0
pip install -r requirements.txt
python dashboard_app.py
```

### ZIP用户：
恢复备份文件夹中的所有内容

---

## 📊 升级对比

| 项目 | v2.0.0 | v2.1.0 | 提升 |
|------|--------|--------|------|
| 性能指标 | 0个 | 4个 | +∞ |
| 图表数量 | 1个 | 3个 | +200% |
| 时间范围 | 固定 | 4个可选 | +300% |
| 专业度 | ⭐⭐ | ⭐⭐⭐⭐⭐ | +150% |

---

## 📚 更多资源

- [完整更新日志](CHANGELOG.md)
- [发布说明](RELEASE_NOTES_v2.1.0.md)
- [快速使用指南](DASHBOARD_QUICK_START.md)
- [优化对比](DASHBOARD_BEFORE_AFTER.md)

---

## 📞 需要帮助？

如果升级遇到问题：

1. **运行检查**: `python check_dashboard_integration.py`
2. **查看文档**: [DASHBOARD_QUICK_START.md](DASHBOARD_QUICK_START.md)
3. **提交Issue**: [GitHub Issues](https://github.com/2078123478/deepseek-trade-aster/issues)

---

## ✅ 升级完成清单

- [ ] 停止旧版本服务
- [ ] 备份 `.env` 和 `dashboard.db`
- [ ] 拉取/下载新版本代码
- [ ] 安装新依赖 `pip install -r requirements.txt`
- [ ] 恢复配置文件
- [ ] 运行检查脚本
- [ ] 启动新版本 Dashboard
- [ ] 验证新功能正常工作

---

**🎉 欢迎升级到 v2.1.0！享受专业级的Dashboard体验！**

