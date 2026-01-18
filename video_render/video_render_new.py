import cv2
import json
import numpy as np
import os

# ================= 配置区域 =================
VIDEO_PATH = 'C:\\Users\\24968\\Desktop\\video_render\\IMG_0113_7569_8026.mp4'  # 请修改为实际视频文件名
OUTPUT_PATH = 'output_4k_corrected.mp4'

GT_JSON_PATH = 'gt_IMG_0113_7569_8026.json'
PRED_JSON_PATH = 'IMG_0113_7569_8026_cleaned.json'
BBOX_JSON_PATH = 'bbox.json'

# 定义事件 ID、名称和颜色 (BGR 格式)
# 对应关系: 1-based Index based on your list
# 1:Pass, 2:DribbleSteal, 3:Shot, 4:InterShot, 5:Rebound, 6:Drive, 7:Dribble, 8:PassSteal, 9:Background
EVENT_MAP = {
    0: {"name": "No Event", "color": (50, 50, 50)},  # 0: 无事件/默认 (深灰)
    1: {"name": "Pass", "color": (0, 0, 255)},  # 1: 红色
    2: {"name": "DribbleSteal", "color": (0, 255, 0)},  # 2: 绿色
    3: {"name": "Shot", "color": (255, 0, 0)},  # 3: 蓝色
    4: {"name": "InterShot", "color": (0, 255, 255)},  # 4: 黄色
    5: {"name": "Rebound", "color": (255, 0, 255)},  # 5: 紫色
    6: {"name": "Drive", "color": (255, 255, 0)},  # 6: 青色
    7: {"name": "Dribble", "color": (0, 165, 255)},  # 7: 橙色
    8: {"name": "PassSteal", "color": (147, 20, 255)},  # 8: 深粉/红紫
    9: {"name": "Background", "color": (200, 200, 200)}  # 9: 浅灰/白
}

DEFAULT_COLOR = (50, 50, 50)

# ================= 4K 分辨率 (3840x2160) 界面布局配置 =================
# 进度条参数
BAR_HEIGHT = 60  # 进度条高度
MARGIN_BOTTOM = 140  # 进度条底部边距
BAR_GAP = 60  # 两个进度条之间的垂直间距

# 图例参数
LEGEND_X_OFFSET = 50  # 图例距离右边的距离
LEGEND_Y_OFFSET = 50  # 图例距离顶部的距离
LEGEND_PADDING = 30  # 图例内边距
LEGEND_LINE_HEIGHT = 70  # 图例每行高度
LEGEND_BOX_SIZE = 40  # 图例色块大小
LEGEND_FONT_SCALE = 1.5  # 图例字体大小
LEGEND_THICKNESS = 3  # 图例字体粗细

# 通用字体参数
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
TEXT_THICKNESS = 3  # 普通文字粗细 (BBox ID等)
TEXT_SCALE = 1.2  # 普通文字大小
FRAME_INFO_SCALE = 2.0  # 左上角帧数文字大小


# ================= 数据解析函数 =================

def parse_frame_id(frame_str):
    """解析 'IMG_...,00123' 格式为整数帧号 123"""
    try:
        return int(frame_str.split(',')[-1])
    except:
        return -1


def load_data():
    # 1. 加载 Ground Truth
    gt_map = {}
    if os.path.exists(GT_JSON_PATH):
        with open(GT_JSON_PATH, 'r') as f:
            gt_data = json.load(f)
            for item in gt_data:
                start = item['start_frame']
                end = item['end_frame']
                evt = item['event_type']
                for i in range(start, end + 1):
                    gt_map[i] = evt
    else:
        print(f"警告: 未找到 {GT_JSON_PATH}")

    # 2. 加载 Prediction
    pred_map = {}
    if os.path.exists(PRED_JSON_PATH):
        with open(PRED_JSON_PATH, 'r') as f:
            pred_data = json.load(f)
            for item in pred_data:
                frame_idx = parse_frame_id(item['frame_id'])
                pred_map[frame_idx] = item['event_type']
    else:
        print(f"警告: 未找到 {PRED_JSON_PATH}")

    # 3. 加载 BBox
    bbox_map = {}
    if os.path.exists(BBOX_JSON_PATH):
        with open(BBOX_JSON_PATH, 'r') as f:
            bbox_data = json.load(f)
            for key, boxes in bbox_data.items():
                idx = parse_frame_id(key)
                bbox_map[idx] = boxes
    else:
        print(f"警告: 未找到 {BBOX_JSON_PATH}")

    return gt_map, pred_map, bbox_map


# ================= 渲染辅助函数 =================

def create_timeline_bar(data_map, total_frames, width, height):
    """创建一个静态的时间轴图像条"""
    bar_img = np.zeros((height, width, 3), dtype=np.uint8)
    bar_img[:] = EVENT_MAP[0]["color"]  # 默认填充背景色 (无事件)

    for frame_idx in range(total_frames):
        event_type = data_map.get(frame_idx, 0)
        color = EVENT_MAP.get(event_type, {"color": DEFAULT_COLOR})["color"]

        # 计算当前帧在图像上的 x 坐标范围
        x_start = int((frame_idx / total_frames) * width)
        x_end = int(((frame_idx + 1) / total_frames) * width)

        # 确保至少绘制 1 像素宽
        if x_end <= x_start:
            x_end = x_start + 1

        cv2.rectangle(bar_img, (x_start, 0), (x_end, height), color, -1)

    return bar_img


def draw_legend(frame, width, height):
    """在视频右上角绘制图例"""

    # 1. 计算图例所需的尺寸
    max_text_width = 0
    # 我们只绘制 1-9 的图例，跳过 0 (No Event) 以保持整洁
    items_to_draw = [k for k in sorted(EVENT_MAP.keys()) if k != 0]

    for eid in items_to_draw:
        text = f"{eid}: {EVENT_MAP[eid]['name']}"  # 显示 ID: Name
        (w, h), _ = cv2.getTextSize(text, FONT_FACE, LEGEND_FONT_SCALE, LEGEND_THICKNESS)
        if w > max_text_width:
            max_text_width = w

    # 图例总宽 = 内边距*2 + 色块宽 + 间距 + 文字宽
    legend_w = LEGEND_PADDING * 2 + LEGEND_BOX_SIZE + 20 + max_text_width
    legend_h = LEGEND_PADDING * 2 + (len(items_to_draw) * LEGEND_LINE_HEIGHT)

    # 图例左上角坐标 (右上角放置)
    x1 = width - legend_w - LEGEND_X_OFFSET
    y1 = LEGEND_Y_OFFSET
    x2 = x1 + legend_w
    y2 = y1 + legend_h

    # 2. 绘制半透明背景
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)  # 黑色背景
    alpha = 0.6  # 透明度
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # 3. 绘制每一行
    current_y = y1 + LEGEND_PADDING
    for eid in items_to_draw:
        item = EVENT_MAP[eid]
        color = item["color"]
        name = item["name"]
        display_text = f"{eid}: {name}"

        # 绘制色块
        # 色块位置: x1 + padding, current_y + offset
        box_y = current_y + 10  # 垂直微调
        cv2.rectangle(frame, (x1 + LEGEND_PADDING, box_y),
                      (x1 + LEGEND_PADDING + LEGEND_BOX_SIZE, box_y + LEGEND_BOX_SIZE), color, -1)

        # 绘制文字
        text_x = x1 + LEGEND_PADDING + LEGEND_BOX_SIZE + 20
        # 垂直居中对齐文字: 基线位置大概是 box_y + box_size/2 + font_height/2
        text_y = current_y + 10 + int(LEGEND_BOX_SIZE / 2) + 15

        cv2.putText(frame, display_text, (text_x, text_y), FONT_FACE, LEGEND_FONT_SCALE, (255, 255, 255),
                    LEGEND_THICKNESS)

        current_y += LEGEND_LINE_HEIGHT


def main():
    if not os.path.exists(VIDEO_PATH):
        print(f"错误: 找不到视频文件 {VIDEO_PATH}")
        return

    print("正在加载 JSON 数据...")
    gt_map, pred_map, bbox_map = load_data()

    cap = cv2.VideoCapture(VIDEO_PATH)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"视频信息: {width}x{height}, {total_frames} 帧, {fps} FPS")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (width, height))

    print("正在预生成时间轴...")
    # 生成静态的时间轴条
    bar_gt_img = create_timeline_bar(gt_map, total_frames, width, BAR_HEIGHT)
    bar_pred_img = create_timeline_bar(pred_map, total_frames, width, BAR_HEIGHT)

    current_frame = 0
    print("开始渲染视频...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # ---------------- 渲染步骤 ----------------

        # 1. 渲染左上角帧数
        cv2.putText(frame, f"Frame: {current_frame}", (50, 100),
                    FONT_FACE, FRAME_INFO_SCALE, (0, 255, 255), TEXT_THICKNESS + 1)

        # 2. 渲染 BBox (带有 ID)
        if current_frame in bbox_map:
            boxes = bbox_map[current_frame]
            for i, box in enumerate(boxes):
                # box 格式 [norm_x1, norm_y1, norm_x2, norm_y2, conf]
                # 检查数据长度防止越界
                if len(box) >= 4:
                    nx1, ny1, nx2, ny2 = box[0], box[1], box[2], box[3]

                    x1 = int(nx1 * width)
                    y1 = int(ny1 * height)
                    x2 = int(nx2 * width)
                    y2 = int(ny2 * height)

                    # 绘制矩形 (使用青色以突出显示, 线条加粗)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 4)

                    # 绘制 ID 背景条
                    id_text = f"ID: {i}"
                    (text_w, text_h), baseline = cv2.getTextSize(id_text, FONT_FACE, TEXT_SCALE, TEXT_THICKNESS)
                    # 确保背景条不出界
                    id_bg_y1 = max(y1 - text_h - 20, 0)
                    id_bg_y2 = max(y1, text_h + 20)

                    cv2.rectangle(frame, (x1, id_bg_y1), (x1 + text_w + 20, id_bg_y2), (255, 255, 0), -1)
                    cv2.putText(frame, id_text, (x1 + 10, id_bg_y2 - 10),
                                FONT_FACE, TEXT_SCALE, (0, 0, 0), TEXT_THICKNESS)

        # 3. 绘制右上角图例
        draw_legend(frame, width, height)

        # 4. 渲染底部进度条
        # 计算位置 (从底部向上排列)
        # 布局:
        # [ Pred Label ]
        # [ Pred Bar   ]
        # [ GT Label   ]
        # [ GT Bar     ]

        pos_pred_y = height - MARGIN_BOTTOM - BAR_HEIGHT
        pos_gt_y = pos_pred_y - BAR_GAP - BAR_HEIGHT

        # 贴图
        frame[pos_gt_y:pos_gt_y + BAR_HEIGHT, 0:width] = bar_gt_img
        frame[pos_pred_y:pos_pred_y + BAR_HEIGHT, 0:width] = bar_pred_img

        # 添加文字标签 (加大字体)
        label_font_scale = 1.2
        label_thickness = 2
        cv2.putText(frame, "Ground Truth:", (20, pos_gt_y - 15),
                    FONT_FACE, label_font_scale, (255, 255, 255), label_thickness)
        cv2.putText(frame, "Prediction:", (20, pos_pred_y - 15),
                    FONT_FACE, label_font_scale, (255, 255, 255), label_thickness)

        # 5. 绘制播放进度指示线 (白线, 加粗)
        if total_frames > 0:
            cursor_x = int((current_frame / total_frames) * width)
            line_thickness = 4
            # 在两个条的位置画线
            cv2.line(frame, (cursor_x, pos_gt_y), (cursor_x, pos_gt_y + BAR_HEIGHT), (255, 255, 255), line_thickness)
            cv2.line(frame, (cursor_x, pos_pred_y), (cursor_x, pos_pred_y + BAR_HEIGHT), (255, 255, 255),
                     line_thickness)

        out.write(frame)

        if current_frame % 50 == 0:
            print(f"已处理: {current_frame}/{total_frames} 帧")

        current_frame += 1

    cap.release()
    out.release()
    print(f"渲染完成! 输出文件: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()