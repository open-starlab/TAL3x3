import json
import os
import glob


def merge_json_files(folder_path: str, output_path) -> str:
    """
    合并文件夹中的所有JSON文件

    参数:
        folder_path (str): 包含JSON文件的文件夹路径

    返回:
        str: 合并后的JSON文件路径
    """

    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        raise ValueError(f"文件夹不存在: {folder_path}")

    # 获取所有JSON文件
    json_files = glob.glob(os.path.join(folder_path, "*.json"))

    if not json_files:
        raise ValueError(f"在 {folder_path} 中未找到JSON文件")

    merged_data = {}
    processed_files = 0

    print(f"找到 {len(json_files)} 个JSON文件，开始合并...")

    # 逐个处理JSON文件
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict):
                # 合并数据
                for key, value in data.items():
                    if key in merged_data:
                        print(f"警告: 发现重复键 '{key}' - 覆盖旧值")
                    merged_data[key] = value

                processed_files += 1
                print(f"已处理: {os.path.basename(file_path)}")

            else:
                print(f"跳过 {file_path}: 数据格式不正确")

        except json.JSONDecodeError:
            print(f"跳过 {file_path}: JSON格式错误")
        except Exception as e:
            print(f"处理 {file_path} 时出错: {e}")

    # 保存合并结果

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)

        print(f"\n合并完成!")
        print(f"成功合并 {processed_files} 个文件")
        print(f"输出文件: {output_path}")
        print(f"总键数: {len(merged_data)}")

        return output_path

    except Exception as e:
        raise RuntimeError(f"保存合并文件失败: {e}")


# 使用示例
if __name__ == "__main__":
    # 使用方法很简单：输入文件夹路径，返回合并后的JSON文件路径
    # 合并当前目录下的JSON文件
    input_json_file_folder = "/work6/q_hu/AG/RKU_TAL/HHIDataset/annotation/skeletons/train"
    json_path = "/work6/q_hu/AG/RKU_TAL/HHIDataset/annotation/gt_skeleton_hhi_train.json"
    # input_json_file_folder = "/work6/q_hu/AG/RKU_TAL/HHIDataset/annotation/skeletons/val"
    # json_path = "/work6/q_hu/AG/RKU_TAL/HHIDataset/annotation/gt_skeleton_hhi_val.json"
    merge_json_files(input_json_file_folder, json_path)
    print(f"合并文件保存在: {json_path}")

    # 或者合并指定文件夹的JSON文件
    # json_path = merge_json_files("./val")
    # json_path = merge_json_files("/path/to/your/json/folder")
