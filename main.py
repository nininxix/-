# -*- coding: utf-8 -*-

"""
百度贴吧删除自己的回帖工具

功能：
1. 连接已经登录的 Edge 浏览器
2. 自动进入个人主页 -> 回帖
3. 循环删除第一条回复
4. 当前页面删除完自动刷新重新加载
5. 自动恢复
6. 支持紧急停止

注意：
- 请使用独立 Edge 调试窗口
- 不要用自己日常浏览器窗口运行
"""

import os
import time
import random
import traceback
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# ===============================
# 配置区域（要改的地方都在这）
# ===============================

# Edge 调试地址（端口要和启动 Edge 的命令一致）
DEBUG_ADDRESS = "127.0.0.1:9222"

# ★★★ 必须修改：你的贴吧个人主页地址 ★★★
# 获取方法：登录贴吧 -> 点自己头像进「个人主页」-> 点「回贴」tab
#           -> 复制浏览器地址栏里的完整网址，整段替换掉下面这个占位符。
# 网址形如：https://tieba.baidu.com/home/main?id=填写你的贴吧ID&fr=personalize_page
TIEBA_URL = "你的贴吧主页URL"

# 最大删除数量（删够这个数就自动停，想继续删就调大）
MAX_DELETE_COUNT = 500

# 随机等待时间范围（秒）
MIN_WAIT = 1
MAX_WAIT = 3

# 删除后等待页面刷新的时间范围（秒）
DELETE_WAIT_MIN = 4
DELETE_WAIT_MAX = 7

# 连续检测到几次空页面就刷新重新加载
EMPTY_LIMIT = 2

# ===============================
# 日志
# ===============================

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

# ===============================
# 随机等待
# ===============================

def human_sleep(min_time=MIN_WAIT, max_time=MAX_WAIT):
    time.sleep(random.uniform(min_time, max_time))

# ===============================
# 检查停止文件
# ===============================

def check_stop():
    if os.path.exists("stop.txt"):
        log("发现 stop.txt，程序停止")
        return True
    return False

# ===============================
# 创建浏览器连接
# ===============================

def create_driver():
    options = Options()
    options.add_experimental_option("debuggerAddress", DEBUG_ADDRESS)
    driver = webdriver.Edge(options=options)
    return driver

# ===============================
# 获取回复列表
# ===============================

def get_replies(driver):
    try:
        replies = driver.find_elements(
            By.XPATH,
            "/html/body/div[1]/div[2]/div/div/div[3]/div[1]/div[2]/div/div/div"
        )
        log(f"当前回复数量:{len(replies)}")
        return replies
    except Exception:
        log("获取回复失败")
        traceback.print_exc()
        return []

# ===============================
# 进入回帖
# ===============================

def open_reply_tab(driver, wait):
    try:
        tab = wait.until(
            EC.element_to_be_clickable((By.ID, "tab-reply"))
        )
        driver.execute_script("arguments[0].click();", tab)
        log("进入回帖成功")
        time.sleep(5)
        return True
    except Exception:
        log("进入回帖失败")
        traceback.print_exc()
        return False

# ===============================
# 删除第一条
# ===============================

def delete_first_reply(driver, wait):
    try:
        replies = get_replies(driver)
        if len(replies) == 0:
            return False

        reply = replies[0]
        log("处理第一条回复")

        # 三个点
        more = reply.find_element(By.CSS_SELECTOR, ".thread-setting")
        ActionChains(driver).move_to_element(more).perform()
        human_sleep()
        driver.execute_script("arguments[0].click();", more)
        log("三个点点击成功")
        human_sleep()

        # 删除
        delete_btn = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class,'setting-popover')]"
                    "//div[contains(@class,'text') and text()='删除']"
                )
            )
        )
        driver.execute_script("arguments[0].click();", delete_btn)
        log("删除按钮点击成功")
        human_sleep(2, 4)

        # 确认
        confirm = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class,'center') and text()='确定']"
                )
            )
        )
        driver.execute_script("arguments[0].click();", confirm)
        log("确定按钮点击成功")
        human_sleep(DELETE_WAIT_MIN, DELETE_WAIT_MAX)
        return True

    except Exception:
        log("删除异常")
        traceback.print_exc()
        os.makedirs("screenshots", exist_ok=True)
        filename = (
            "screenshots/error_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".png"
        )
        try:
            driver.save_screenshot(filename)
            log(f"保存截图:{filename}")
        except Exception:
            pass
        return False

# ===============================
# 主程序
# ===============================

def main():
    print()
    print("===============================")
    print(" 百度贴吧删除回帖工具")
    print("===============================")
    print("""
即将删除你的贴吧回帖。

安全措施:
1. 删除前需要确认
2. 最大删除数量限制
3. 可使用 stop.txt 紧急停止

输入 YES 开始:
""")
    confirm = input("> ")
    if confirm != "YES":
        print("已取消")
        return

    driver = create_driver()
    wait = WebDriverWait(driver, 15)
    log("浏览器连接成功")

    driver.get(TIEBA_URL)
    log("打开贴吧主页")
    time.sleep(5)

    if not open_reply_tab(driver, wait):
        return

    delete_count = 0
    empty_count = 0

    while True:
        if check_stop():
            break

        if delete_count >= MAX_DELETE_COUNT:
            log("达到最大删除数量")
            break

        result = delete_first_reply(driver, wait)

        if result:
            delete_count += 1
            empty_count = 0
            log(f"累计删除:{delete_count}")
        else:
            replies = get_replies(driver)
            if len(replies) == 0:
                empty_count += 1
                log(f"空页面检测:{empty_count}")
            else:
                empty_count = 0

            # 当前加载完，刷新重新获取
            if empty_count >= EMPTY_LIMIT:
                log("当前页面完成，刷新重新加载")
                driver.refresh()
                time.sleep(8)
                open_reply_tab(driver, wait)
                empty_count = 0

        human_sleep(2, 5)

    log("任务结束")
    log(f"总删除数量:{delete_count}")

if __name__ == "__main__":
    main()
