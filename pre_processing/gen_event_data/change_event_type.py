import json
import os


def standardize_events(input_json_path, output_json_path):
    """
    读取JSON文件，标准化事件类型，只保留指定的事件类型，并将事件类型转换为整数

    参数:
        input_json_path: 输入JSON文件的路径
        output_json_path: 输出JSON文件的路径
    """
    # 定义事件类型映射字典
    event_type_dict = {
        "Pass": 1,
        "PassSteal": 2,
        "Shot": 3,
        "InterShot": 4,
        "Rebound": 5,
        "Drive": 6,
        "Dribble": 7,
        "DribbleSteal": 8
    }

    # 定义需要合并的事件类型
    shot_events = ["2PShot", "2PShot miss", "3PShot", "3PShot miss", "FreeThrow"]
    rebound_events = ["DefRebound", "OffRebound"]

    try:
        # 读取输入JSON文件
        with open(input_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 创建新的结果字典
        standardized_data = {}

        # 处理每个视频片段
        for video_key, events in data.items():
            standardized_events = []

            for event in events:
                # 获取原始事件类型
                original_event_type = event['event']

                # 标准化事件类型
                if original_event_type in shot_events:
                    standardized_event_type = "Shot"
                elif original_event_type in rebound_events:
                    standardized_event_type = "Rebound"
                else:
                    standardized_event_type = original_event_type

                # 只保留指定的事件类型
                if standardized_event_type in event_type_dict:
                    # 创建新的事件字典
                    new_event = event.copy()
                    # 将事件类型转换为整数
                    new_event['event'] = event_type_dict[standardized_event_type]
                    # 添加到标准化事件列表
                    standardized_events.append(new_event)

            # 如果有保留的事件，则将其添加到结果字典中
            if standardized_events:
                standardized_data[video_key] = standardized_events

        # 将标准化后的数据写入输出JSON文件
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(standardized_data, f, ensure_ascii=False, indent=4)

        print(f"处理完成！已将标准化后的结果保存到: {output_json_path}")
        print(f"保留的视频片段数量: {len(standardized_data)}")

        # 统计转换后的事件类型数量
        event_counts = {}
        for event_type, event_code in event_type_dict.items():
            count = sum(
                sum(1 for event in events if event['event'] == event_code)
                for events in standardized_data.values()
            )
            event_counts[event_type] = count

        print("各事件类型数量统计:")
        for event_type, count in event_counts.items():
            print(f"  {event_type} ({event_type_dict[event_type]}): {count}")

    except Exception as e:
        print(f"处理失败: {str(e)}")


# 使用示例
if __name__ == "__main__":
    # 替换以下路径为实际路径
    # input_json_path = "/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/gt_events_train_raw.json"
    # output_json_path = "/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/gt_events_train.json"
    input_json_path = "/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/gt_events_val_raw.json"
    output_json_path = "/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/gt_events_val.json"
    standardize_events(input_json_path, output_json_path)