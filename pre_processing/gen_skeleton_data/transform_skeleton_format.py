import json
import os


def change_json_format(input_path, output_path):
    # 读取JSON文件
    with open(input_path, 'r') as f:
        data = json.load(f)

    # 创建新字典用于存储重组后的数据
    new_data = {}

    # 图像尺寸用于归一化
    # width, height = 3840, 2160
    width, height = 1280, 720

    # 遍历instance_info中的每个帧
    for frame in data['instance_info']:
        # 获取文件名前缀和帧号
        filename = frame['json_key'].split(',')[0]
        count = int(frame['json_key'].split(',')[1])

        # 生成新的键名，格式为"文件名,xxxx"，其中xxxx是四位数计数
        new_key = f"{filename},{count:05d}"

        # 创建一个列表来保存该帧中所有实例的关键点信息
        frame_keypoints = []

        # 遍历该帧中的所有实例
        for instance in frame['instances']:
            # 将keypoints和keypoint_scores组合成17*3的列表
            instance_keypoints = []
            for j in range(17):
                x, y = instance['keypoints'][j]
                # 归一化坐标
                x = x / width
                y = y / height
                score = instance['keypoint_scores'][j]
                instance_keypoints.append([x, y, score])

            # 将这个实例的关键点列表添加到帧关键点列表中
            frame_keypoints.append(instance_keypoints)

        # 将该帧的所有实例关键点数据添加到新字典中
        new_data[new_key] = frame_keypoints

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 将新字典写入到新的JSON文件
    with open(output_path, 'w') as f:
        json.dump(new_data, f, indent=4)

    return len(new_data)


def process_all_files(input_dir, output_dir):
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 统计处理文件数和总帧数
    file_count = 0
    total_frames = 0

    # 遍历输入目录中所有JSON文件
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename)
            print(output_file)

            try:
                frames = change_json_format(input_file, output_file)
                file_count += 1
                total_frames += frames
                print(f"已处理: {filename} - {frames}个帧")
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")

    print(f"所有处理完成！共处理了{file_count}个文件，总计{total_frames}个帧。")


if __name__ == '__main__':
    # input_dir = '/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/skeleton_mmpose_format'
    # output_dir = '/work6/q_hu/AG/SportsHHI/cnn_method/RKU_dataset/annotations/skeletons'
    # process_all_files(input_dir, output_dir)

    # input_dir = '/work6/q_hu/AG/RKU_TAL/HHIDataset/annotation/skeleton_mmpose_format/demo_hhi_train'
    # output_dir = '/work6/q_hu/AG/RKU_TAL/HHIDataset/annotation/skeletons/train'
    input_dir = '/work6/q_hu/AG/RKU_TAL/HHIDataset/annotation/skeleton_mmpose_format/demo_hhi_val'
    output_dir = '/work6/q_hu/AG/RKU_TAL/HHIDataset/annotation/skeletons/val'
    process_all_files(input_dir, output_dir)