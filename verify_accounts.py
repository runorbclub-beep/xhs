#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证账号内容 - 确保是真正的目标账号
"""
import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def verify_account(account_name, account_id, category):
    """验证账号是否真的是目标行业账号"""
    print(f"\n🔍 验证账号: {account_name}")
    print(f"   ID: {account_id}")

    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

    try:
        contexts = browser.contexts
        context = contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        # 访问账号主页
        user_url = f"https://www.xiaohongshu.com/user/profile/{account_id}"
        print(f"   正在访问主页...")
        await page.goto(user_url, timeout=30000)
        await page.wait_for_timeout(3000)

        # 滚动加载笔记
        print(f"   正在加载笔记内容...")
        for i in range(5):
            await page.evaluate('window.scrollBy(0, 500)')
            await page.wait_for_timeout(1500)

        # 提取笔记内容和标题
        notes_data = await page.evaluate("""() => {
            const results = [];
            const noteElements = document.querySelectorAll('a[href*="/explore/"]');

            noteElements.forEach((elem, index) => {
                if (index < 15) {
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

        print(f"   ✅ 找到 {len(notes_data)} 条笔记")

        # 分析笔记内容，判断是否是目标账号
        is_target = analyze_account_content(notes_data, category)

        if is_target:
            print(f"   ✅ 确认为目标账号！")
            # 显示前3条笔记
            for i, note in enumerate(notes_data[:3], 1):
                title = note['title'] or '无标题'
                print(f"      [{i}] {title[:50]}...")
        else:
            print(f"   ⚠️  可能不是目标账号")
            print(f"      笔记内容与'{category}'不相关")

        return is_target, notes_data[:3]  # 返回是否是目标账号和前3条笔记

    except Exception as e:
        print(f"   ❌ 验证失败: {e}")
        return False, []
    finally:
        await browser.close()


def analyze_account_content(notes, category):
    """分析笔记内容，判断是否是目标账号"""
    if not notes:
        return False

    # 定义各行业的关键词
    keywords = {
        '牙医': ['牙', '齿', '口腔', '诊所', '牙科', '洗牙', '补牙', '拔牙', '根管', '牙齿', '正畸', '种植'],
        '美容院': ['美容', '护肤', '美容院', '美业', '护理', '皮肤', '面膜', '美容店', '美甲'],
        '按摩店': ['按摩', '推拿', '理疗', 'SPA', '足疗', '按摩店', '养生', '放松'],
        '养生馆': ['养生', '中医', '针灸', '艾灸', '调理', '养生馆', '健康', '滋补'],
        '美甲店': ['美甲', '指甲', '美甲店', '美睫', '睫毛', '美业']
    }

    # 获取分类的关键词
    category_keywords = keywords.get(category, [])

    if not category_keywords:
        return True  # 如果没有定义关键词，默认通过

    # 统计相关笔记数量
    relevant_count = 0
    for note in notes:
        full_text = (note['title'] + ' ' + note['content']).lower()

        # 检查是否包含任何关键词
        for keyword in category_keywords:
            if keyword in full_text:
                relevant_count += 1
                break

    # 如果超过50%的笔记相关，认为是目标账号
    ratio = relevant_count / len(notes)
    print(f"   相关笔记: {relevant_count}/{len(notes)} ({ratio*100:.0f}%)")

    return ratio >= 0.3  # 至少30%的笔记相关


async def main():
    """主函数"""
    # 读取当前监控账号
    with open('/Users/xiaoningli/xiaohongshu_automation/data/monitored_accounts.json', 'r', encoding='utf-8') as f:
        accounts = json.load(f)

    print("=" * 70)
    print("🔍 验证账号内容 - 确认目标账号")
    print("=" * 70)

    # 验证前10个账号
    verified_accounts = {}
    count = 0

    for account_name, account_info in list(accounts.items())[:10]:
        account_id = account_info['id']
        category = account_info['category']

        is_target, notes = await verify_account(account_name, account_id, category)

        if is_target and notes:
            verified_accounts[account_name] = {
                'id': account_id,
                'category': category,
                'notes': notes,
                'verified': True
            }
            count += 1

    print("\n" + "=" * 70)
    print(f"✅ 验证完成！")
    print(f"   原账号数: 10")
    print(f"   确认为目标账号: {count} 个")
    print("=" * 70)

    # 保存验证结果
    with open('/Users/xiaoningli/xiaohongshu_automation/verified_accounts.json', 'w', encoding='utf-8') as f:
        json.dump(verified_accounts, f, ensure_ascii=False, indent=2)

    print(f"\n已保存到: verified_accounts.json")

    if count > 0:
        print(f"\n✅ 找到 {count} 个真实的目标账号！")
        print("\n建议使用这些账号进行互动:")
        for name in verified_accounts.keys():
            print(f"  - {name}")
    else:
        print("\n⚠️  未找到符合条件的目标账号")
        print("建议:")
        print("1. 更换搜索关键词")
        print("2. 调整筛选条件")


if __name__ == "__main__":
    asyncio.run(main())
