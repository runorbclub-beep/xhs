#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全自动化浏览 - 机器人自动打开账号主页
"""
import asyncio
from playwright.async_api import async_playwright
import json
import subprocess
from datetime import datetime


# 评论建议库
COMMENTS = {
    '牙医': [
        '专业！这个科普很到位',
        '作为患者看完放心多了',
        '牙医确实需要耐心和细心',
        '真实案例很有参考价值',
        '我们诊所也遇到类似情况'
    ],
    '摄影服务': [
        '摄影技术很专业！',
        '审美在线，喜欢你的作品',
        '照片质感很好',
        '构图很有想法',
        '期待看到更多作品'
    ],
    '汽车服务': [
        '维修很专业',
        '服务态度很好',
        '价格实惠',
        '技术过硬',
        '值得推荐'
    ],
    '宠物服务': [
        '对宠物真有爱心',
        '服务很贴心',
        '环境很干净',
        '专业负责',
        '毛孩子很喜欢'
    ],
    '场地租赁': [
        '场地环境很好',
        '地理位置方便',
        '设施齐全',
        '价格合理',
        '会考虑预订'
    ],
    '通用': [
        '内容很实用！',
        '学到了很多',
        '感谢分享',
        '很有启发',
        '支持一下'
    ]
}


def copy_to_clipboard(text):
    """复制文本到剪贴板（macOS）"""
    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    process.communicate(text.encode('utf-8'))


def clear_screen():
    """清屏"""
    print('\n' * 100)


async def auto_browse_session():
    """完全自动化浏览会话"""
    # 读取监控账号
    with open('/Users/xiaoningli/xiaohongshu_automation/data/monitored_accounts.json', 'r', encoding='utf-8') as f:
        accounts = json.load(f)

    clear_screen()
    print('=' * 70)
    print('🤖 自动化浏览会话 - 完全自动模式')
    print('=' * 70)
    print(f'\n监控账号总数: {len(accounts)} 个')
    print('\n工作流程:')
    print('1. 机器人自动打开账号主页')
    print('2. 你查看笔记、点赞、评论')
    print('3. 你按Enter键')
    print('4. 机器人自动打开下一个账号主页')
    print('=' * 70)

    input('\n⏸️  准备好后按 Enter 开始...')

    # 连接浏览器
    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

    try:
        contexts = browser.contexts
        context = contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        completed = 0
        failed = []
        skipped = []

        for index, (account_name, account_info) in enumerate(accounts.items(), 1):
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

            # 复制账号ID到剪贴板（备用）
            copy_to_clipboard(account_id)
            print(f'\n✅ 账号ID已复制到剪贴板（备用）')

            # 获取评论建议
            cat_comments = COMMENTS.get(category, COMMENTS['通用'])
            comment = cat_comments[(index - 1) % len(cat_comments)]
            print(f'\n💬 建议评论: {comment}')

            print('\n' + '-' * 70)
            print('🌐 正在打开账号主页...')
            print('-' * 70)

            # 自动打开账号主页，带错误处理
            try:
                user_url = f"https://www.xiaohongshu.com/user/profile/{account_id}"
                await page.goto(user_url, timeout=30000)
                await page.wait_for_timeout(3000)

                print('✅ 账号主页已打开！')
                print('\n' + '-' * 70)
                print('⏸️  请操作:')
                print('1. 查看账号的笔记')
                print('2. 点赞❤️')
                print('3. 发表评论💬')
                print('4. 完成后按 Enter 继续')
                print('输入 "s" 或 "skip" 跳过此账号')
                print('输入 "q" 或 "quit" 退出')
                print('-' * 70)

                # 等待用户完成
                user_input = input('\n✅ 完成后按 Enter 继续: ').strip().lower()

                if user_input in ['q', 'quit']:
                    print('\n👋 会话已结束')
                    break
                elif user_input in ['s', 'skip']:
                    print('⏭️  已跳过此账号')
                    skipped.append(account_name)
                    continue

                completed += 1

            except Exception as e:
                print(f'\n⚠️  打开账号失败: {e}')
                print(f'   可能原因: 账号不存在/被封禁/网络问题')

                user_input = input('\n按 Enter 跳过此账号继续，输入 q 退出: ').strip().lower()

                failed.append(account_name)

                if user_input == 'q':
                    print('\n👋 会话已结束')
                    break

                # 继续下一个账号
                continue

        # 总结
        clear_screen()
        print('=' * 70)
        print('📊 互动总结')
        print('=' * 70)
        print(f'\n✅ 已完成互动: {completed} 个账号')

        if failed:
            print(f'⚠️  打开失败: {len(failed)} 个账号')
            print('   失败账号:')
            for name in failed:
                print(f'     - {name}')

        if skipped:
            print(f'⏭️  跳过: {len(skipped)} 个账号')

        print(f'\n📈 总进度: {completed}/{len(accounts)} ({completed/len(accounts)*100:.1f}%)')

        if completed == len(accounts):
            print('\n🎉 太棒了！所有账号已完成互动！')
        elif completed > 0:
            print(f'\n💪 做得好！已完成 {completed} 个账号')
            print(f'   还有 {len(accounts) - completed - len(failed)} 个账号待完成')
        else:
            print('\n💡 提示: 可以稍后再继续完成剩余账号')

        print('=' * 70)
        print('\n按 Enter 退出...')
        input()

    finally:
        await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(auto_browse_session())
    except KeyboardInterrupt:
        print('\n\n⚠️  用户中断')
    except Exception as e:
        print(f'\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()
