#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全国范围搜索 - 所有可能使用预约系统的商家
"""
import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


# 全面的商家分类和关键词
MERCHANT_CATEGORIES = {
    '教育培训': [
        '舞蹈室', '瑜伽馆', '普拉提', '钢琴培训', '美术班',
        '音乐培训', '英语培训', '早教中心', '婴幼儿游泳',
        '补习班', '辅导班', '职业技能培训'
    ],
    '健康养生': [
        '健身房', '瑜伽馆', '普拉提', '按摩店', '足疗',
        'SPA', '养生馆', '中医馆', '理疗', '推拿',
        '艾灸', '针灸', '康复中心'
    ],
    '美容美发': [
        '美容院', '美甲店', '美发', '美睫', '半永久',
        '纹绣', '皮肤管理', '医美', '整形医院'
    ],
    '医疗口腔': [
        '牙医', '口腔诊所', '牙科', '牙齿矫正',
        '眼科诊所', '体检中心', '诊所'
    ],
    '宠物服务': [
        '宠物医院', '宠物美容', '宠物店', '宠物寄养'
    ],
    '汽车服务': [
        '汽车保养', '汽车维修', '洗车', '汽车美容'
    ],
    '摄影服务': [
        '摄影工作室', '摄像', '婚纱摄影', '写真',
        '照相馆', '证件照'
    ],
    '场地租赁': [
        '会议室', '活动场地', '排练室', '录音棚',
        '直播间', '摄影棚', '共享办公', '联合办公'
    ],
    '餐饮场地': [
        '咖啡厅', '茶室', '私房菜', '小型餐厅',
        '包间预订', '聚餐场地'
    ],
    '婚庆服务': [
        '婚庆公司', '婚礼策划', '婚宴场地'
    ],
    '体育场馆': [
        '网球场', '羽毛球馆', '乒乓球', '篮球场',
        '游泳馆', '溜冰场', '健身房'
    ],
    '心理咨询': [
        '心理咨询', '心理辅导', '心理咨询室'
    ],
    '其他服务': [
        '律师事务所', '会计服务', '设计工作室',
        '花店', '蛋糕店', '定制服务'
    ]
}


async def search_category(category_name, keywords, max_per_keyword=10):
    """搜索一个分类下的所有关键词"""
    print(f"\n{'='*70}")
    print(f"📂 分类: {category_name}")
    print(f"{'='*70}")

    all_verified = []

    for keyword in keywords[:5]:  # 每个分类最多搜5个关键词
        try:
            print(f"\n🔍 搜索: {keyword}")

            verified = await search_single_keyword(keyword, category_name, max_per_keyword)

            if verified:
                all_verified.extend(verified)
                print(f"   ✅ 找到 {len(verified)} 个账号")

            await asyncio.sleep(2)  # 休息避免被限制

        except Exception as e:
            print(f"   ⚠️  搜索失败: {e}")
            continue

    return all_verified


async def search_single_keyword(keyword, category, max_results=10):
    """搜索单个关键词"""
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

        # 滚动
        for i in range(3):
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
                            userName: userName
                        });
                    }
                } catch (e) {}
            });

            return results;
        }""")

        print(f"   找到 {len(users_data)} 个用户")

        # 简化验证 - 只要有笔记内容就通过
        verified = []
        for user in users_data[:max_results]:
            is_valid = await quick_verify(browser, user['userId'])
            if is_valid:
                verified.append({
                    'name': user['userName'],
                    'id': user['userId'],
                    'category': category
                })

        return verified

    finally:
        await browser.close()


async def quick_verify(browser, user_id):
    """快速验证 - 只检查是否有笔记内容"""
    try:
        contexts = browser.contexts
        context = contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
        await page.goto(user_url, timeout=20000)
        await page.wait_for_timeout(1500)

        # 检查是否有笔记
        has_notes = await page.evaluate("""() => {
            const noteElements = document.querySelectorAll('a[href*="/explore/"]');
            return noteElements.length > 0;
        }""")

        return has_notes

    except Exception as e:
        return False


async def main():
    """主函数"""
    print("=" * 70)
    print("🔍 全国范围搜索 - 所有预约系统商家")
    print("=" * 70)
    print("\n搜索范围:")
    print("- 全国所有城市")
    print("- 所有可能使用预约系统的商家")
    print("- 场地管理客户")
    print("-" * 70)

    all_verified = {}
    total_searched = 0

    # 遍历所有分类
    for category_name, keywords in MERCHANT_CATEGORIES.items():
        try:
            verified = await search_category(category_name, keywords, max_per_keyword=5)

            for acc in verified:
                # 去重
                if acc['id'] not in [a['id'] for a in all_verified.values()]:
                    all_verified[acc['name']] = acc
                    total_searched += 1

            if verified:
                print(f"\n✅ {category_name}: 找到 {len(verified)} 个账号")

        except Exception as e:
            print(f"\n⚠️  {category_name} 搜索失败: {e}")
            continue

    print(f"\n\n{'='*70}")
    print(f"🎉 搜索完成！")
    print(f"{'='*70}")
    print(f"\n共找到 {len(all_verified)} 个账号")

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

        # 保存
        with open('/Users/xiaoningli/xiaohongshu_automation/data/all_merchants.json', 'w', encoding='utf-8') as f:
            json.dump(all_verified, f, ensure_ascii=False, indent=2)

        # 更新监控列表
        with open('/Users/xiaoningli/xiaohongshu_automation/data/monitored_accounts.json', 'r', encoding='utf-8') as f:
            current_accounts = json.load(f)

        added_count = 0
        for name, acc in all_verified.items():
            if name not in current_accounts:
                current_accounts[name] = {
                    'id': acc['id'],
                    'category': acc['category'],
                    'added_date': datetime.now().strftime('%Y-%m-%d'),
                    'last_check': None,
                    'notes': []
                }
                added_count += 1

        with open('/Users/xiaoningli/xiaohongshu_automation/data/monitored_accounts.json', 'w', encoding='utf-8') as f:
            json.dump(current_accounts, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 已更新监控列表")
        print(f"   新增: {added_count} 个")
        print(f"   总计: {len(current_accounts)} 个")

    else:
        print("\n⚠️  未找到账号")


if __name__ == "__main__":
    asyncio.run(main())
