#!/usr/bin/env python3
"""
批量修改 character_setting 中的所有 script_XXX.md 文件
添加功能：
1. 在文件开头添加"绝对禁止重复"的约束板块
"""

import os
from pathlib import Path

# 反重复约束板块（从 script_001.md 提取）
ANTI_REPETITION_HEADER = """## 🚨🚨🚨 最高优先级约束：绝对禁止重复 🚨🚨🚨

**这是你必须遵守的铁律，违反即视为任务失败：**

1. ❌ **绝对禁止**重复你在之前任何轮次说过的：
   - 相同的话、句子、表达
   - 相同的例子、故事细节
   - 相同的情绪描述方式
   - 相同的反问句式

2. ✅ **即使讲同一段经历，也必须**：
   - 挖掘新的细节（不同的场景片段）
   - 展现新的情绪层次（从愤怒到委屈到自我怀疑等）
   - 提供新的视角（从"我当时"到"现在回想"到"这让我明白"）
   - 引入新的反思或联想

3. ✅ **每轮回复前必须检查**：
   □ 仔细阅读完整对话历史
   □ 确认这一轮的内容与之前所有轮次都不重复
   □ 确认引入了新的信息、角度或层面
   □ 确认推进了对话而非原地打转

**记住：重复=失败！每一轮都必须是新的！**

---

"""

def fix_prompt_file(file_path: Path) -> bool:
    """
    修正单个prompt文件
    
    功能：
    1. 检查文件开头是否已有反重复约束
    2. 如果没有，则添加到文件开头
    
    Returns:
        bool: 是否做了修改
    """
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 检查是否已经有反重复约束
        if "🚨🚨🚨 最高优先级约束：绝对禁止重复 🚨🚨🚨" in content:
            print(f"   ⏭️  已存在约束: {file_path.name}")
            return False
        
        # 添加反重复约束到文件开头
        content = ANTI_REPETITION_HEADER + content
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
            
    except Exception as e:
        print(f"❌ 处理 {file_path.name} 时出错: {e}")
        return False


def main():
    """批量处理所有script文件"""
    # 定位目录
    script_dir = Path(__file__).parent
    character_setting_dir = script_dir / "Benchmark" / "topics" / "data" / "character_setting"
    
    if not character_setting_dir.exists():
        print(f"❌ 目录不存在: {character_setting_dir}")
        return
    
    print("=" * 70)
    print("🔧 批量修改 Character Setting Prompts")
    print("=" * 70)
    print(f"\n目标目录: {character_setting_dir}")
    
    # 获取所有 script_*.md 文件
    script_files = sorted(character_setting_dir.glob("script_*.md"))
    
    if not script_files:
        print("\n❌ 没有找到任何 script_*.md 文件")
        return
    
    print(f"\n找到 {len(script_files)} 个文件")
    
    # 统计
    modified_count = 0
    skipped_count = 0
    
    print("\n开始处理...")
    print("-" * 70)
    
    for file_path in script_files:
        was_modified = fix_prompt_file(file_path)
        
        if was_modified:
            print(f"✅ 已修改: {file_path.name}")
            modified_count += 1
        else:
            print(f"⏭️  跳过（无需修改）: {file_path.name}")
            skipped_count += 1
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 处理完成")
    print("=" * 70)
    print(f"总文件数: {len(script_files)}")
    print(f"已修改: {modified_count}")
    print(f"跳过: {skipped_count}")
    print("\n✅ 所有文件已处理完成！")
    
    if modified_count > 0:
        print("\n💡 下一步:")
        print("1. 检查修改是否正确（可以用 git diff 查看）")
        print("2. 删除 Actor.set_system_prompt() 中的预处理代码")
        print("3. 测试运行确保一切正常")


if __name__ == "__main__":
    main()

