@echo off
chcp 936 >nul
rem 启动一个带远程调试端口的 Edge（用专用配置目录，不影响你日常用的 Edge）
rem 双击本文件即可；在弹出的浏览器里登录贴吧后，保持窗口开着，再运行脚本
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium_edge_profile"
echo Edge 已启动（远程调试端口 9222）
echo 请在弹出的浏览器里手动登录百度贴吧并保持登录，然后再运行脚本
pause
