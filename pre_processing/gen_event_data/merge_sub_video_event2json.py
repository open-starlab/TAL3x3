import os
import json
import re
import glob


def merge_json_files_flat(input_folder, output_json_path):
    """
    合并文件夹中的所有JSON文件到一个扁平结构的JSON文件，并按时间帧排序

    参数:
        input_folder: 包含JSON文件的文件夹路径
        output_json_path: 输出JSON文件的路径
    """
    # 创建用于存储合并结果的字典
    merged_data = {}

    # 查找输入文件夹中所有.json文件
    json_files = glob.glob(os.path.join(input_folder, "*.json"))

    # 正则表达式匹配文件名格式为IMG_videoid_start_end_events.json
    pattern = r"(IMG_\d+_\d+_\d+)_events\.json"

    for json_file in json_files:
        # 从文件名中提取键值
        filename = os.path.basename(json_file)
        match = re.match(pattern, filename)

        if match:
            key = match.group(1)  # 键值为IMG_videoid_start_end

            try:
                # 读取JSON文件内容
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_content = json.load(f)

                # 按照开始帧排序事件
                sorted_events = sorted(json_content, key=lambda x: x['start_frame'])

                # 将键值和排序后的内容添加到结果字典中
                merged_data[key] = sorted_events

                print(f"已成功处理文件: {filename}")
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")
        else:
            print(f"跳过文件 {filename} - 不匹配命名格式")

    # 将合并结果写入输出JSON文件
    try:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=4)

        print(f"合并完成！已将结果保存到: {output_json_path}")
        print(f"共合并了 {len(merged_data)} 个JSON文件的内容")
    except Exception as e:
        print(f"保存合并结果时出错: {str(e)}")


# 使用示例
if __name__ == "__main__":
    # 替换以下路径为实际路径
    # input_folder = "/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/events_raw/train"
    # output_json_path = "/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/gt_events_train.json"
    input_folder = "/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/events_raw/val"
    output_json_path = "/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/gt_events_val.json"

    merge_json_files_flat(input_folder, output_json_path)