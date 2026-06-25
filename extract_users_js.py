#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import json


async def extract_users_with_js():
    """使用JavaScript直接提取用户信息"""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

    contexts = browser.contexts
    context = contexts[0]
    pages = context.pages

    # 找到小红书页面
    xiaohongshu_page = None
    for page in pages:
        if 'xiaohongshu.com/search_result' in page.url or 'xiaohongshu.com/search_result/' in page.url:
            xiaohongshu_page = page
            print(f"✅ 找到搜索页面: {page.url}")
            break

    if not xiaohongshu_page:
        # 尝试使用第一个xiaohongshu页面
        for page in pages:
            if 'xiaohongshu.com' in page.url and 'agree' not in page.url:
                xiaohongshu_page = page
                print(f"✅ 使用小红书页面: {page.url}")
                break

    if not xiaohongshu_page:
        print("❌ 未找到小红书搜索页面")
        await browser.close()
        return

    print("\n等待页面加载完成...")
    await xiaohongshu_page.wait_for_timeout(5000)

    print("执行JavaScript提取用户信息...")

    # 执行JavaScript获取页面内容
    users_data = await xiaohongshu_page.evaluate("""() => {
        const results = [];

        // 查找所有可能包含用户信息的元素
        const allElements = document.querySelectorAll('*');

        // 查找包含链接的元素
        const linkElements = document.querySelectorAll('a[href*="/user/profile/"]');

        linkElements.forEach((link, index) => {
            try {
                const href = link.getAttribute('href');
                if (href && href.includes('/user/profile/')) {
                    const userId = href.split('/user/profile/')[1].split('?')[0];

                    // 查找用户名
                    let userName = '';
                    const nameSelectors = ['.name', '.username', '.nickname', '.author-name', '[class*="name"]'];
                    for (const selector of nameSelectors) {
                        const nameElem = link.querySelector(selector);
                        if (nameElem) {
                            const text = nameElem.textContent || nameElem.innerText || '';
                            if (text && text.length > 0 && text.length < 50) {
                                userName = text.trim();
                                break;
                            }
                        }
                    }

                    // 如果没找到，从链接文本获取
                    if (!userName) {
                        userName = link.textContent.trim().substring(0, 30);
                    }

                    // 查找粉丝数
                    let fansCount = 0;
                    const parent = link.closest('[class*="card"], [class*="item"], [class*="user"], [class*="author"]');

                    if (parent) {
                        const parentText = parent.textContent || '';
                        const fansMatch = parentText.match(/(\d+)\s*粉丝/);
                        if (fansMatch) {
                            fansCount = parseInt(fansMatch[1]);
                        }

                        // 尝试其他粉丝数格式
                        if (fansCount === 0) {
                            const allMatches = parentText.match(/\d+/g);
                            if (allMatches) {
                                // 取最后一个数字（可能是粉丝数）
                                fansCount = parseInt(allMatches[allMatches.length - 1]);
                            }
                        }
                    }

                    results.push({
                        userId: userId,
                        userName: userName || '未知',
                        fansCount: fansCount,
                        href: href
                    });
                }
            } catch (e) {
                // 忽略错误
            }
        });

        return results;
    }""")

    print(f"\n找到 {len(users_data)} 个用户链接")

    # 筛选粉丝数20-100的用户
    filtered_users = [
        user for user in users_data
        if 20 <= user['fansCount'] <= 100
    ]

    print(f"筛选后（粉丝20-100）: {len(filtered_users)} 个用户")

    if filtered_users:
        print("\n用户列表:")
        for i, user in enumerate(filtered_users[:10], 1):
            print(f"\n[{i}] {user['userName']}")
            print(f"    ID: {user['userId']}")
            print(f"    粉丝: {user['fansCount']}")
            print(f"    链接: {user['href']}")

        # 保存结果
        with open('found_users.json', 'w', encoding='utf-8') as f:
            json.dump(filtered_users, f, ensure_ascii=False, indent=2)

        print("\n✅ 结果已保存到 found_users.json")

        # 询问是否添加到监控列表
        print("\n是否要添加这些用户到监控列表？")
        print("请运行: python3 smart_social_assistant.py --add-account '用户名,用户ID,牙医'")

    else:
        print("\n⚠️  未找到符合条件的用户（粉丝20-100）")
        print("\n所有找到的用户:")
        for user in users_data[:10]:
            print(f"  - {user['userName']}: {user['fansCount']} 粉丝")

    await browser.close()


if __name__ == "__main__":
    asyncio.run(extract_users_with_js())
