#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动查找账号的真实笔记
"""
import asyncio
from playwright.async_api import async_playwright
from xhs_searcher_cdp import XiaohongshuSearcherCDP
import json


async def find_user_notes(account_name, account_id):
    """查找账号发布的真实笔记"""
    print(f"\n🔍 正在查找账号: {account_name}")
    print(f"   ID: {account_id}")

    searcher = XiaohongshuSearcherCDP()
    try:
        if not await searcher.connect():
            return []

        # 导航到账号主页
        user_url = f"https://www.xiaohongshu.com/user/profile/{account_id}"
        print(f"   正在打开主页...")
        await searcher.page.goto(user_url, timeout=30000)
        await searcher.page.wait_for_timeout(3000)

        # 滚动加载笔记
        print(f"   正在加载笔记...")
        for i in range(3):
            await searcher.page.evaluate('window.scrollBy(0, 500)')
            await searcher.page.wait_for_timeout(1500)

        # 提取笔记链接
        notes_data = await searcher.page.evaluate("""() => {
            const results = [];
            const noteElements = document.querySelectorAll('a[href*="/explore/"]');

            noteElements.forEach((elem, index) => {
                if (index < 10) {  // 只取前10条
                    try {
                        const href = elem.getAttribute('href');
                        if (href && href.includes('/explore/')) {
                            const noteId = href.split('/explore/')[1].split('?')[0];

                            // 查找笔记标题
                            let title = '';
                            const titleSelectors = ['.title', '.note-title', '[class*="title"]'];
                            for (const selector of titleSelectors) {
                                const titleElem = elem.querySelector(selector);
                                if (titleElem) {
                                    title = titleElem.textContent || titleElem.innerText || '';
                                    break;
                                }
                            }

                            // 如果没找到标题，尝试从链接文本获取
                            if (!title) {
                                title = elem.textContent.trim().substring(0, 50);
                            }

                            results.push({
                                noteId: noteId,
                                title: title || '笔记',
                                href: href
                            });
                        }
                    } catch (e) {
                        // 忽略错误
                    }
                }
            });

            return results;
        }""")

        print(f"   ✅ 找到 {len(notes_data)} 条笔记")

        # 构建完整URL
        notes = []
        for note in notes_data:
            full_url = f"https://www.xiaohongshu.com{note['href']}"
            notes.append({
                'id': note['noteId'],
                'title': note['title'],
                'url': full_url
            })
            print(f"      - {note['title']}")

        return notes

    except Exception as e:
        print(f"   ❌ 查找失败: {e}")
        return []
    finally:
        await searcher.close()


async def main():
    """主函数"""
    # 读取监控账号
    with open('/Users/xiaoningli/xiaohongshu_automation/data/monitored_accounts.json', 'r', encoding='utf-8') as f:
        accounts = json.load(f)

    print("=" * 70)
    print("🔍 自动查找真实笔记")
    print("=" * 70)

    # 取前5个账号做测试
    test_accounts = list(accounts.items())[:5]

    all_notes = {}

    for account_name, account_info in test_accounts:
        account_id = account_info['id']
        category = account_info['category']

        # 查找笔记
        notes = await find_user_notes(account_name, account_id)

        if notes:
            all_notes[account_name] = {
                'id': account_id,
                'category': category,
                'notes': notes
            }

    # 保存结果
    with open('/Users/xiaoningli/xiaohongshu_automation/real_notes.json', 'w', encoding='utf-8') as f:
        json.dump(all_notes, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"✅ 完成！共找到 {len(all_notes)} 个账号的真实笔记")
    print("   已保存到: real_notes.json")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
