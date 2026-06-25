# 小红书智能社交助手

## 🎯 项目简介

**小红书智能社交助手** 是一个基于人机协作模式的社交互动工具，专门为小微企业主（美容院、牙医诊所、按摩店、养生馆等）设计，帮助他们在小红书等社交平台上建立关系网络，最终推广"霸族预约助手"微信小程序。

### 核心理念

- **机器人负责**: 搜索账号、监控内容、生成建议、跟踪进度
- **人类负责**: 查看内容、亲自互动、建立关系、推广产品
- **完全安全**: 机器人不进行任何平台操作，避免被封号

---

## ✨ 主要功能

### 1. 智能账号搜索
- 按关键词搜索相关账号（牙医、美容院、养生馆等）
- 按粉丝数筛选（20-100人的小店）
- 自动添加到监控列表
- 支持多平台扩展

### 2. 内容监控
- 自动跟踪监控账号的新作品
- 智能生成评论建议
- 每日生成互动报告
- 支持手动添加笔记

### 3. 交互式浏览会话
- **核心功能**: 机器人自动打开浏览器，逐个导航到笔记页面
- 您查看内容并亲自点赞/评论
- 按Enter键自动跳转到下一个
- 自动标记已完成互动
- 完全的人机协作体验

### 4. 关系管理
- 跟踪所有互动历史
- 生成每日报告
- 统计互动效果
- 支持多账号分类管理

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Chrome浏览器（需要启用远程调试）
- 稳定的网络连接

### 安装依赖

```bash
pip3 install playwright
playwright install chromium
```

### 启动Chrome远程调试

**macOS**:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

**Windows**:
```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

**Linux**:
```bash
google-chrome --remote-debugging-port=9222
```

### 基本使用

#### 1. 搜索账号

```bash
# 搜索牙医账号（粉丝20-100人），自动添加
python3 smart_social_assistant.py --search "牙医" --min-followers 20 --max-followers 100 --auto-add
```

#### 2. 查看监控列表

```bash
python3 smart_social_assistant.py --list
```

#### 3. 添加笔记

```bash
python3 smart_social_assistant.py --add-note "账号名,笔记ID,笔记标题,笔记URL"
```

#### 4. 启动交互式浏览会话 ⭐

```bash
python3 smart_social_assistant.py --start-session
```

**这是核心功能！** 机器人会：
- 自动打开浏览器
- 逐个导航到待互动的笔记
- 显示评论建议
- 等待您完成互动后，按Enter自动跳转到下一个

#### 5. 生成每日报告

```bash
python3 smart_social_assistant.py --report
```

---

## 📖 详细使用指南

- **智能社交助手使用指南.md**: 完整功能说明
- **交互式浏览使用指南.md**: 交互式会话详细教程

---

## 🎯 使用场景

### 目标用户

- 美容院老板
- 牙医诊所
- 按摩店店主
- 养生馆经营者
- 美甲店老板
- 其他需要预约管理的专家小店

### 推广策略

**阶段1：建立联系（1-2周）**
- 搜索相关账号
- 每天互动5-10条笔记
- 提供有价值的评论

**阶段2：建立关系（3-4周）**
- 关注优质账号
- 等待回关
- 私信建立联系

**阶段3：推广产品（5周+）**
- 介绍"霸族预约助手"
- 强调价值：减少混乱、提升体验、免费使用
- 建立信任后推荐

---

## 📁 项目结构

```
xiaohongshu_automation/
├── smart_social_assistant.py    # 主程序
├── xhs_searcher_cdp.py          # 搜索器（CDP模式）
├── extract_users_js.py          # JavaScript提取器
├── data/                        # 数据目录
│   └── monitored_accounts.json  # 监控账号数据
├── reports/                     # 报告目录
├── .gitignore                   # Git忽略文件
├── README.md                    # 本文件
├── 智能社交助手使用指南.md      # 完整使用指南
└── 交互式浏览使用指南.md        # 交互会话教程
```

---

## 🔧 命令参考

```bash
# 查看帮助
python3 smart_social_assistant.py --help

# 搜索账号
python3 smart_social_assistant.py --search "关键词" --auto-add

# 添加账号
python3 smart_social_assistant.py --add-account "账号名,账号ID,分类"

# 添加笔记
python3 smart_social_assistant.py --add-note "账号名,笔记ID,标题,URL"

# 列出账号
python3 smart_social_assistant.py --list

# 标记互动
python3 smart_social_assistant.py --mark "账号名,笔记ID,互动类型"

# 生成报告
python3 smart_social_assistant.py --report

# 交互模式
python3 smart_social_assistant.py --interactive

# 启动浏览会话 ⭐
python3 smart_social_assistant.py --start-session
```

---

## 💡 核心优势

### ✅ 安全性
- 机器人不进行任何平台操作
- 完全由人类亲自互动
- 避免被封号风险

### ✅ 高效性
- 自动搜索和筛选
- 自动导航和跟踪
- 智能评论建议

### ✅ 真实性
- 真人查看和互动
- 真实的评论内容
- 建立真实的关系

### ✅ 可扩展
- 支持多平台（小红书、抖音、快手等）
- 模块化设计
- 易于添加新功能

---

## 🛠️ 技术栈

- **Python 3.8+**: 主要编程语言
- **Playwright**: 浏览器自动化
- **CDP (Chrome DevTools Protocol)**: 连接现有浏览器
- **JavaScript注入**: 动态内容提取

---

## 📊 工作流程

```
1. 搜索账号 → 添加到监控列表
              ↓
2. 监控内容 → 发现新笔记 → 生成评论建议
              ↓
3. 启动会话 → 逐个浏览 → 亲自互动 → 按Enter继续
              ↓
4. 建立关系 → 相互关注 → 私信推广
              ↓
5. 推广产品 → 介绍预约系统 → 免费试用
```

---

## 🎯 推广话术示例

### 建立联系阶段
- "专业！这个科普很到位"
- "真实创业经历，比理论知识有用多了"
- "干货满满！已收藏，慢慢学习"

### 私信推广阶段
```
您好！一直关注您的分享，很有价值。

我这边有个免费的预约管理系统，专门为小店设计：
- 减少预约混乱
- 提升客户体验
- 自动提醒服务
- 完全免费使用

有兴趣试试吗？可以看看效果再决定。
```

---

## 📝 更新日志

### v1.0.0 (2026-06-25)
- ✅ 初始版本发布
- ✅ 账号搜索功能
- ✅ 内容监控功能
- ✅ 交互式浏览会话
- ✅ 每日报告生成
- ✅ 支持104个账号监控

---

## 🤝 贡献指南

这是一个持续更新的项目，欢迎：

1. 报告Bug
2. 提出新功能建议
3. 提交代码改进
4. 分享使用经验

---

## 📞 联系方式

- GitHub: https://github.com/runorbclub-beep/xhs
- 项目维护: RunOrb Club

---

## ⚠️ 免责声明

本工具仅供学习和研究使用。使用时请遵守：
1. 小红书平台规则
2. 相关法律法规
3. 商业道德规范

建议：
- 真诚互动，不要 spam
- 提供有价值的内容
- 建立真实的信任关系

---

## 🎉 开始使用

现在就开始：

```bash
# 1. 搜索你的第一批账号
python3 smart_social_assistant.py --search "牙医" --auto-add

# 2. 启动交互式浏览会话
python3 smart_social_assistant.py --start-session

# 3. 开始建立关系，推广你的产品！
```

**祝您推广成功！** 🚀
