#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析小红书页面结构
"""

import asyncio
from playwright.async_api import async_playwright


async def analyze_page():
    """分析小红书搜索页面结构"""
    print("🔍 连接到浏览器...")

    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

    contexts = browser.contexts
    context = contexts[0]

    # 找到小红书页面
    pages = context.pages
    xiaohongshu_page = None
    for page in pages:
        if 'xiaohongshu.com' in page.url:
            xiaohongshu_page = page
            print(f"✅ 找到小红书页面: {page.url}")
            break

    if not xiaohongshu_page:
        print("❌ 未找到小红书页面")
        await browser.close()
        return

    # 获取页面内容
    print("\n📄 正在分析页面结构...")

    # 保存页面HTML
    content = await xiaohongshu_page.content()

    with open('/Users/xiaoningli/xiaohongshu_automation/xiaohongshu_page.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ 页面HTML已保存到: xiaohongshu_page.html")

    # 尝试找到账号相关的元素
    print("\n🔍 查找账号相关元素...")

    # 尝试各种选择器
    selectors_to_try = [
        # 通用搜索结果
        '.search-item',
        '.search-result-item',
        '.item',
        '.card',

        # 用户相关
        '.user',
        '.user-item',
        '.user-card',
        '.account',
        '.author',

        # 小红书特定
        '.note-item',
        '.feed-item',
        '.user-list-item',
        '.search-user',

        # 带有data属性的
        '[data-user]',
        '[data-author]',
        '[data-id]',
    ]

    found_elements = []

    for selector in selectors_to_try:
        try:
            elements = await xiaohongshu_page.query_selector_all(selector)
            if elements:
                count = len(elements)
                print(f"   ✅ 找到 {count} 个 '{selector}' 元素")

                # 分析第一个元素的结构
                if count > 0:
                    first_elem = elements[0]
                    html = await first_elem.inner_html()
                    if len(html) < 500:
                        print(f"      内容预览: {html[:200]}...")

                    # 尝试提取子元素
                    try:
                        text = await first_elem.inner_text()
                        if text and len(text) < 200:
                            print(f"      文本: {text[:100]}...")
                    except:
                        pass

                found_elements.append((selector, count))
        except Exception as e:
            pass

    # 查找可能包含粉丝数的元素
    print("\n🔍 查找粉丝数相关元素...")
    fans_selectors = [
        '.fans',
        '.follower',
        '.follow-count',
        '.fans-count',
        '[class*="fans"]',
        '[class*="follower"]',
    ]

    for selector in fans_selectors:
        try:
            elements = await xiaohongshu_page.query_selector_all(selector)
            if elements:
                count = len(elements)
                print(f"   ✅ 找到 {count} 个 '{selector}' 元素")

                if count > 0 and count < 20:
                    for i, elem in enumerate(elements[:3]):
                        try:
                            text = await elem.inner_text()
                            print(f"      [{i+1}] {text}")
                        except:
                            pass
        except:
            pass

    # 查找用户名相关元素
    print("\n🔍 查找用户名相关元素...")
    name_selectors = [
        '.name',
        '.username',
        '.nickname',
        '.user-name',
        '.author-name',
        '[class*="name"]',
    ]

    for selector in name_selectors:
        try:
            elements = await xiaohongshu_page.query_selector_all(selector)
            if elements:
                count = len(elements)
                print(f"   ✅ 找到 {count} 个 '{selector}' 元素")

                if count > 0 and count < 30:
                    for i, elem in enumerate(elements[:5]):
                        try:
                            text = await elem.inner_text()
                            if len(text) < 50:
                                print(f"      [{i+1}] {text}")
                        except:
                            pass
        except:
            pass

    # 总结
    print("\n" + "="*60)
    print("📊 分析总结")
    print("="*60)

    if found_elements:
        print(f"\n找到以下可能的选择器:")
        for selector, count in found_elements:
            print(f"  - {selector}: {count} 个元素")
    else:
        print("\n⚠️  未找到明显的账号元素")

    print("\n✅ 分析完成！HTML已保存到 xiaohongshu_page.html")

    await browser.close()


if __name__ == "__main__":
    asyncio.run(analyze_page())
