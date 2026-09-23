@echo off
chcp 65001 >nul
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium_edge_profile"
echo Edge 已启动（远程调试端口 9222）
echo 请在弹出的浏览器里手动登录百度贴吧并保持登录，然后再运行 main.py
pause
