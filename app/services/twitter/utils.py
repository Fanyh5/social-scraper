import random
import time
import math

def human_mouse_move(page, start_x, start_y, end_x, end_y, steps=20):
    """
    模拟人类鼠标移动轨迹 (Bézier 曲线)
    """
    # 随机控制点
    control_x = random.randint(min(start_x, end_x), max(start_x, end_x))
    control_y = random.randint(min(start_y, end_y), max(start_y, end_y))
    
    for i in range(steps + 1):
        t = i / steps
        # 二阶贝塞尔曲线公式
        x = (1 - t)**2 * start_x + 2 * (1 - t) * t * control_x + t**2 * end_x
        y = (1 - t)**2 * start_y + 2 * (1 - t) * t * control_y + t**2 * end_y
        
        # 添加微小抖动
        x += random.uniform(-2, 2)
        y += random.uniform(-2, 2)
        
        page.mouse.move(x, y)
        # 随机等待
        time.sleep(random.uniform(0.005, 0.02))

def human_click(page, x, y):
    """
    模拟人类点击：移动 -> 悬停 -> 点击
    """
    # 获取当前鼠标位置 (Playwright 不直接提供，假设从 0,0 或上次位置开始，这里简化为从当前页面中心或随机位置)
    # 实际上 page.mouse.move 会直接跳过去如果没中间步，所以我们需要起始点
    # 既然无法获取当前位置，我们假设一个随机起始点或者就在附近
    start_x = random.randint(0, 1920)
    start_y = random.randint(0, 1080)
    
    human_mouse_move(page, start_x, start_y, x, y)
    time.sleep(random.uniform(0.1, 0.3))
    page.mouse.down()
    time.sleep(random.uniform(0.05, 0.15))
    page.mouse.up()
