#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式账号浏览 - 自动复制ID到剪贴板
"""
import json
import subprocess
import sys
from pathlib import Path

# 评论建议库
COMMENTS = {
    '牙医': [
        '专业！这个科普很到位',
        '作为患者看完放心多了',
        '牙医确实需要耐心和细心',
        '真实案例很有参考价值',
        '我们诊所也遇到类似情况'
    ],
    '美容院': [
        '太实用了！我们店也在考虑这个问题',
        '做美容院确实不容易，感谢分享',
        '真实创业经历，比理论知识有用多了',
        '干货满满！已收藏，慢慢学习'
    ],
    '按摩店': [
        '专业分享，学到了！',
        '服务细节很重要，说得对',
        '顾客体验确实是第一位的'
    ],
    '养生馆': [
        '养生理念很棒！',
        '健康是最重要的，赞同',
        '专业分享，干货满满'
    ],
    '美甲店': [
        '技术很专业！',
        '审美在线，喜欢',
        '美业人都不容易，支持'
    ]
}

def copy_to_clipboard(text):
    """复制文本到剪贴板（macOS）"""
    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    process.communicate(text.encode('utf-8'))

def clear_screen():
    """清屏"""
    print('\n' * 100)

def main():
    """主函数"""
    # 读取监控账号
    accounts_file = Path(__file__).parent / "data" / "monitored_accounts.json"
    with open(accounts_file, 'r', encoding='utf-8') as f:
        accounts = json.load(f)

    print('=' * 70)
    print('🤖 小红书智能互动助手')
    print('=' * 70)
    print(f'\n监控账号总数: {len(accounts)} 个')
    print('\n使用说明:')
    print('1. 账号ID已自动复制到剪贴板 ✅')
    print('2. 在小红书搜索框粘贴（⌘+V 或 Ctrl+V）')
    print('3. 找到账号后查看笔记并点赞评论')
    print('4. 完成后按 Enter 继续')
    print('5. 输入 q 退出')
    print('=' * 70)

    input('\n按 Enter 开始...')

    index = 1
    completed = 0

    for account_name, account_info in accounts.items():
        account_id = account_info['id']
        category = account_info['category']

        # 清屏
        clear_screen()

        # 显示账号信息
        print('=' * 70)
        print(f'📌 账号 [{index}/{len(accounts)}]')
        print('=' * 70)
        print(f'\n账号名: {account_name}')
        print(f'账号ID: {account_id}')
        print(f'分类: {category}')
        print(f'\n✅ 账号ID已复制到剪贴板！')

        # 复制到剪贴板
        copy_to_clipboard(account_id)

        # 获取评论建议
        cat_comments = COMMENTS.get(category, COMMENTS['牙医'])
        comment = cat_comments[(index - 1) % len(cat_comments)]

        print(f'\n💬 建议评论: {comment}')
        print('\n' + '-' * 70)
        print('操作步骤:')
        print('1. 打开小红书搜索框')
        print('2. 粘贴账号ID（⌘+V 或 Ctrl+V）')
        print('3. 找到账号，查看笔记')
        print('4. 点赞❤️并评论💬')
        print('-' * 70)

        # 等待用户完成
        user_input = input('\n✅ 完成后按 Enter 继续，输入 q 退出: ').strip().lower()

        if user_input == 'q':
            print('\n👋 再见！')
            break

        completed += 1
        index += 1

    # 总结
    clear_screen()
    print('=' * 70)
    print('📊 互动总结')
    print('=' * 70)
    print(f'\n已完成: {completed} 个账号')
    print(f'总账号数: {len(accounts)} 个')
    print(f'完成度: {completed/len(accounts)*100:.1f}%')

    if completed == len(accounts):
        print('\n🎉 太棒了！所有账号已完成互动！')
    else:
        print(f'\n💪 还有 {len(accounts) - completed} 个账号待完成')

    print('=' * 70)
    print('\n按 Enter 退出...')
    input()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n⚠️  用户中断')
    except Exception as e:
        print(f'\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()
