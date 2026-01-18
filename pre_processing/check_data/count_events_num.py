import json


def analyze_events(json_file_path):
    # 读取JSON文件
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # 统计总事件数
    total_events = 0
    event_types = {}
    video_segments = {}

    # 遍历所有视频片段
    for segment_name, events in data.items():
        segment_event_count = len(events)
        total_events += segment_event_count
        video_segments[segment_name] = segment_event_count

        # 按事件类型统计
        for event in events:
            event_type = event.get("event_type")
            if event_type in event_types:
                event_types[event_type] += 1
            else:
                event_types[event_type] = 1

    # 输出统计结果
    print(f"总事件数: {total_events}")

    print("\n按事件类型统计:")
    for event_type, count in sorted(event_types.items()):
        print(f"事件类型 {event_type}: {count}个事件")

    print("\n每个视频片段的事件数量前10:")
    sorted_segments = sorted(video_segments.items(), key=lambda x: x[1], reverse=True)
    for segment, count in sorted_segments[:10]:
        print(f"{segment}: {count}个事件")

    return total_events, event_types, video_segments


# 使用示例
# 假设JSON文件保存为gt_events_train.json
file_path = '/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/gt_events_train.json'
total, by_type, by_segment = analyze_events(file_path)