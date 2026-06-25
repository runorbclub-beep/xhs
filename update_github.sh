#!/bin/bash
# 更新到GitHub脚本

echo "========================================"
echo "📤 更新到GitHub"
echo "========================================"

# 1. 检查状态
echo "\n📊 检查Git状态..."
git status

# 2. 添加所有更改
echo "\n➕ 添加所有更改..."
git add .

# 3. 询问提交信息
echo "\n📝 请输入提交信息（留空使用默认时间戳）:"
read commit_message

if [ -z "$commit_message" ]; then
    commit_message="Update $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 4. 提交
echo "\n✅ 提交更改: $commit_message"
git commit -m "$commit_message"

# 5. 推送
echo "\n🚀 推送到GitHub..."
git push origin main

echo "\n✅ 更新完成！"
echo "========================================"
