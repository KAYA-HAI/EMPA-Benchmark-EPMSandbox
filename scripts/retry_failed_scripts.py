#!/usr/bin/env python3
"""
重新评估失败的剧本并更新结果文件
"""

import json
import time
from pathlib import Path
from datetime import datetime

# 导入必要的模块
from Benchmark.agents.judger import Judger
from Benchmark.topics.config_loader import ConfigLoader

# 配置
RESULT_FILE = Path("results/iedr_batch_results.json")
MODEL_NAME = "google/gemini-2.5-pro"

def load_results():
    """加载现有结果"""
    with open(RESULT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_results(data):
    """保存结果"""
    with open(RESULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def evaluate_single_script(script_id: str, judger: Judger, config_loader: ConfigLoader):
    """评估单个剧本"""
    print(f"\n{'='*70}")
    print(f"📝 重新评估剧本: {script_id}")
    print(f"{'='*70}")
    
    try:
        # 提取数字ID（例如 "script_012" -> "012"）
        numeric_id = script_id.split('_')[1]
        
        # 加载剧本配置
        config = config_loader.load_config(numeric_id)
        
        print(f"✅ 已加载剧本配置")
        
        # 构造script_content
        script_content = {
            'actor_prompt': config['actor_prompt'],
            'scenario': config['scenario']
        }
        
        # 填写IEDR
        print(f"🤖 调用Judger进行IEDR评估...")
        iedr_result = judger.fill_iedr(script_content)
        
        if iedr_result:
            print(f"✅ IEDR评估成功")
            print(f"📊 评估结果:")
            print(f"   C.1={iedr_result.get('C.1')}, C.2={iedr_result.get('C.2')}, C.3={iedr_result.get('C.3')}")
            print(f"   A.1={iedr_result.get('A.1')}, A.2={iedr_result.get('A.2')}, A.3={iedr_result.get('A.3')}")
            print(f"   P.1={iedr_result.get('P.1')}, P.2={iedr_result.get('P.2')}, P.3={iedr_result.get('P.3')}")
            
            # 计算初始赤字向量
            from Benchmark.epj.scoring import calculate_initial_deficit
            P_0_tuple = calculate_initial_deficit(iedr_result)
            
            # 转换为dict格式
            P_0 = {
                "C": P_0_tuple[0],
                "A": P_0_tuple[1],
                "P": P_0_tuple[2],
                "total": sum(P_0_tuple)
            }
            
            print(f"📐 初始赤字向量 P_0:")
            print(f"   C={P_0['C']}, A={P_0['A']}, P={P_0['P']}")
            print(f"   总赤字 = {P_0['total']}")
            
            return {
                'script_id': script_id,
                'status': 'success',
                'iedr': iedr_result,
                'P_0': P_0,
                'timestamp': datetime.now().isoformat()
            }
        else:
            print(f"❌ IEDR评估失败")
            return {
                'script_id': script_id,
                'status': 'error',
                'error': 'IEDR评估返回None',
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"❌ 评估失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'script_id': script_id,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def retry_failed_scripts():
    """重新评估失败的剧本"""
    print("=" * 80)
    print("🔄 重新评估失败的剧本")
    print("=" * 80)
    
    # 加载现有结果
    print("\n📂 加载现有结果...")
    results = load_results()
    
    # 找出失败的剧本
    failed_items = [item for item in results if item['status'] == 'error']
    failed_script_ids = [item['script_id'] for item in failed_items]
    
    print(f"\n❌ 发现 {len(failed_items)} 个失败的剧本:")
    for script_id in failed_script_ids:
        print(f"   - {script_id}")
    
    if not failed_items:
        print("\n✅ 没有失败的剧本需要重新评估")
        return
    
    # 初始化
    print("\n🔧 初始化Judger和ConfigLoader...")
    judger = Judger(model_name=MODEL_NAME)
    config_loader = ConfigLoader()
    
    # 重新评估失败的剧本
    print(f"\n🚀 开始重新评估...")
    retry_results = []
    
    for script_id in failed_script_ids:
        result = evaluate_single_script(script_id, judger, config_loader)
        retry_results.append(result)
        
        # 稍微延迟，避免API限流
        if result['status'] == 'success':
            print(f"⏱️  等待3秒...")
            time.sleep(3)
    
    # 更新结果
    print(f"\n💾 更新结果文件...")
    
    # 创建script_id到索引的映射
    script_to_idx = {item['script_id']: idx for idx, item in enumerate(results)}
    
    # 更新失败剧本的结果
    for retry_result in retry_results:
        script_id = retry_result['script_id']
        idx = script_to_idx[script_id]
        results[idx] = retry_result
    
    # 保存更新后的结果
    save_results(results)
    
    # 统计
    success_count = sum(1 for r in retry_results if r['status'] == 'success')
    error_count = sum(1 for r in retry_results if r['status'] == 'error')
    
    print("\n" + "=" * 80)
    print("📊 重新评估完成")
    print("=" * 80)
    print(f"\n重新评估结果:")
    print(f"  ✅ 成功: {success_count}/{len(retry_results)}")
    print(f"  ❌ 仍然失败: {error_count}/{len(retry_results)}")
    
    if error_count > 0:
        print(f"\n⚠️  以下剧本仍然失败:")
        for r in retry_results:
            if r['status'] == 'error':
                print(f"   - {r['script_id']}: {r['error']}")
    
    # 最终统计
    total_success = sum(1 for item in results if item['status'] == 'success')
    total_error = sum(1 for item in results if item['status'] == 'error')
    
    print(f"\n最终统计:")
    print(f"  总计: {len(results)}")
    print(f"  ✅ 成功: {total_success} ({total_success/len(results)*100:.1f}%)")
    print(f"  ❌ 失败: {total_error} ({total_error/len(results)*100:.1f}%)")
    
    print(f"\n✅ 结果已更新到: {RESULT_FILE}")


if __name__ == "__main__":
    retry_failed_scripts()

