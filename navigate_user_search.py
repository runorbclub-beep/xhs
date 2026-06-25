#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright


async def navigate_to_user_search():
    """导航到用户搜索页面"""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

    contexts = browser.contexts
    context = contexts[0]
    pages = context.pages

    # 找到小红书页面
    xiaohongshu_page = None
    for page in pages:
        if 'xiaohongshu.com' in page.url:
            xiaohongshu_page = page
            break

    if not xiaohongshu_page:
        print("❌ 未找到小红书页面")
        await browser.close()
        return

    print(f"当前页面: {xiaohongshu_page.url}")

    # 导航到用户搜索页面
    user_search_url = "https://www.xiaohongshu.com/search_result?keyword=牙医&type=51&page=1&search_type=0"
    print(f"\n导航到用户搜索页面...")

    await xiaohongshu_page.goto(user_search_url, timeout=30000)
    await xiaohongshu_page.wait_for_timeout(3000)

    print(f"新页面: {xiaohongshu_page.url}")

    # 保存页面
    content = await xiaohongshu_page.content()
    with open('user_search_page.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ 用户搜索页面已保存")

    # 截图
    await xiaohongshu_page.screenshot(path='user_search_screenshot.png', full_page=True)
    print("✅ 截图已保存")

    await browser.close()


if __name__ == "__main__":
    asyncio.run(navigate_to_user_search())
