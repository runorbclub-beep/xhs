#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动添加真实商家账号
"""
import json
import sys
from pathlib import Path
from datetime import datetime


def add_account_manually():
    """手动添加账号"""
    print("=" * 70)
    print("📝 手动添加真实商家账号")
    print("=" * 70)

    # 读取当前列表
    accounts_file = Path(__file__).parent / "data" / "monitored_accounts.json"
    with open(accounts_file, 'r', encoding='utf-8') as f:
        accounts = json.load(f)

    print(f"\n当前监控账号数: {len(accounts)}")
    print("\n添加新账号（输入 q 退出）")

    count = 0

    while True:
        print("\n" + "-" * 70)

        # 输入账号名
        account_name = input("\n账号名/店铺名: ").strip()

        if account_name.lower() == 'q':
            break

        if not account_name:
            print("⚠️  账号名不能为空")
            continue

        # 输入账号ID（可选）
        account_id = input("账号ID (可选，按Enter跳过): ").strip()

        if not account_id:
            account_id = f"manual_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 选择分类
        print("\n选择分类:")
        print("1. 牙医")
        print("2. 美容院")
        print("3. 按摩店")
        print("4. 养生馆")
        print("5. 美甲店")
        print("6. 其他")

        category_choice = input("请选择 (1-6): ").strip()

        category_map = {
            '1': '牙医',
            '2': '美容院',
            '3': '按摩店',
            '4': '养生馆',
            '5': '美甲店',
            '6': '其他'
        }

        category = category_map.get(category_choice, '其他')

        # 添加到列表
        accounts[account_name] = {
            'id': account_id,
            'category': category,
            'added_date': datetime.now().strftime('%Y-%m-%d'),
            'added_by': 'manual',
            'last_check': None,
            'notes': []
        }

        count += 1
        print(f"\n✅ 已添加: {account_name} ({category})")

        # 询问是否继续
        continue_add = input("\n继续添加？(y/n): ").strip().lower()
        if continue_add != 'y':
            break

    # 保存
    with open(accounts_file, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"✅ 完成！共添加 {count} 个账号")
    print(f"   总账号数: {len(accounts)}")
    print("=" * 70)

    # 显示所有账号
    print("\n📋 当前监控账号列表:")
    print("-" * 70)

    # 按分类分组
    categories = {}
    for name, info in accounts.items():
        cat = info['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(name)

    for cat, names in categories.items():
        print(f"\n【{cat}】({len(names)} 个)")
        for i, name in enumerate(names[:5], 1):
            print(f"  {i}. {name}")
        if len(names) > 5:
            print(f"  ... 还有 {len(names) - 5} 个")


if __name__ == "__main__":
    try:
        add_account_manually()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
