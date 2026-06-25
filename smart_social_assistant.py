#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能社交助手 - 人机协作模式
核心功能：
1. 搜索和筛选目标账号
2. 监控账号新作品
3. 智能起草评论建议
4. 生成每日互动清单
"""

import sys
import json
import time
import random
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

from xhs_searcher_cdp import XiaohongshuSearcherCDP


class CommentGenerator:
    """评论生成器 - 根据内容类型生成个性化评论"""

    def __init__(self):
        # 美容院相关评论模板
        self.beauty_comments = [
            "太实用了！我们店也在考虑这个问题，感谢分享🌟",
            "做美容院确实不容易，这个经验很有价值！",
            "深有同感！经营这些年深有体会😊",
            "这个方法不错，准备试试看",
            "说得太对了！每条都说到心坎里了",
            "干货满满！已收藏，慢慢学习",
            "真实创业经历，比理论知识有用多了",
            "同行交流最珍贵，感谢分享！"
        ]

        # 牙医相关评论模板
        self.dentist_comments = [
            "专业！这个科普很到位",
            "作为患者看完放心多了",
            "牙医确实需要耐心和细心",
            "我们诊所也遇到类似情况",
            "技术和服务都很重要，说得对",
            "真实案例很有参考价值",
            "专业分享，学到了！",
            "牙医日常工作，真实记录"
        ]

        # 瑜伽馆相关评论模板
        self.yoga_comments = [
            "瑜伽就是这么神奇！",
            "学员的进步是最好的证明",
            "教学有方法，值得学习",
            "瑜伽馆经营有道啊",
            "身心合一，瑜伽的真谛",
            "老师专业，学员认真",
            "这个课程设计不错",
            "瑜伽改变生活，赞同！"
        ]

        # 通用评论模板
        self.general_comments = [
            "太有同感了！",
            "说得太对了！",
            "学到了！",
            "感谢分享！",
            "很有启发！",
            "赞同！",
            "受教了！",
            "干货满满！",
            "真实！",
            "支持！"
        ]

    def generate_comment(self, content: str, category: str = "") -> str:
        """根据内容和类别生成评论"""
        category = category.lower()

        if "美容" in category or "美容院" in content:
            return random.choice(self.beauty_comments)
        elif "牙医" in category or "牙科" in content or "口腔" in content:
            return random.choice(self.dentist_comments)
        elif "瑜伽" in category or "瑜伽馆" in content:
            return random.choice(self.yoga_comments)
        else:
            return random.choice(self.general_comments)


class AccountMonitor:
    """账号监控器 - 监控账号的新作品"""

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or Path(__file__).parent / "data")
        self.data_dir.mkdir(exist_ok=True)

        self.accounts_file = self.data_dir / "monitored_accounts.json"
        self.notes_file = self.data_dir / "tracked_notes.json"
        self.comment_gen = CommentGenerator()

        # 加载数据
        self.accounts = self._load_json(self.accounts_file, {})
        self.tracked_notes = self._load_json(self.notes_file, {})

    def _load_json(self, file_path: Path, default: dict) -> dict:
        """加载JSON文件"""
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default

    def _save_json(self, file_path: Path, data: dict):
        """保存JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_account(self, account_name: str, account_id: str, category: str = ""):
        """添加监控账号"""
        if account_name in self.accounts:
            print(f"⚠️  账号已存在: {account_name}")
            return

        self.accounts[account_name] = {
            "id": account_id,
            "category": category,
            "added_date": datetime.now().strftime('%Y-%m-%d'),
            "last_check": None,
            "notes": []
        }

        self._save_json(self.accounts_file, self.accounts)
        print(f"✅ 添加账号: {account_name}")

    def check_new_notes(self) -> List[Dict]:
        """检查所有账号的新作品"""
        new_notes = []

        for account_name, account_info in self.accounts.items():
            print(f"\n🔍 检查账号: {account_name}")

            # 这里需要实际获取笔记列表
            # 由于xiaohongshu-skill的限制，我们提供占位符
            print(f"   提示：请查看 {account_name} 的主页，检查是否有新作品")

            # 实际实现中，这里会调用API获取笔记列表
            # 并与已跟踪的笔记对比，找出新的

        return new_notes

    def generate_comment_suggestion(self, note: Dict) -> str:
        """为笔记生成评论建议"""
        content = note.get('content', '')
        category = note.get('category', '')

        suggestion = self.comment_gen.generate_comment(content, category)

        return suggestion

    def add_manual_note(self, account_name: str, note_id: str, note_title: str, note_url: str):
        """手动添加笔记到跟踪列表"""
        if account_name not in self.accounts:
            print(f"⚠️  账号不存在: {account_name}")
            return

        # 检查是否已跟踪
        for note in self.accounts[account_name]['notes']:
            if note['id'] == note_id:
                print(f"ℹ️  笔记已跟踪: {note_title}")
                return

        # 添加笔记
        note_data = {
            "id": note_id,
            "title": note_title,
            "url": note_url,
            "found_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "interacted": False,
            "interaction_type": "",
            "comment_suggestion": ""
        }

        # 生成评论建议
        account_category = self.accounts[account_name].get('category', '')
        note_data['comment_suggestion'] = self.generate_comment_suggestion({
            'content': note_title,
            'category': account_category
        })

        self.accounts[account_name]['notes'].append(note_data)
        self.accounts[account_name]['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self._save_json(self.accounts_file, self.accounts)

        print(f"\n✅ 添加新笔记到跟踪列表:")
        print(f"   📌 {note_title}")
        print(f"   💬 建议评论: {note_data['comment_suggestion']}")

    def generate_daily_report(self) -> Dict:
        """生成每日互动报告"""
        today = datetime.now().strftime('%Y-%m-%d')
        report = {
            "date": today,
            "total_accounts": len(self.accounts),
            "active_accounts": 0,
            "new_notes": [],
            "pending_interactions": [],
            "statistics": {
                "total_notes": 0,
                "interacted_notes": 0,
                "pending_notes": 0
            }
        }

        for account_name, account_info in self.accounts.items():
            notes = account_info.get('notes', [])

            if notes:
                report['active_accounts'] += 1
                report['statistics']['total_notes'] += len(notes)

            for note in notes:
                if not note.get('interacted', False):
                    report['pending_interactions'].append({
                        'account': account_name,
                        'note_id': note['id'],
                        'note_title': note['title'],
                        'note_url': note['url'],
                        'comment_suggestion': note.get('comment_suggestion', ''),
                        'found_date': note['found_date']
                    })
                    report['statistics']['pending_notes'] += 1
                else:
                    report['statistics']['interacted_notes'] += 1

        return report

    def mark_interacted(self, account_name: str, note_id: str, interaction_type: str):
        """标记笔记已互动"""
        if account_name not in self.accounts:
            return False

        for note in self.accounts[account_name]['notes']:
            if note['id'] == note_id:
                note['interacted'] = True
                note['interaction_type'] = interaction_type
                note['interacted_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self._save_json(self.accounts_file, self.accounts)
                print(f"✅ 已标记互动: {note['title']} ({interaction_type})")
                return True

        return False


class DailyReport:
    """每日报告生成器"""

    def __init__(self, monitor: AccountMonitor):
        self.monitor = monitor

    def generate(self) -> str:
        """生成每日报告"""
        report = self.monitor.generate_daily_report()

        output = []
        output.append("=" * 60)
        output.append(f"📊 每日互动报告 - {report['date']}")
        output.append("=" * 60)

        output.append(f"\n📈 统计概览:")
        output.append(f"   监控账号总数: {report['total_accounts']}")
        output.append(f"   活跃账号数: {report['active_accounts']}")
        output.append(f"   笔记总数: {report['statistics']['total_notes']}")
        output.append(f"   已互动: {report['statistics']['interacted_notes']}")
        output.append(f"   待互动: {report['statistics']['pending_notes']}")

        if report['pending_interactions']:
            output.append(f"\n📋 今日待互动清单:")
            output.append("-" * 60)

            for i, item in enumerate(report['pending_interactions'], 1):
                output.append(f"\n[{i}] {item['account']}")
                output.append(f"    笔记: {item['note_title']}")
                output.append(f"    链接: {item['note_url']}")
                output.append(f"    💬 建议评论: {item['comment_suggestion']}")
                output.append(f"    发现时间: {item['found_date']}")

        output.append("\n" + "=" * 60)
        output.append("✨ 使用说明:")
        output.append("1. 打开小红书APP或网页")
        output.append("2. 按照清单逐一访问笔记")
        output.append("3. 参考建议评论，亲自点赞和评论")
        output.append("4. 完成后标记为已互动")
        output.append("=" * 60 + "\n")

        return "\n".join(output)

    def save_to_file(self, filename: str = None):
        """保存报告到文件"""
        if not filename:
            filename = f"每日报告_{datetime.now().strftime('%Y%m%d')}.txt"

        report_path = Path(__file__).parent / "reports"
        report_path.mkdir(exist_ok=True)

        full_path = report_path / filename
        report_content = self.generate()

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"📄 报告已保存: {full_path}")

        return full_path


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能社交助手")
    parser.add_argument('--add-account', '-a', help='添加监控账号（格式：账号名,账号ID,分类）')
    parser.add_argument('--add-note', '-n', help='添加笔记到跟踪（格式：账号名,笔记ID,笔记标题,笔记URL）')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有监控账号')
    parser.add_argument('--report', '-r', action='store_true', help='生成每日报告')
    parser.add_argument('--mark', '-m', help='标记已互动（格式：账号名,笔记ID,互动类型）')
    parser.add_argument('--interactive', '-i', action='store_true', help='进入交互模式')
    parser.add_argument('--search', '-s', help='搜索账号（关键词）')
    parser.add_argument('--min-followers', type=int, default=20, help='最小粉丝数（默认20）')
    parser.add_argument('--max-followers', type=int, default=100, help='最大粉丝数（默认100）')
    parser.add_argument('--auto-add', action='store_true', help='搜索后自动添加到监控列表')
    parser.add_argument('--start-session', action='store_true', help='启动交互式浏览会话')

    args = parser.parse_args()

    monitor = AccountMonitor()

    try:
        if args.search:
            # 搜索账号
            print("\n" + "="*60)
            print("🔍 启动账号搜索功能")
            print("="*60)

            async def search_and_add():
                searcher = XiaohongshuSearcherCDP()
                try:
                    # 连接到已打开的浏览器
                    if not await searcher.connect():
                        print("❌ 连接浏览器失败")
                        print("\n请按提示操作后重试")
                        return

                    # 搜索账号
                    accounts = await searcher.search_accounts(
                        keyword=args.search,
                        max_results=20,
                        min_followers=args.min_followers,
                        max_followers=args.max_followers
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

                    # 自动添加到监控列表
                    if args.auto_add:
                        category = "牙医"  # 自动设置分类
                        print(f"\n正在添加账号到监控列表（分类: {category}）...")

                        for account in accounts:
                            monitor.add_account(account['name'], account['id'], category)
                            time.sleep(0.5)

                        print(f"\n✅ 已添加 {len(accounts)} 个账号到监控列表")
                    else:
                        # 询问是否添加
                        if accounts:
                            print(f"\n找到 {len(accounts)} 个账号")
                            add_accounts = input("\n是否添加所有账号到监控列表？(y/n): ").strip().lower()
                            if add_accounts == 'y':
                                category = input("请输入账号分类（美容院/牙医/瑜伽馆等）: ").strip()

                                for account in accounts:
                                    monitor.add_account(account['name'], account['id'], category)
                                    time.sleep(0.5)

                                print(f"✅ 已添加 {len(accounts)} 个账号")
                        else:
                            print("\n⚠️  未找到符合条件的账号，跳过添加")

                    print("\n按Enter键关闭浏览器...")
                    if not args.auto_add:
                        input()

                finally:
                    await searcher.close()

            asyncio.run(search_and_add())

        elif args.add_account:
            # 添加账号
            parts = args.add_account.split(',')
            if len(parts) >= 2:
                account_name = parts[0].strip()
                account_id = parts[1].strip()
                category = parts[2].strip() if len(parts) > 2 else ""
                monitor.add_account(account_name, account_id, category)

        elif args.add_note:
            # 添加笔记
            parts = args.add_note.split(',')
            if len(parts) >= 4:
                account_name = parts[0].strip()
                note_id = parts[1].strip()
                note_title = parts[2].strip()
                note_url = parts[3].strip()
                monitor.add_manual_note(account_name, note_id, note_title, note_url)

        elif args.list:
            # 列出账号
            monitor.list_accounts()

        elif args.report:
            # 生成报告
            report_gen = DailyReport(monitor)
            report_gen.generate()
            report_gen.save_to_file()

        elif args.mark:
            # 标记已互动
            parts = args.mark.split(',')
            if len(parts) >= 3:
                account_name = parts[0].strip()
                note_id = parts[1].strip()
                interaction_type = parts[2].strip()
                monitor.mark_interacted(account_name, note_id, interaction_type)

        elif args.start_session:
            # 启动交互式浏览会话
            asyncio.run(start_browsing_session(monitor))

        elif args.interactive:
            # 交互模式
            enter_interactive_mode(monitor)

        else:
            # 默认生成报告
            print("智能社交助手 - 人机协作模式")
            print("\n使用 --help 查看所有命令")
            print("\n快速开始:")
            print("  1. 添加监控账号: --add-account '账号名,账号ID,分类'")
            print("  2. 添加笔记到跟踪: --add-note '账号名,笔记ID,笔记标题,URL'")
            print("  3. 生成每日报告: --report")

    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


async def start_browsing_session(monitor: AccountMonitor):
    """启动交互式浏览会话"""
    print("\n" + "=" * 70)
    print("🤖 智能社交助手 - 交互式浏览会话")
    print("=" * 70)

    # 生成报告获取待互动清单
    report_gen = DailyReport(monitor)
    report = monitor.generate_daily_report()
    pending_notes = report.get('pending_interactions', [])

    if not pending_notes:
        print("\n✅ 太棒了！目前没有待互动的笔记")
        print("\n提示:")
        print("  - 使用 --add-note 添加新笔记")
        print("  - 使用 --search 搜索更多账号")
        return

    print(f"\n📋 今日待互动笔记: {len(pending_notes)} 条")
    print("\n" + "=" * 70)

    # 连接到浏览器
    print("\n🔌 正在连接到您的Chrome浏览器...")
    searcher = XiaohongshuSearcherCDP()
    try:
        if not await searcher.connect():
            print("❌ 连接浏览器失败")
            return

        print("✅ 已连接到浏览器")

        # 逐个浏览笔记
        for i, note_item in enumerate(pending_notes, 1):
            account_name = note_item['account']
            note_title = note_item['note_title']
            note_url = note_item['note_url']
            comment_suggestion = note_item['comment_suggestion']
            note_id = note_item['note_id']

            print("\n" + "=" * 70)
            print(f"📌 笔记 [{i}/{len(pending_notes)}]")
            print("=" * 70)
            print(f"\n账号: {account_name}")
            print(f"标题: {note_title}")
            print(f"💬 建议评论: {comment_suggestion}")

            # 导航到笔记页面
            print(f"\n🌐 正在打开笔记...")
            try:
                await searcher.page.goto(note_url, timeout=30000)
                await searcher.page.wait_for_timeout(2000)
                print("✅ 笔记已打开")

                # 等待用户互动
                print("\n" + "-" * 70)
                print("⏸️  请查看笔记并点赞/评论")
                print("完成后按 Enter 键继续到下一个笔记...")
                print("输入 'q' 或 'quit' 退出会话")
                print("输入 's' 或 'skip' 跳过当前笔记")
                print("-" * 70)

                user_input = input("\n您的选择: ").strip().lower()

                if user_input in ['q', 'quit', '退出']:
                    print("\n👋 会话已结束")
                    break
                elif user_input in ['s', 'skip', '跳过']:
                    print("⏭️  已跳过当前笔记")
                    continue
                else:
                    # 标记为已互动
                    interaction_type = "点赞+评论"
                    monitor.mark_interacted(account_name, note_id, interaction_type)
                    print("✅ 已标记为已互动")

            except Exception as e:
                print(f"❌ 打开笔记失败: {e}")
                print("提示: 请检查笔记URL是否正确")
                continue

        # 会话总结
        print("\n" + "=" * 70)
        print("📊 会话总结")
        print("=" * 70)

        final_report = monitor.generate_daily_report()
        print(f"\n已完成互动: {final_report['statistics']['interacted_notes']} 条")
        print(f"仍需互动: {final_report['statistics']['pending_notes']} 条")

        if final_report['statistics']['pending_notes'] == 0:
            print("\n🎉 太棒了！所有笔记都已互动完成！")
        else:
            print("\n💪 继续加油！明天继续完成剩余的互动")

        print("\n" + "=" * 70)

    finally:
        print("\n按 Enter 键关闭浏览器连接...")
        input()
        await searcher.close()


def enter_interactive_mode(monitor: AccountMonitor):
    """进入交互模式"""
    print("\n" + "=" * 60)
    print("🤖 智能社交助手 - 交互模式")
    print("=" * 60)

    while True:
        print("\n可用命令:")
        print("  1. 搜索账号")
        print("  2. 添加账号")
        print("  3. 添加笔记")
        print("  4. 查看报告")
        print("  5. 标记互动")
        print("  6. 退出")

        choice = input("\n请选择操作 (1-6): ").strip()

        if choice == '1':
            # 搜索账号
            keyword = input("搜索关键词: ").strip()
            min_followers = int(input("最小粉丝数（默认20）: ") or "20")
            max_followers = int(input("最大粉丝数（默认100）: ") or "100")

            async def search_accounts():
                searcher = XiaohongshuSearcherCDP()
                try:
                    # 连接到已打开的浏览器
                    if not await searcher.connect():
                        print("❌ 连接浏览器失败")
                        return

                    accounts = await searcher.search_accounts(
                        keyword=keyword,
                        max_results=20,
                        min_followers=min_followers,
                        max_followers=max_followers
                    )

                    print("\n搜索结果:")
                    for i, account in enumerate(accounts, 1):
                        print(f"\n[{i}] {account['name']}")
                        print(f"    ID: {account['id']}")
                        print(f"    粉丝: {account['followers']}")

                    if accounts:
                        add_all = input("\n是否添加所有账号到监控列表？(y/n): ").strip().lower()
                        if add_all == 'y':
                            category = input("请输入账号分类（美容院/牙医/瑜伽馆等）: ").strip()
                            for account in accounts:
                                monitor.add_account(account['name'], account['id'], category)
                            print(f"✅ 已添加 {len(accounts)} 个账号")

                    print("\n按Enter键关闭浏览器...")
                    input()

                finally:
                    await searcher.close()

            asyncio.run(search_accounts())

        elif choice == '2':
            # 添加账号
            account_name = input("账号名: ").strip()
            account_id = input("账号ID: ").strip()
            category = input("分类（美容院/牙医/瑜伽馆等）: ").strip()
            monitor.add_account(account_name, account_id, category)

        elif choice == '3':
            # 添加笔记
            account_name = input("账号名: ").strip()
            note_id = input("笔记ID: ").strip()
            note_title = input("笔记标题: ").strip()
            note_url = input("笔记URL: ").strip()
            monitor.add_manual_note(account_name, note_id, note_title, note_url)

        elif choice == '4':
            # 查看报告
            report_gen = DailyReport(monitor)
            report_content = report_gen.generate()
            print("\n" + report_content)

            save = input("\n是否保存报告？(y/n): ").strip().lower()
            if save == 'y':
                report_gen.save_to_file()

        elif choice == '5':
            # 标记互动
            account_name = input("账号名: ").strip()
            note_id = input("笔记ID: ").strip()
            interaction_type = input("互动类型（点赞/评论/收藏）: ").strip()
            monitor.mark_interacted(account_name, note_id, interaction_type)

        elif choice == '6':
            print("\n👋 再见！")
            break

        else:
            print("\n⚠️  无效选择")


if __name__ == "__main__":
    main()
