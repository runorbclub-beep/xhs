#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩大范围搜索 - 寻找更多真实商家账号
"""
import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def search_and_verify(keyword, category, max_results=30):
    """搜索并验证账号 - 放宽验证标准"""
    print("=" * 70)
    print(f"🔍 搜索: {keyword}")
    print(f"分类: {category}")
    print("=" * 70)

    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

    try:
        contexts = browser.contexts
        context = contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        # 搜索
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51"
        await page.goto(search_url, timeout=30000)
        await page.wait_for_timeout(3000)

        # 滚动加载更多
        for i in range(5):
            await page.evaluate('window.scrollBy(0, 500)')
            await page.wait_for_timeout(1500)

        # 提取用户
        users_data = await page.evaluate("""() => {
            const results = [];
            const linkElements = document.querySelectorAll('a[href*="/user/profile/"]');

            linkElements.forEach((link) => {
                try {
                    const href = link.getAttribute('href');
                    if (href && href.includes('/user/profile/')) {
                        const userId = href.split('/user/profile/')[1].split('?')[0];
                        let userName = link.textContent.trim().substring(0, 40);
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

        print(f"✅ 找到 {len(users_data)} 个用户")

        # 验证账号 - 降低标准到20%
        verified = []
        for i, user in enumerate(users_data[:max_results], 1):
            if i % 10 == 0:
                print(f"   进度: {i}/{len(users_data)}")

            is_valid, notes = await verify_account(browser, user['userId'], category)
            if is_valid:
                verified.append({
                    'name': user['userName'],
                    'id': user['userId'],
                    'category': category,
                    'notes': notes
                })

        print(f"\n✅ 验证通过: {len(verified)}/{len(users_data[:max_results])}")

        return verified

    finally:
        await browser.close()


async def verify_account(browser, user_id, category):
    """验证账号 - 放宽标准"""
    try:
        contexts = browser.contexts
        context = contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
        await page.goto(user_url, timeout=30000)
        await page.wait_for_timeout(2000)

        # 滚动加载
        for i in range(3):
            await page.evaluate('window.scrollBy(0, 500)')
            await page.wait_for_timeout(1500)

        # 提取笔记
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

        # 放宽的关键词匹配
        keywords = {
            '牙医': ['牙', '齿', '口腔', '诊所', '牙科', '洗牙', '补牙', '医生', '治疗', '种植', '正畸', '根管', '牙齿', '美白', '护理'],
            '美容院': ['美容', '护肤', '美容院', '美业', '护理', '皮肤', '面膜', '美容店', '美甲', '美容师', '美容', '项目', '店'],
            '按摩店': ['按摩', '推拿', '理疗', 'SPA', '足疗', '按摩店', '养生', '放松', '身体', '精油', '服务'],
            '养生馆': ['养生', '中医', '针灸', '艾灸', '调理', '健康', '滋补', '食疗', '养生馆', '理疗', '保健'],
            '美甲店': ['美甲', '指甲', '美甲店', '美睫', '睫毛', '美业', '美甲师', '款式', '指甲艺术'],
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

        # 降低标准到20%
        return ratio >= 0.2, notes_data[:3]

    except Exception as e:
        return False, []


async def main():
    """主函数 - 扩大搜索范围"""
    print("=" * 70)
    print("🔍 扩大范围搜索 - 放宽验证标准")
    print("=" * 70)
    print("\n验证标准: 从30%降低到20%")
    print("搜索范围: 扩展到更多关键词")
    print("-" * 70)

    # 扩展的搜索关键词
    search_tasks = [
        # 牙医相关
        ("牙科", "牙医", 30),
        ("牙齿", "牙医", 30),
        ("洗牙", "牙医", 30),
        ("口腔医院", "牙医", 30),
        ("牙齿矫正", "牙医", 30),
        ("种植牙", "牙医", 30),

        # 美容院相关
        ("美容护肤", "美容院", 30),
        ("美容店", "美容院", 30),
        ("美容师", "美容院", 30),
        ("皮肤管理", "美容院", 30),
        ("美甲", "美甲店", 30),

        # 按摩养生相关
        ("中医推拿", "养生馆", 30),
        ("理疗", "按摩店", 30),
        ("足疗", "按摩店", 30),
        ("艾灸", "养生馆", 30),
        ("针灸", "养生馆", 30),

        # 综合类
        ("健康养生", "养生馆", 30),
        ("美业", "美容院", 30),
    ]

    all_verified = {}

    for keyword, category, max_results in search_tasks:
        print(f"\n\n{'='*70}")
        print(f"搜索: {keyword}")
        print(f"{'='*70}")

        try:
            verified = await search_and_verify(keyword, category, max_results)

            if verified:
                for acc in verified:
                    # 避免重复
                    if acc['id'] not in [a['id'] for a in all_verified.values()]:
                        all_verified[acc['name']] = acc

            await asyncio.sleep(2)  # 休息

        except Exception as e:
            print(f"搜索失败: {e}")
            continue

    print(f"\n\n{'='*70}")
    print(f"🎉 搜索完成！")
    print(f"{'='*70}")
    print(f"\n共找到 {len(all_verified)} 个真实账号")

    if all_verified:
        # 按分类统计
        categories = {}
        for name, acc in all_verified.items():
            cat = acc['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(name)

        print("\n📊 分类统计:")
        for cat, names in categories.items():
            print(f"  {cat}: {len(names)} 个")

        print("\n✅ 账号列表:")
        for i, (name, acc) in enumerate(all_verified.items(), 1):
            print(f"{i}. {name} ({acc['category']})")

        # 保存
        with open('/Users/xiaoningli/xiaohongshu_automation/data/verified_comprehensive.json', 'w', encoding='utf-8') as f:
            json.dump(all_verified, f, ensure_ascii=False, indent=2)

        # 更新监控列表 - 保留已有的
        try:
            with open('/Users/xiaoningli/xiaohongshu_automation/data/monitored_accounts.json', 'r', encoding='utf-8') as f:
                current_accounts = json.load(f)
        except:
            current_accounts = {}

        # 添加新账号
        for name, acc in all_verified.items():
            if name not in current_accounts:
                current_accounts[name] = {
                    'id': acc['id'],
                    'category': acc['category'],
                    'added_date': datetime.now().strftime('%Y-%m-%d'),
                    'last_check': None,
                    'notes': []
                }

        with open('/Users/xiaoningli/xiaohongshu_automation/data/monitored_accounts.json', 'w', encoding='utf-8') as f:
            json.dump(current_accounts, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 已更新监控列表")
        print(f"   总账号数: {len(current_accounts)}")
        print(f"   新增: {len(all_verified)} 个")

    else:
        print("\n⚠️  未找到符合条件的账号")


if __name__ == "__main__":
    asyncio.run(main())
