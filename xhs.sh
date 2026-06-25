#!/bin/bash
# 小红书智能社交助手 - 通用快捷启动脚本
#
# 使用方法：
#   ./xhs.sh --start-session    # 启动交互式浏览会话
#   ./xhs.sh --search "关键词"   # 搜索账号
#   ./xhs.sh --report           # 生成报告
#   ./xhs.sh --list             # 查看监控列表

cd /Users/xiaoningli/xiaohongshu_automation
python3 smart_social_assistant.py "$@"
