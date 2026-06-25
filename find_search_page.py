#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright


async def find_and_analyze():
    """找到搜索结果页面并分析"""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

    contexts = browser.contexts
    context = contexts[0]

    pages = context.pages

    print("📄 当前打开的所有页面:")
    for i, page in enumerate(pages):
        print(f"  [{i}] {page.url}")

    # 找到搜索结果页面
    search_page = None
    for page in pages:
        if 'search_result' in page.url and 'keyword' in page.url:
            search_page = page
            print(f"\n✅ 找到搜索结果页面: {page.url}")
            break

    if not search_page:
        print("\n❌ 未找到搜索结果页面")
        print("请确保在小红书中进行了搜索")
        await browser.close()
        return

    # 保存搜索页面
    content = await search_page.content()

    with open('search_page.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ 搜索页面已保存到: search_page.html")

    # 截图
    await search_page.screenshot(path='search_page_screenshot.png')
    print("✅ 截图已保存到: search_page_screenshot.png")

    # 尝试各种选择器
    print("\n🔍 测试各种选择器...")

    # 查找所有可能的用户卡片
    all_elements = await search_page.query_selector_all('*')

    print(f"\n页面总共有 {len(all_elements)} 个元素")

    # 查找包含特定类名的元素
    print("\n查找包含特定关键词的class名称:")

    class_keywords = ['user', 'author', 'card', 'item', 'account', 'avatar', 'name', 'fans']

    for element in all_elements[:200]:  # 只检查前200个元素
        try:
            class_name = await element.get_attribute('class')
            if class_name:
                for keyword in class_keywords:
                    if keyword in class_name.lower():
                        text = await element.inner_text()
                        if text and len(text) < 100:
                            print(f"   class='{class_name}': {text[:50]}")
                        break
        except:
            continue

    await browser.close()


if __name__ == "__main__":
    asyncio.run(find_and_analyze())
