#!/usr/bin/env python3
"""
监控批量评估进度
"""

import json
import time
from pathlib import Path

RESULT_FILE = Path("results/iedr_batch_results.json")
TOTAL_SCRIPTS = 100
CHECK_INTERVAL = 5  # 每5秒检查一次

def get_progress():
    """获取当前进度"""
    try:
        if RESULT_FILE.exists():
            with open(RESULT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data)
        return 0
    except Exception as e:
        return -1

def main():
    """主函数"""
    print("=" * 70)
    print("📊 EPJ批量评估进度监控")
    print("=" * 70)
    print(f"目标: {TOTAL_SCRIPTS} 个剧本")
    print(f"检查间隔: {CHECK_INTERVAL} 秒")
    print("按 Ctrl+C 停止监控")
    print("=" * 70)
    print()
    
    last_count = 0
    start_time = time.time()
    
    try:
        while True:
            current_count = get_progress()
            
            if current_count >= 0:
                if current_count != last_count:
                    elapsed = time.time() - start_time
                    elapsed_min = int(elapsed // 60)
                    elapsed_sec = int(elapsed % 60)
                    
                    if current_count > 0:
                        avg_time = elapsed / current_count
                        remaining = (TOTAL_SCRIPTS - current_count) * avg_time
                        remaining_min = int(remaining // 60)
                        remaining_sec = int(remaining % 60)
                        
                        print(f"[{elapsed_min:02d}:{elapsed_sec:02d}] "
                              f"进度: {current_count}/{TOTAL_SCRIPTS} "
                              f"({current_count/TOTAL_SCRIPTS*100:.1f}%) | "
                              f"平均: {avg_time:.1f}s/个 | "
                              f"预计剩余: {remaining_min:02d}:{remaining_sec:02d}")
                    else:
                        print(f"[{elapsed_min:02d}:{elapsed_sec:02d}] "
                              f"进度: {current_count}/{TOTAL_SCRIPTS} (0.0%)")
                    
                    last_count = current_count
                    
                    if current_count >= TOTAL_SCRIPTS:
                        print()
                        print("=" * 70)
                        print("🎉 批量评估已完成！")
                        print("=" * 70)
                        break
            else:
                print(f"⚠️ 无法读取结果文件")
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("⏸️  监控已停止")
        print(f"最终进度: {last_count}/{TOTAL_SCRIPTS} ({last_count/TOTAL_SCRIPTS*100:.1f}%)")
        print("=" * 70)

if __name__ == "__main__":
    main()

