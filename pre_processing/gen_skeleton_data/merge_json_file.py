import os
import json
import argparse
import re


def merge_json_files(input_folder, output_file):
    """
    遍历文件夹，按时间顺序合并JSON事件文件

    Args:
        input_folder: 包含JSON文件的文件夹路径
        output_file: 合并后输出的JSON文件路径

    Returns:
        None
    """
    # 初始化结果字典和文件列表
    merged_data = {}
    json_files = []

    # 使用os.walk遍历文件夹及其子文件夹
    for root, _, files in os.walk(input_folder):
        for file in files:
            # if file.endswith('.json'):
            if file.endswith('.json') and file.startswith('results_IMG_'):
                # 获取完整文件路径
                file_path = os.path.join(root, file)
                # 提取视频ID和时间信息
                match = re.search(r'results_IMG_(\d+)_(\d+)_(\d+)\.json', file)
                if match:
                    video_id = match.group(1)
                    start_time = int(match.group(2))
                    end_time = int(match.group(3))
                    # 将文件信息存储为元组：(视频ID, 开始时间, 结束时间, 文件路径)
                    json_files.append((video_id, start_time, end_time, file_path))

    # 按视频ID和开始时间排序文件
    # 首先按视频ID排序，然后在每个视频ID内按开始时间排序
    json_files.sort(key=lambda x: (x[0], x[1]))

    # 遍历排序后的文件列表
    for video_id, start_time, end_time, file_path in json_files:
        print(f"处理文件：{os.path.basename(file_path)}")

        try:
            # 读取JSON文件内容
            with open(file_path, 'r') as f:
                video_data = json.load(f)

            # 将视频数据合并到结果中
            # 根据示例，每个键使用"IMG_XXXX_YYYY_ZZZZ,FFFF"格式
            # 其中XXXX是视频ID，YYYY_ZZZZ是开始结束时间，FFFF是帧号
            # 这里我们使用文件名中的信息构建键前缀
            key_prefix = f"IMG_{video_id}_{start_time}_{end_time}"

            # 合并数据
            for key, value in video_data.items():
                # 如果键已经完整（包含逗号），则直接使用
                if ',' in key:
                    merged_data[key] = value
                else:
                    # 否则，添加前缀
                    new_key = f"{key_prefix},{key}"
                    merged_data[new_key] = value

        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
            continue

    # 将合并后的数据写入输出文件
    try:
        with open(output_file, 'w') as f:
            json.dump(merged_data, f, indent=4)
        print(f"已成功将 {len(merged_data)} 个事件合并到文件 {output_file}")
    except Exception as e:
        print(f"写入输出文件 {output_file} 失败: {str(e)}")


def main():
    # input_json_folder_path = '/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/skeletons/train'
    # output_json_path = '/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/gt_skeleton_train.json'
    input_json_folder_path = '/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/skeletons/val'
    output_json_path = '/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/gt_skeleton_val.json'
    # 合并JSON文件
    merge_json_files(input_json_folder_path, output_json_path)


if __name__ == '__main__':
    main()