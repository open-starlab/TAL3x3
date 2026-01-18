import json
import sys
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# 事件类别映射
EVENT_CATEGORIES = {
    1: 'Pass',
    2: 'DribbleSteal',
    3: 'Shot',
    4: 'InterShot',
    5: 'Rebound',
    6: 'Drive',
    7: 'Dribble',
    8: 'PassSteal'
}


def count_frames_by_category(json_file_path):
    """
    统计JSON文件中每个事件类别的持续帧数

    Args:
        json_file_path (str): JSON文件路径

    Returns:
        tuple: (总帧数, 各类别帧数字典)
    """

    # 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_frames = 0
    total_events = 0
    category_frames = defaultdict(int)
    category_counts = defaultdict(int)

    # 遍历所有视频片段和事件
    for video_segment, events in data.items():
        for event in events:
            duration = event['end_frame'] - event['start_frame']
            event_type = event['event_type']

            total_frames += duration
            total_events += 1
            category_frames[event_type] += duration
            category_counts[event_type] += 1

    # 输出总体统计
    print(f"📊 总体统计:")
    print(f"   总事件数: {total_events}")
    print(f"   总持续帧数: {total_frames}")
    print(f"   平均每事件帧数: {total_frames / total_events:.2f}")

    # 输出各类别统计
    print(f"\n📈 各事件类别统计:")
    sorted_categories = sorted(category_frames.items())

    for event_type, frames in sorted_categories:
        category_name = EVENT_CATEGORIES.get(event_type, f"Unknown_{event_type}")
        count = category_counts[event_type]
        percentage = (frames / total_frames) * 100
        avg_duration = frames / count

        print(
            f"   {category_name} (类别{event_type}): {frames} 帧 ({percentage:.1f}%) | {count} 个事件 | 平均 {avg_duration:.1f} 帧/事件")

    return total_frames, dict(category_frames)


def plot_category_frames(category_frames, save_path=None):
    """
    绘制各类别帧数的柱状图（对数坐标）

    Args:
        category_frames (dict): 各类别帧数字典
        save_path (str, optional): 保存图片的路径
    """

    # 准备数据
    categories = []
    frames = []

    for event_type, frame_count in category_frames.items():
        category_name = EVENT_CATEGORIES.get(event_type, f"Unknown_{event_type}")
        categories.append(category_name)
        frames.append(frame_count)

    # 按帧数从高到低排序
    sorted_data = sorted(zip(categories, frames), key=lambda x: x[1], reverse=True)
    categories, frames = zip(*sorted_data)

    # 设置图表样式
    plt.figure(figsize=(12, 8))
    plt.rcParams['font.family'] = 'sans-serif'

    # 创建柱状图
    bars = plt.bar(range(len(categories)), frames, color='steelblue', alpha=0.8, width=0.5, edgecolor='none')

    # 设置对数坐标
    plt.yscale('log')

    # 设置标签和标题
    # plt.xlabel('Event Categories', fontsize=12)
    plt.ylabel('# instances per class', fontsize=12)
    # plt.title('Event Category Frame Distribution', fontsize=14, fontweight='bold')

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # 设置x轴标签
    plt.xticks(range(len(categories)), categories, rotation=45, ha='right')

    # 设置网格
    plt.grid(True, alpha=0.3, axis='y')

    # 在柱子上添加数值标签
    for i, (bar, value) in enumerate(zip(bars, frames)):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.1,
                 str(value), ha='center', va='bottom', fontsize=9)

    # 调整布局
    plt.tight_layout()

    # 保存或显示图表
    if save_path:
        plt.savefig(save_path, dpi=600, bbox_inches='tight')
        print(f"📊 图表已保存到: {save_path}")

    plt.show()


def count_total_frames(json_file_path):
    """
    简单版本：只统计总帧数（保持向后兼容）
    """
    total, _ = count_frames_by_category(json_file_path)
    return total


# 使用方法
if __name__ == "__main__":
    json_file = "/work6/q_hu/AG/RKU_TAL/cnn_method/RKU_dataset/annotations/gt_events.json"

    try:
        total, category_data = count_frames_by_category(json_file)

        print(f"\n✅ 所有事件总计持续 {total} 帧")
        print(f"✅ 共有 {len(category_data)} 种事件类别")

        # 显示占比最高的类别
        if category_data:
            max_category = max(category_data.items(), key=lambda x: x[1])
            max_category_name = EVENT_CATEGORIES.get(max_category[0], f"Unknown_{max_category[0]}")
            max_percentage = (max_category[1] / total) * 100
            print(f"🏆 占比最高: {max_category_name} ({max_category[1]} 帧, {max_percentage:.1f}%)")

            # 绘制图表
            print(f"\n📊 正在生成图表...")
            plot_category_frames(category_data, f"event_frame_distribution.png")

    except FileNotFoundError:
        print(f"❌ 文件 '{json_file}' 不存在")
    except Exception as e:
        print(f"❌ 错误: {e}")


# 快速使用函数
def quick_count(json_path):
    """一行代码统计总帧数"""
    return count_total_frames(json_path)


def quick_analysis(json_path):
    """一行代码获取详细分析"""
    return count_frames_by_category(json_path)


def quick_plot(json_path, save_path=None):
    """一行代码生成图表"""
    _, category_data = count_frames_by_category(json_path)
    plot_category_frames(category_data, save_path)
    return category_data









