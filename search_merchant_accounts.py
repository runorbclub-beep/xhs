#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用小红书商户搜索功能 - 寻找真实的商家账号
"""
import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def search_merchants(keyword, category, max_results=20):
    """搜索小红书商户"""
    print("=" * 70)
    print(f"🔍 商户搜索模式")
    print(f"关键词: {keyword}")
    print(f"分类: {category}")
    print("=" * 70)

    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

    try:
        contexts = browser.contexts
        context = contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        # 小红书商户搜索 - 使用type=51参数（用户/商户）
        # 或者尝试不同的搜索类型
        search_types = [
            f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51",  # 用户搜索
            f"https://www.xiaohongshu.com/search_result?keyword={keyword}",  # 综合搜索
        ]

        merchants_found = []

        for search_url in search_types:
            print(f"\n尝试搜索: {search_url}")
            await page.goto(search_url, timeout=30000)
            await page.wait_for_timeout(3000)

            # 尝试切换到商户/用户标签
            try:
                # 查找可能的商户标签按钮
                tab_selectors = [
                    'text=商户',
                    'text=店铺',
                    'text=品牌',
                    'text=用户',
                    '[data-tab="merchant"]',
                    '[data-type="merchant"]',
                ]

                for selector in tab_selectors:
                    try:
                        tab = await page.query_selector(selector)
                        if tab:
                            print(f"   找到标签: {selector}")
                            await tab.click()
                            await page.wait_for_timeout(2000)
                            break
                    except:
                        continue
            except:
                pass

            # 滚动加载
            for i in range(3):
                await page.evaluate('window.scrollBy(0, 500)')
                await page.wait_for_timeout(1500)

            # 保存页面HTML用于分析
            content = await page.content()
            with open(f'/Users/xiaoningli/xiaohongshu_automation/merchant_search_{keyword}.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   页面已保存")

            # 提取用户/商户信息
            users_data = await page.evaluate("""() => {
                const results = [];

                // 尝试多种选择器
                const selectors = [
                    'a[href*="/user/profile/"]',
                    'a[href*="/store/"]',
                    'a[href*="/shop/"]',
                    '.user-item',
                    '.merchant-item',
                    '.store-item',
                ];

                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        console.log('Found elements with:', selector);
                        elements.forEach((elem, index) => {
                            if (index >= 20) return;

                            try {
                                const href = elem.getAttribute('href') || elem.querySelector('a')?.getAttribute('href');
                                const name = elem.textContent || elem.innerText || '';

                                if (href && (href.includes('/user/profile/') || href.includes('/store/') || href.includes('/shop/'))) {
                                    const userId = href.split('/').pop()?.split('?')[0];

                                    results.push({
                                        userId: userId,
                                        userName: name.trim().substring(0, 50),
                                        href: href,
                                        selector: selector
                                    });
                                }
                            } catch (e) {
                            }
                        });
                        break;
                    }
                }

                return results;
            }""")

            print(f"   找到 {len(users_data)} 个结果")

            if users_data:
                merchants_found.extend(users_data)
                break  # 找到了就停止尝试其他URL

        # 去重
        seen = {}
        unique_merchants = []
        for m in merchants_found:
            user_id = m['userId']
            if user_id and user_id not in seen:
                seen[user_id] = True
                unique_merchants.append(m)

        print(f"\n✅ 总共找到 {len(unique_merchants)} 个唯一账号")

        # 验证前几个账号
        verified = []
        for i, merchant in enumerate(unique_merchants[:max_results], 1):
            print(f"\n[{i}/{len(unique_merchants)}] 验证: {merchant['userName']}")
            print(f"   ID: {merchant['userId']}")

            is_valid, notes = await verify_merchant(browser, merchant['userId'], category)

            if is_valid:
                verified.append({
                    'name': merchant['userName'],
                    'id': merchant['userId'],
                    'category': category,
                    'notes': notes
                })
                print(f"   ✅ 确认为目标账号")
            else:
                print(f"   ⚠️  不符合条件")

        print(f"\n验证通过: {len(verified)}/{len(unique_merchants)}")

        return verified

    finally:
        await browser.close()


async def verify_merchant(browser, user_id, category):
    """验证商户账号"""
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

        # 检查是否有认证标识（蓝V或企业标识）
        has_verification = await page.evaluate("""() => {
            // 查找认证标识
            const verifySelectors = [
                '[class*="verify"]',
                '[class*="enterprise"]',
                '[class*="official"]',
                '.verify-icon',
                '.official-badge',
            ];

            for (const selector of verifySelectors) {
                if (document.querySelector(selector)) {
                    return true;
                }
            }
            return false;
        }""")

        # 分析内容相关性
        keywords = {
            '牙医': ['牙', '齿', '口腔', '诊所', '牙科', '洗牙', '补牙', '医生', '治疗'],
            '美容院': ['美容', '护肤', '美容院', '美业', '护理', '皮肤', '项目'],
            '按摩店': ['按摩', '推拿', '理疗', 'SPA', '足疗', '服务'],
            '养生馆': ['养生', '中医', '针灸', '艾灸', '调理', '健康'],
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

        # 有认证标识 或 内容相关性高
        return (has_verification or ratio >= 0.2), notes_data[:3]

    except Exception as e:
        print(f"   验证失败: {e}")
        return False, []


async def main():
    """主函数"""
    print("=" * 70)
    print("🔍 小红书商户搜索模式")
    print("=" * 70)
    print("\n使用商户/店铺搜索功能，寻找真正的商家账号")
    print("-" * 70)

    search_tasks = [
        ("牙医", "牙医", 10),
        ("口腔", "牙医", 10),
        ("美容院", "美容院", 10),
        ("养生", "养生馆", 10),
    ]

    all_verified = {}

    for keyword, category, max_results in search_tasks:
        print(f"\n\n{'='*70}")
        print(f"搜索: {keyword} (商户模式)")
        print(f"{'='*70}")

        try:
            verified = await search_merchants(keyword, category, max_results)

            if verified:
                for acc in verified:
                    all_verified[acc['name']] = acc

            await asyncio.sleep(2)  # 休息一下
        except Exception as e:
            print(f"搜索失败: {e}")
            continue

    print(f"\n\n{'='*70}")
    print(f"🎉 商户搜索完成")
    print(f"{'='*70}")
    print(f"\n共找到 {len(all_verified)} 个真实商家账号")

    if all_verified:
        print("\n✅ 商家账号列表:")
        for i, (name, acc) in enumerate(all_verified.items(), 1):
            print(f"{i}. {name} ({acc['category']})")

        # 保存
        with open('/Users/xiaoningli/xiaohongshu_automation/data/verified_merchants.json', 'w', encoding='utf-8') as f:
            json.dump(all_verified, f, ensure_ascii=False, indent=2)

        # 更新监控列表
        with open('/Users/xiaoningli/xiaohongshu_automation/data/monitored_accounts.json', 'r', encoding='utf-8') as f:
            current_accounts = json.load(f)

        # 清空并只保留验证通过的
        new_accounts = {}
        for name, acc in all_verified.items():
            new_accounts[name] = {
                'id': acc['id'],
                'category': acc['category'],
                'added_date': datetime.now().strftime('%Y-%m-%d'),
                'last_check': None,
                'notes': []
            }

        with open('/Users/xiaoningli/xiaohongshu_automation/data/monitored_accounts.json', 'w', encoding='utf-8') as f:
            json.dump(new_accounts, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 已更新监控列表")
        print(f"   文件: monitored_accounts.json")
        print(f"   账号数: {len(new_accounts)}")

    else:
        print("\n⚠️  未找到符合条件的商户")
        print("\n建议:")
        print("1. 小红书的商户功能可能需要特殊的搜索方式")
        print("2. 可以手动查找一些真实商家账号")
        print("3. 告诉我账号名，我帮你添加")


if __name__ == "__main__":
    asyncio.run(main())
