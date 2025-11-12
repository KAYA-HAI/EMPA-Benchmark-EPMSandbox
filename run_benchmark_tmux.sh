#!/bin/bash
#
# 使用 tmux 在后台运行完整的 30 个测试案例
# 即使断开 SSH 连接，测试也会继续运行
#

# 设置 tmux 会话名称
SESSION_NAME="benchmark_test"

# 检查是否已经存在同名会话
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "⚠️  tmux 会话 '$SESSION_NAME' 已存在"
    echo ""
    echo "选择操作："
    echo "  1. 连接到现有会话查看进度：tmux attach -t $SESSION_NAME"
    echo "  2. 终止旧会话并创建新的：tmux kill-session -t $SESSION_NAME && bash $0"
    exit 1
fi

# 创建新的 tmux 会话并运行测试
echo "🚀 创建 tmux 会话: $SESSION_NAME"
echo "📋 将运行 30 个测试案例（预计需要数小时）"
echo ""

# 创建 detached 会话并执行命令
tmux new-session -d -s $SESSION_NAME -c "$(pwd)" "python3 run_benchmark_custom_model.py 2>&1 | tee benchmark_run_$(date +%Y%m%d_%H%M%S).log"

echo "✅ tmux 会话已启动！"
echo ""
echo "📌 常用命令："
echo "  查看运行状态：tmux attach -t $SESSION_NAME"
echo "  断开连接（保持运行）：按 Ctrl+B 然后按 D"
echo "  终止运行：tmux kill-session -t $SESSION_NAME"
echo ""
echo "💡 提示："
echo "  - 测试会在后台持续运行，即使关闭终端窗口也不会中断"
echo "  - 日志会实时保存到 benchmark_run_*.log 文件"
echo "  - 结果会保存到 results/benchmark_runs/ 目录"
echo ""
echo "🔍 现在连接到会话查看运行状态..."
sleep 2
tmux attach -t $SESSION_NAME

