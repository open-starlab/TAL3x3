import json


def remove_duplicate_frames(input_file, output_file):
    # 读取JSON文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"原始数据条数: {len(data)}")

    # 用于存储去重后的数据
    # 键 (Key): (frame_id, player_ids, event_type)
    # 值 (Value): 该键对应的置信度最高的数据条目
    unique_events = {}

    for entry in data:
        frame_id = entry['frame_id']
        # 将列表转换为元组以便作为字典的键，并排序以忽略玩家ID顺序的影响 (如 [1,2] 和 [2,1] 视为相同)
        player_ids = tuple(sorted(entry['player_ids']))
        event_type = entry['event_type']

        # 组合唯一键：帧ID + 玩家组合 + 事件类型
        key = (frame_id, player_ids, event_type)

        # 如果该键已存在，比较置信度，保留较高的那个
        if key in unique_events:
            if entry['confidence'] > unique_events[key]['confidence']:
                unique_events[key] = entry
        else:
            unique_events[key] = entry

    # 将字典的值转回列表
    cleaned_data = list(unique_events.values())

    # 按 frame_id 排序，保持时间顺序
    cleaned_data.sort(key=lambda x: x['frame_id'])

    # 保存结果到新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

    print(f"清洗后数据条数: {len(cleaned_data)}")
    print(f"已移除重复条数: {len(data) - len(cleaned_data)}")
    print(f"结果已保存至: {output_file}")


# 使用示例
input_filename = 'IMG_0113_7569_8026.json'  # 输入文件名
output_filename = 'IMG_0113_7569_8026_cleaned.json'  # 输出文件名

remove_duplicate_frames(input_filename, output_filename)