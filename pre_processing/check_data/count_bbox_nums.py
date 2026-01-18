import json
import sys
from typing import Dict, List, Any


def count_bboxes_in_json(json_path: str) -> Dict[str, Any]:
    """
    统计JSON文件中bbox的数量

    Args:
        json_path: JSON文件路径

    Returns:
        包含统计信息的字典
    """
    total_bboxes = 0
    total_images = 0
    image_bbox_counts = {}

    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 遍历JSON数据
        for image_id, bbox_data in data.items():
            total_images += 1

            # 计算当前图像的bbox数量
            if isinstance(bbox_data, list):
                # 如果bbox_data是列表，直接计算长度
                bbox_count = len(bbox_data)
            elif isinstance(bbox_data, dict):
                # 如果是字典，查找bbox相关的键
                bbox_count = 0
                for key, value in bbox_data.items():
                    if isinstance(value, list) and key.lower().find('bbox') != -1:
                        bbox_count += len(value)
                    elif isinstance(value, list):
                        # 假设列表就是bbox数据
                        bbox_count += len(value)
            else:
                bbox_count = 0

            image_bbox_counts[image_id] = bbox_count
            total_bboxes += bbox_count

    except FileNotFoundError:
        print(f"错误：找不到文件 {json_path}")
        return None
    except json.JSONDecodeError:
        print(f"错误：{json_path} 不是有效的JSON文件")
        return None
    except Exception as e:
        print(f"错误：处理文件时出现异常 - {e}")
        return None

    return {
        'total_bboxes': total_bboxes,
        'total_images': total_images,
        'average_bboxes_per_image': total_bboxes / total_images if total_images > 0 else 0,
        'image_bbox_counts': image_bbox_counts
    }


def count_bboxes_in_jsonl(jsonl_path: str) -> Dict[str, Any]:
    """
    统计JSONL文件中bbox的数量（每行一个JSON对象）

    Args:
        jsonl_path: JSONL文件路径

    Returns:
        包含统计信息的字典
    """
    total_bboxes = 0
    total_images = 0
    image_bbox_counts = {}

    try:
        with open(jsonl_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    total_images += 1

                    # 从您的截图看，数据格式可能是：image_id: [bbox1, bbox2, ...]
                    bbox_count = 0

                    if isinstance(data, dict):
                        for image_id, bbox_data in data.items():
                            if isinstance(bbox_data, list):
                                # 过滤掉无效的bbox（比如包含"(S)[-]"的项）
                                valid_bboxes = [
                                    bbox for bbox in bbox_data
                                    if isinstance(bbox, list) and
                                       len(bbox) >= 4 and
                                       all(isinstance(coord, (int, float)) for coord in bbox[:4])
                                ]
                                bbox_count += len(valid_bboxes)
                                image_bbox_counts[image_id] = len(valid_bboxes)

                    total_bboxes += bbox_count

                except json.JSONDecodeError:
                    print(f"警告：第{line_num}行不是有效的JSON格式，跳过")
                    continue

    except FileNotFoundError:
        print(f"错误：找不到文件 {jsonl_path}")
        return None
    except Exception as e:
        print(f"错误：处理文件时出现异常 - {e}")
        return None

    return {
        'total_bboxes': total_bboxes,
        'total_images': total_images,
        'average_bboxes_per_image': total_bboxes / total_images if total_images > 0 else 0,
        'image_bbox_counts': image_bbox_counts
    }


def main():
    """主函数"""


    # json_path = "/work6/q_hu/AG/RKU_TAL/cnn_method/RKU_dataset/annotations/gt_bbox_val.json"
    json_path = "/work6/q_hu/AG/RKU_TAL/cnn_method/RKU_dataset/annotations/gt_bbox_train.json"

    # 判断文件类型
    if json_path.endswith('.jsonl'):
        result = count_bboxes_in_jsonl(json_path)
    else:
        result = count_bboxes_in_json(json_path)

    if result is None:
        sys.exit(1)

    # 输出统计结果
    print(f"=== Bbox统计结果 ===")
    print(f"总图像数量: {result['total_images']}")
    print(f"总bbox数量: {result['total_bboxes']}")
    print(f"平均每张图像的bbox数量: {result['average_bboxes_per_image']:.2f}")

    # 显示前10个图像的bbox数量
    print(f"\n=== 前10个图像的bbox数量 ===")
    for i, (image_id, count) in enumerate(result['image_bbox_counts'].items()):
        if i >= 10:
            break
        print(f"{image_id}: {count} bboxes")

    if len(result['image_bbox_counts']) > 10:
        print(f"... 还有 {len(result['image_bbox_counts']) - 10} 个图像")


if __name__ == "__main__":
    main()