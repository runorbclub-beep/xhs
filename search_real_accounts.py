#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索真实的目标账号 - 严格验证笔记内容
"""
import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def search_and_verify(keyword, category, max_results=20):
    """搜索并严格验证账号"""
    print("=" * 70)
    print(f"🔍 搜索关键词: {keyword}")
    print(f"📂 目标分类: {category}")
    print("=" * 70)

    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

    try:
        contexts = browser.contexts
        context = contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        # 搜索账号
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51"
        print(f"\n正在搜索...")
        await page.goto(search_url, timeout=30000)
        await page.wait_for_timeout(3000)

        # 滚动加载更多
        for i in range(3):
            await page.evaluate('window.scrollBy(0, 500)')
            await page.wait_for_timeout(1500)

        # 提取用户链接
        users_data = await page.evaluate("""() => {
            const results = [];
            const linkElements = document.querySelectorAll('a[href*="/user/profile/"]');

            linkElements.forEach((link) => {
                try {
                    const href = link.getAttribute('href');
                    if (href && href.includes('/user/profile/')) {
                        const userId = href.split('/user/profile/')[1].split('?')[0];
                        let userName = link.textContent.trim().substring(0, 30);
                        results.push({
                            userId: userId,
                            userName: userName,
                            href: href
                        });
                    }
                } catch (e) {
                }
            });

            return results;
        }""")

        print(f"✅ 找到 {len(users_data)} 个用户链接")

        # 验证每个账号
        verified_accounts = []
        count = 0

        for user in users_data[:max_results]:
            user_id = user['userId']
            user_name = user['userName']

            count += 1
            print(f"\n[{count}/{len(users_data)}] 验证: {user_name}")

            # 访问账号主页验证内容
            is_valid, notes = await verify_single_account(browser, user_id, category)

            if is_valid:
                verified_accounts.append({
                    'name': user_name,
                    'id': user_id,
                    'category': category,
                    'notes': notes
                })
                print(f"   ✅ 确认为目标账号！")
            else:
                print(f"   ⚠️  跳过（不符合条件）")

        print("\n" + "=" * 70)
        print(f"✅ 搜索完成！")
        print(f"   搜索关键词: {keyword}")
        print(f"   找到用户: {len(users_data)} 个")
        print(f"   验证通过: {len(verified_accounts)} 个")
        print("=" * 70)

        return verified_accounts

    finally:
        await browser.close()


async def verify_single_account(browser, user_id, category):
    """验证单个账号"""
    try:
        contexts = browser.contexts
        context = contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        # 访问账号主页
        user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
        await page.goto(user_url, timeout=30000)
        await page.wait_for_timeout(2000)

        # 滚动加载笔记
        for i in range(3):
            await page.evaluate('window.scrollBy(0, 500)')
            await page.wait_for_timeout(1500)

        # 提取笔记内容
        notes_data = await page.evaluate("""() => {
            const results = [];
            const noteElements = document.querySelectorAll('a[href*="/explore/"]');

            noteElements.forEach((elem, index) => {
                if (index < 10) {
                    try {
                        const href = elem.getAttribute('href');
                        if (href && href.includes('/explore/')) {
                            let title = '';
                            let content = '';

                            const titleElem = elem.querySelector('[class*="title"]');
                            if (titleElem) {
                                title = titleElem.textContent || '';
                            }

                            const contentElem = elem.querySelector('[class*="content"], [class*="desc"]');
                            if (contentElem) {
                                content = contentElem.textContent || '';
                            }

                            if (!title && !content) {
                                const text = elem.textContent || '';
                                title = text.substring(0, 50);
                            }

                            results.push({
                                title: title,
                                content: content,
                                fullText: (title + ' ' + content).trim()
                            });
                        }
                    } catch (e) {
                    }
                }
            });

            return results;
        }""")

        if len(notes_data) == 0:
            return False, []

        # 分析内容相关性
        keywords = {
            '牙医': ['牙', '齿', '口腔', '诊所', '牙科', '洗牙', '补牙', '拔牙', '根管', '牙齿', '正畸', '种植'],
            '美容院': ['美容', '护肤', '美容院', '美业', '护理', '皮肤', '面膜', '美容店'],
            '按摩店': ['按摩', '推拿', '理疗', 'SPA', '足疗', '按摩店', '养生'],
            '养生馆': ['养生', '中医', '针灸', '艾灸', '调理', '养生馆', '健康'],
            '美甲店': ['美甲', '指甲', '美甲店', '美睫', '睫毛']
        }

        category_keywords = keywords.get(category, [])
        relevant_count = 0

        for note in notes_data:
            full_text = (note['title'] + ' ' + note['content']).lower()
            for keyword in category_keywords:
                if keyword in full_text:
                    relevant_count += 1
                    break

        ratio = relevant_count / len(notes_data) if notes_data else 0

        # 至少30%的笔记相关
        return ratio >= 0.3, notes_data[:3]

    except Exception as e:
        print(f"   验证失败: {e}")
        return False, []


async def main():
    """主函数"""
    # 定义更精确的搜索关键词
    search_tasks = [
        # 牙医相关
        ("牙医诊所", "牙医", 5),
        ("口腔诊所", "牙医", 5),
        ("牙科诊所", "牙医", 5),

        # 美容院相关
        ("美容院创业", "美容院", 5),
        ("美容院管理", "美容院", 5),

        # 养生馆相关
        ("养生馆经营", "养生馆", 5),
    ]

    all_verified = {}

    for keyword, category, max_results in search_tasks:
        print(f"\n\n{'='*70}")
        print(f"开始搜索: {keyword}")
        print(f"{'='*70}")

        verified = await search_and_verify(keyword, category, max_results)

        if verified:
            for acc in verified:
                all_verified[acc['name']] = acc

        # 休息一下，避免频繁请求
        await asyncio.sleep(2)

    # 保存结果
    with open('/Users/xiaoningli/xiaohongshu_automation/data/verified_real_accounts.json', 'w', encoding='utf-8') as f:
        json.dump(all_verified, f, ensure_ascii=False, indent=2)

    print(f"\n\n{'='*70}")
    print(f"🎉 全部搜索完成！")
    print(f"{'='*70}")
    print(f"\n共找到 {len(all_verified)} 个真实的目标账号")

    if all_verified:
        print("\n账号列表:")
        for i, (name, acc) in enumerate(all_verified.items(), 1):
            print(f"{i}. {name} ({acc['category']})")

        # 保存到监控列表
        with open('/Users/xiaoningli/xiaohongshu_automation/data/monitored_accounts.json', 'r', encoding='utf-8') as f:
            current_accounts = json.load(f)

        # 清空并更新
        for name, acc in all_verified.items():
            current_accounts[name] = {
                'id': acc['id'],
                'category': acc['category'],
                'added_date': datetime.now().strftime('%Y-%m-%d'),
                'last_check': None,
                'notes': []
            }

        with open('/Users/xiaoningli/xiaohongshu_automation/data/monitored_accounts.json', 'w', encoding='utf-8') as f:
            json.dump(current_accounts, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 已更新监控列表: monitored_accounts.json")
        print(f"   现在有 {len(current_accounts)} 个账号")

    print(f"\n详细数据已保存到: verified_real_accounts.json")


if __name__ == "__main__":
    asyncio.run(main())
