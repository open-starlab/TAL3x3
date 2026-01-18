#!/usr/bin/env python3
import os
import sys
from pathlib import Path


def count_files_in_directories(base_path='.', pattern=None):
    """
    统计指定路径下每个文件夹中的文件数量

    Args:
        base_path: 基础路径，默认当前目录
        pattern: 文件夹名称模式，如 'IMG_0106' 只统计匹配的文件夹
    """

    base_path = Path(base_path)

    if not base_path.exists():
        print(f"错误: 路径 '{base_path}' 不存在")
        return

    # 获取所有子目录
    directories = [d for d in base_path.iterdir() if d.is_dir()]

    # 如果指定了模式，只处理匹配的目录
    if pattern:
        directories = [d for d in directories if pattern in d.name]

    # 按名称排序
    directories = sorted(directories, key=lambda x: x.name)

    if not directories:
        print("未找到任何文件夹")
        return

    print("=" * 60)
    print(f"文件夹统计结果 (基础路径: {base_path.absolute()})")
    print("=" * 60)

    total_files = 0
    file_counts = []  # 存储每个文件夹的文件数量用于统计

    for directory in directories:
        try:
            # 统计文件夹中的文件数量（不包括子文件夹）
            files = [f for f in directory.iterdir() if f.is_file()]
            file_count = len(files)
            total_files += file_count
            file_counts.append(file_count)

            print(f"{directory.name:<30} : {file_count:>5} 个文件")

        except PermissionError:
            print(f"{directory.name:<30} : 权限拒绝")
        except Exception as e:
            print(f"{directory.name:<30} : 错误 - {e}")

    print("-" * 60)
    print(f"{'总计':<30} : {total_files:>5} 个文件")
    print(f"{'文件夹数量':<30} : {len(directories):>5} 个")

    # 计算统计信息
    if file_counts:
        avg_files = total_files / len(directories)
        max_files = max(file_counts)
        min_files = min(file_counts)

        # 计算中位数
        sorted_counts = sorted(file_counts)
        n = len(sorted_counts)
        if n % 2 == 0:
            median_files = (sorted_counts[n // 2 - 1] + sorted_counts[n // 2]) / 2
        else:
            median_files = sorted_counts[n // 2]

        # 计算标准差
        variance = sum((x - avg_files) ** 2 for x in file_counts) / len(file_counts)
        std_dev = variance ** 0.5

        print("-" * 60)
        print("统计信息:")
        print(f"{'平均文件数量':<30} : {avg_files:>8.2f} 个")
        print(f"{'中位数':<30} : {median_files:>8.2f} 个")
        print(f"{'最大文件数量':<30} : {max_files:>5} 个")
        print(f"{'最小文件数量':<30} : {min_files:>5} 个")
        print(f"{'标准差':<30} : {std_dev:>8.2f}")

        # 找出文件数量最多和最少的文件夹
        max_folder = directories[file_counts.index(max_files)].name
        min_folder = directories[file_counts.index(min_files)].name
        print(f"{'文件数量最多的文件夹':<30} : {max_folder}")
        print(f"{'文件数量最少的文件夹':<30} : {min_folder}")

    print("=" * 60)


def count_files_recursive(base_path='.', pattern=None):
    """
    递归统计文件夹中的文件数量（包括子文件夹）
    """

    base_path = Path(base_path)

    if not base_path.exists():
        print(f"错误: 路径 '{base_path}' 不存在")
        return

    directories = [d for d in base_path.iterdir() if d.is_dir()]

    if pattern:
        directories = [d for d in directories if pattern in d.name]

    directories = sorted(directories, key=lambda x: x.name)

    if not directories:
        print("未找到任何文件夹")
        return

    print("\n" + "=" * 60)
    print("递归统计结果 (包括子文件夹)")
    print("=" * 60)

    total_files = 0

    for directory in directories:
        try:
            # 递归统计所有文件
            files = list(directory.rglob('*'))
            file_count = len([f for f in files if f.is_file()])
            total_files += file_count

            print(f"{directory.name:<30} : {file_count:>5} 个文件 (递归)")

        except PermissionError:
            print(f"{directory.name:<30} : 权限拒绝")
        except Exception as e:
            print(f"{directory.name:<30} : 错误 - {e}")

    print("-" * 60)
    print(f"{'总计':<30} : {total_files:>5} 个文件 (递归)")


def show_file_details(base_path='.', pattern=None, show_extensions=True):
    """
    显示更详细的文件信息，包括文件类型统计
    """

    base_path = Path(base_path)
    directories = [d for d in base_path.iterdir() if d.is_dir()]

    if pattern:
        directories = [d for d in directories if pattern in d.name]

    directories = sorted(directories, key=lambda x: x.name)

    print("\n" + "=" * 60)
    print("详细文件信息")
    print("=" * 60)

    for directory in directories:
        try:
            files = [f for f in directory.iterdir() if f.is_file()]

            if show_extensions and files:
                # 统计文件扩展名
                extensions = {}
                for file in files:
                    ext = file.suffix.lower() if file.suffix else '无扩展名'
                    extensions[ext] = extensions.get(ext, 0) + 1

                print(f"\n{directory.name}:")
                print(f"  总文件数: {len(files)}")
                print("  文件类型:")
                for ext, count in sorted(extensions.items()):
                    print(f"    {ext:<10}: {count} 个")
            else:
                print(f"{directory.name:<30} : {len(files)} 个文件")

        except Exception as e:
            print(f"{directory.name}: 错误 - {e}")


if __name__ == "__main__":


    # 可以通过命令行参数指定路径
    base_path = "/work6/q_hu/AG/RKU_TAL/cnn_method/RKU_dataset/annotations/rawframes"

    # 基本统计
    count_files_in_directories(base_path)

    # # 递归统计
    # count_files_recursive(base_path, pattern='IMG_0106')
    #
    # # 详细信息
    # show_file_details(base_path, pattern='IMG_0106')

    print("\n使用说明:")
    print("1. 将此脚本保存为 count_files.py")
    print("2. 在包含文件夹的目录下运行: python3 count_files.py")
    print("3. 或指定路径: python3 count_files.py /path/to/your/directory")