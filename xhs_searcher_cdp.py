#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书账号搜索器 - CDP模式
连接到用户已打开的Chrome浏览器
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from typing import List, Dict, Optional


class XiaohongshuSearcherCDP:
    """小红书账号搜索器 - CDP模式"""

    def __init__(self, cdp_url: str = "http://localhost:9222"):
        """
        Args:
            cdp_url: Chrome DevTools Protocol URL，默认localhost:9222
        """
        self.cdp_url = cdp_url
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def connect(self):
        """连接到已打开的Chrome浏览器"""
        print("\n🔌 正在连接到您的Chrome浏览器...")

        try:
            self.playwright = await async_playwright().start()

            # 使用CDP连接到现有浏览器
            self.browser = await self.playwright.chromium.connect_over_cdp(self.cdp_url)
            print("✅ 已连接到Chrome浏览器")

            # 获取现有的contexts
            contexts = self.browser.contexts
            if contexts:
                self.context = contexts[0]
                print("✅ 已获取浏览器上下文")
            else:
                print("⚠️  未找到现有上下文，创建新上下文")
                self.context = await self.browser.new_context()

            # 获取或创建页面
            pages = self.context.pages
            if pages:
                # 找到已打开的小红书页面
                xiaohongshu_page = None
                for page in pages:
                    try:
                        url = page.url
                        if 'xiaohongshu.com' in url or 'rednote.com' in url:
                            xiaohongshu_page = page
                            print(f"✅ 找到小红书页面: {url}")
                            break
                    except:
                        continue

                if xiaohongshu_page:
                    self.page = xiaohongshu_page
                else:
                    # 使用第一个页面
                    self.page = pages[0]
                    print(f"✅ 使用现有页面: {self.page.url}")
            else:
                print("⚠️  未找到现有页面，创建新页面")
                self.page = await self.context.new_page()

            return True

        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print("\n可能的原因：")
            print("1. Chrome没有启用远程调试")
            print("2. 端口9222被占用或不是正确的端口")
            print("3. Chrome浏览器未打开")
            print("\n请按上面的步骤操作后重试")
            return False

    async def close(self):
        """关闭连接"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

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
            # 导航到搜索页面
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
            print(f"正在打开搜索页面...")
            await self.page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)

            print("✅ 已打开搜索页面")
            print("\n⏳ 正在分析搜索结果...")

            # 尝试切换到"用户"标签
            try:
                # 查找并点击"用户"标签
                user_tab_selectors = [
                    'text=用户',
                    '[data-tab="user"]',
                    '.tab-user',
                    'a:has-text("用户")'
                ]

                for selector in user_tab_selectors:
                    try:
                        user_tab = await self.page.query_selector(selector)
                        if user_tab:
                            await user_tab.click()
                            await self.page.wait_for_timeout(2000)
                            print("✅ 已切换到用户标签")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"⚠️  切换用户标签失败: {e}")

            # 滚动加载更多
            print("正在加载更多内容...")
            for i in range(3):
                await self.page.evaluate('window.scrollBy(0, 500)')
                await self.page.wait_for_timeout(1500)

            # 提取账号信息
            accounts = await self._extract_account_info(min_followers, max_followers)

            return accounts

        except Exception as e:
            print(f"❌ 搜索过程出错: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def _extract_account_info(self, min_followers: int, max_followers: int) -> List[Dict]:
        """提取账号信息 - 使用JavaScript注入方法"""
        accounts = []

        try:
            print("   使用JavaScript提取方法...")

            # 执行JavaScript获取页面内容
            users_data = await self.page.evaluate("""() => {
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
                                const fansMatch = parentText.match(/(\\d+)\\s*粉丝/);
                                if (fansMatch) {
                                    fansCount = parseInt(fansMatch[1]);
                                }

                                // 尝试其他粉丝数格式
                                if (fansCount === 0) {
                                    const allMatches = parentText.match(/\\d+/g);
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

            print(f"   找到 {len(users_data)} 个用户链接")

            # 筛选粉丝数符合条件的用户
            for user in users_data:
                try:
                    fans = user.get('fansCount', 0)
                    if min_followers <= fans <= max_followers:
                        account = {
                            'name': user.get('userName', '未知'),
                            'id': user.get('userId', ''),
                            'followers': fans,
                            'url': f"https://www.xiaohongshu.com{user.get('href', '')}"
                        }
                        # 避免重复
                        if not any(a['id'] == account['id'] for a in accounts):
                            accounts.append(account)
                            print(f"   ✅ {account['name']} (粉丝: {account['followers']})")
                except Exception as e:
                    continue

        except Exception as e:
            print(f"⚠️  JavaScript提取失败: {e}")
            import traceback
            traceback.print_exc()

        return accounts

    async def _extract_single_account(self, element, min_followers: int, max_followers: int) -> Optional[Dict]:
        """从单个元素提取账号信息"""
        try:
            # 提取名称
            name_elem = await element.query_selector('.user-name, .username, .name, .author-name, .nickname')
            name = ""
            if name_elem:
                name = await name_elem.inner_text()
                name = name.strip()

            # 提取粉丝数
            followers = 0
            followers_elem = await element.query_selector('.fans, .followers-count, .follower-count, .follow-count')
            if followers_elem:
                followers_text = await followers_elem.inner_text()
                followers = self._parse_followers(followers_text)

            # 提取账号ID（从链接）
            account_id = ""
            link_elem = await element.query_selector('a')
            if link_elem:
                href = await link_elem.get_attribute('href')
                if href:
                    if '/user/profile/' in href:
                        account_id = href.split('/user/profile/')[1].split('?')[0]
                    elif '/user/' in href:
                        account_id = href.split('/user/')[1].split('?')[0]

            # 筛选粉丝数
            if account_id and (min_followers <= followers <= max_followers):
                return {
                    'name': name,
                    'id': account_id,
                    'followers': followers,
                    'url': f"https://www.xiaohongshu.com/user/profile/{account_id}"
                }

        except Exception as e:
            pass

        return None

    async def _extract_from_page_text(self, min_followers: int, max_followers: int) -> List[Dict]:
        """从页面文本提取账号（备用方法）"""
        print("   使用备用提取方法...")

        accounts = []

        try:
            # 获取页面内容
            content = await self.page.content()

            # 这里可以添加更多的解析逻辑
            # 暂时返回空列表
            pass

        except Exception as e:
            print(f"   备用方法失败: {e}")

        return accounts

    def _parse_followers(self, text: str) -> int:
        """解析粉丝数文本"""
        if not text:
            return 0

        text = text.strip()
        # 移除常见的中文字符
        text = text.replace('粉丝', '').replace('人', '').replace('粉', '').replace(',', '').strip()

        try:
            if '万' in text:
                number = float(text.replace('万', '').replace('w', '').strip())
                return int(number * 10000)
            elif 'k' in text.lower():
                number = float(text.lower().replace('k', '').strip())
                return int(number * 1000)
            else:
                return int(text)
        except:
            return 0


async def main():
    """测试搜索功能"""
    searcher = XiaohongshuSearcherCDP()

    try:
        # 连接到浏览器
        if not await searcher.connect():
            print("❌ 连接失败，请按提示操作后重试")
            return

        # 搜索账号
        keyword = input("\n请输入搜索关键词（例如：牙医）: ").strip()
        if not keyword:
            keyword = "牙医"

        min_followers = int(input("最小粉丝数（默认20）: ") or "20")
        max_followers = int(input("最大粉丝数（默认100）: ") or "100")

        accounts = await searcher.search_accounts(
            keyword=keyword,
            max_results=20,
            min_followers=min_followers,
            max_followers=max_followers
        )

        # 显示结果
        print("\n" + "="*60)
        print("📊 搜索结果")
        print("="*60)

        if accounts:
            for i, account in enumerate(accounts, 1):
                print(f"\n[{i}] {account['name']}")
                print(f"    ID: {account['id']}")
                print(f"    粉丝: {account['followers']}")
                print(f"    链接: {account['url']}")
        else:
            print("\n⚠️  未找到符合条件的账号")
            print("可能的原因：")
            print("1. 搜索关键词没有结果")
            print(f"2. 粉丝数筛选条件（{min_followers}-{max_followers}）太严格")
            print("3. 页面结构与预期不同")

        print("\n" + "="*60)

    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    finally:
        await searcher.close()


if __name__ == "__main__":
    asyncio.run(main())
