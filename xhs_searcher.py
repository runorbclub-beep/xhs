#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书账号搜索器
使用浏览器自动化搜索账号并筛选
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from typing import List, Dict, Optional


class XiaohongshuSearcher:
    """小红书账号搜索器"""

    def __init__(self):
        self.base_url = "https://www.xiaohongshu.com"
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def start(self, headless: bool = False):
        """启动浏览器"""
        playwright = await async_playwright().start()

        # 启动 Chromium 浏览器 - 使用更真实的配置
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu'
            ]
        )

        # 创建浏览器上下文 - 模拟真实用户
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai'
        )

        # 添加初始化脚本，隐藏自动化特征
        await self.context.add_init_script("""
            // 覆盖 navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 覆盖 chrome 对象
            window.chrome = {
                runtime: {}
            };

            // 覆盖 permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        # 创建新页面
        self.page = await self.context.new_page()

        print("✅ 浏览器启动成功")

    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def wait_for_login(self, timeout: int = 120):
        """等待用户登录"""
        print("\n" + "="*60)
        print("🔐 请在浏览器中登录小红书")
        print("="*60)

        try:
            await self.page.goto(f"{self.base_url}", timeout=60000, wait_until="domcontentloaded")
            print(f"\n✅ 已打开小红书页面")
        except Exception as e:
            print(f"⚠️  页面加载警告: {e}")
            print("继续尝试...")

        print(f"⏰ 请在 {timeout} 秒内确认登录状态...")

        # 等待登录成功
        start_time = time.time()

        while time.time() - start_time < timeout:
            await self.page.wait_for_timeout(1000)

            # 检查是否登录成功（通过检查页面元素）
            try:
                # 检查是否有登录按钮（如果没有，说明已登录）
                login_btn = await self.page.query_selector('.login-btn, .login-button')
                if not login_btn:
                    print("✅ 检测到已登录或无需登录！")
                    return True
            except:
                pass

            # 每10秒显示一次倒计时
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            if elapsed % 10 == 0 and elapsed > 0:
                print(f"⏳ 剩余时间: {remaining} 秒")

        print("⚠️  登录超时，但继续尝试搜索...")
        return True  # 即使超时也继续尝试

    async def search_accounts(self, keyword: str, max_results: int = 20,
                           min_followers: int = 20, max_followers: int = 100) -> List[Dict]:
        """搜索账号

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数
            min_followers: 最小粉丝数
            max_followers: 最大粉丝数

        Returns:
            账号列表
        """
        print(f"\n🔍 搜索关键词: {keyword}")
        print(f"📊 筛选条件: 粉丝数 {min_followers}-{max_followers}")

        try:
            # 访问搜索页面
            search_url = f"{self.base_url}/search_result?keyword={keyword}"
            await self.page.goto(search_url, timeout=60000, wait_until="domcontentloaded")
            print("✅ 已打开搜索页面")
            await self.page.wait_for_timeout(3000)
        except Exception as e:
            print(f"⚠️  搜索页面加载问题: {e}")
            print("尝试使用主页搜索...")

            # 尝试从主页搜索
            await self.page.goto(f"{self.base_url}", timeout=60000, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(2000)

        # 切换到"用户"标签（如果需要）
        try:
            user_tab = await self.page.query_selector('text=用户')
            if user_tab:
                await user_tab.click()
                await self.page.wait_for_timeout(2000)
        except:
            print("⚠️  未找到用户标签，继续使用当前结果")

        accounts = []
        page_num = 1

        while len(accounts) < max_results and page_num <= 3:
            print(f"\n📄 正在搜索第 {page_num} 页...")

            # 滚动加载更多
            await self._scroll_page()

            # 提取账号信息
            page_accounts = await self._extract_account_info(min_followers, max_followers)

            for account in page_accounts:
                # 避免重复
                if not any(a['id'] == account['id'] for a in accounts):
                    accounts.append(account)
                    print(f"   ✅ 找到: {account['name']} (粉丝: {account['followers']})")

                    if len(accounts) >= max_results:
                        break

            if len(accounts) >= max_results:
                break

            # 翻页（如果可以）
            try:
                next_button = await self.page.query_selector('.pagination-next:not(.disabled)')
                if next_button:
                    await next_button.click()
                    await self.page.wait_for_timeout(3000)
                    page_num += 1
                else:
                    print("   ℹ️  已到最后一页")
                    break
            except:
                print("   ℹ️  无法翻页，停止搜索")
                break

        print(f"\n✅ 搜索完成！共找到 {len(accounts)} 个符合条件的账号")

        return accounts

    async def _scroll_page(self):
        """滚动页面加载更多内容"""
        try:
            for i in range(3):
                await self.page.evaluate('window.scrollBy(0, 800)')
                await self.page.wait_for_timeout(1500)
        except:
            pass

    async def _extract_account_info(self, min_followers: int, max_followers: int) -> List[Dict]:
        """提取账号信息"""
        accounts = []

        try:
            # 查找所有账号卡片
            account_elements = await self.page.query_selector_all('.user-item, .search-user-item, .user-card')

            for element in account_elements:
                try:
                    # 提取账号信息
                    name_elem = await element.query_selector('.user-name, .username, .name')
                    name = await name_elem.inner_text() if name_elem else "未知"

                    # 提取粉丝数
                    followers = 0
                    followers_elem = await element.query_selector('.fans, .followers-count, .follower-count')
                    if followers_elem:
                        followers_text = await followers_elem.inner_text()
                        followers = self._parse_followers(followers_text)

                    # 提取账号ID（从链接）
                    account_id = ""
                    link_elem = await element.query_selector('a')
                    if link_elem:
                        href = await link_elem.get_attribute('href')
                        if href and '/user/profile/' in href:
                            account_id = href.split('/user/profile/')[1].split('?')[0]

                    # 筛选粉丝数
                    if min_followers <= followers <= max_followers and account_id:
                        accounts.append({
                            'name': name.strip(),
                            'id': account_id,
                            'followers': followers,
                            'url': f"{self.base_url}/user/profile/{account_id}"
                        })

                except Exception as e:
                    continue

        except Exception as e:
            print(f"⚠️  提取账号信息时出错: {e}")

        return accounts

    def _parse_followers(self, text: str) -> int:
        """解析粉丝数文本"""
        text = text.strip().replace('粉丝', '').replace('人', '').replace(',', '').strip()

        if '万' in text:
            return int(float(text.replace('万', '').replace('w', '').strip()) * 10000)
        elif 'k' in text.lower():
            return int(float(text.lower().replace('k', '').strip()) * 1000)
        else:
            try:
                return int(text)
            except:
                return 0

    async def get_account_notes(self, account_id: str, limit: int = 5) -> List[Dict]:
        """获取账号的笔记列表"""
        print(f"\n📖 获取账号笔记...")

        await self.page.goto(f"{self.base_url}/user/profile/{account_id}")
        await self.page.wait_for_timeout(3000)

        notes = []

        # 滚动加载
        await self._scroll_page()

        # 提取笔记
        try:
            note_elements = await self.page.query_selector_all('.note-item, .feed-item')

            for i, element in enumerate(note_elements[:limit]):
                try:
                    # 提取标题
                    title_elem = await element.query_selector('.title, .note-title')
                    title = await title_elem.inner_text() if title_elem else "无标题"

                    # 提取链接
                    link_elem = await element.query_selector('a')
                    note_url = ""
                    note_id = ""
                    if link_elem:
                        href = await link_elem.get_attribute('href')
                        if href:
                            note_url = f"{self.base_url}{href}"
                            if '/explore/' in href:
                                note_id = href.split('/explore/')[1].split('?')[0]

                    if note_id:
                        notes.append({
                            'id': note_id,
                            'title': title.strip(),
                            'url': note_url
                        })

                        print(f"   📌 {title[:40]}...")

                except:
                    continue

        except Exception as e:
            print(f"⚠️  获取笔记时出错: {e}")

        print(f"✅ 找到 {len(notes)} 条笔记")

        return notes


async def main():
    """测试搜索功能"""
    searcher = XiaohongshuSearcher()

    try:
        # 启动浏览器
        await searcher.start(headless=False)

        # 等待登录
        if not await searcher.wait_for_login(timeout=120):
            print("❌ 登录失败")
            return

        # 搜索账号
        keyword = input("\n请输入搜索关键词: ").strip()
        min_followers = int(input("最小粉丝数 (默认20): ") or "20")
        max_followers = int(input("最大粉丝数 (默认100): ") or "100")

        accounts = await searcher.search_accounts(
            keyword=keyword,
            max_results=10,
            min_followers=min_followers,
            max_followers=max_followers
        )

        # 显示结果
        print("\n" + "="*60)
        print("📊 搜索结果")
        print("="*60)

        for i, account in enumerate(accounts, 1):
            print(f"\n[{i}] {account['name']}")
            print(f"    ID: {account['id']}")
            print(f"    粉丝: {account['followers']}")
            print(f"    链接: {account['url']}")

        # 保存结果
        if accounts:
            save = input("\n是否保存搜索结果？(y/n): ").strip().lower()
            if save == 'y':
                filename = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'keyword': keyword,
                        'search_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'accounts': accounts
                    }, f, ensure_ascii=False, indent=2)
                print(f"✅ 已保存到: {filename}")

        print("\n按Enter键退出...")
        input()

    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    finally:
        await searcher.close()


if __name__ == "__main__":
    asyncio.run(main())
