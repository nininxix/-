# 启动一个带远程调试端口的 Edge（用专用配置目录，不影响你日常用的 Edge）
# 用法：在 PowerShell 里执行，或右键「用 PowerShell 运行」
#   powershell -ExecutionPolicy Bypass -File .\start_edge.ps1

$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if (-not (Test-Path $edge)) {
    Write-Host "没找到 Edge，检查一下路径：$edge" -ForegroundColor Red
    exit 1
}

Start-Process $edge -ArgumentList @(
    "--remote-debugging-port=9222",
    "--user-data-dir=C:\selenium_edge_profile"
)

Write-Host "Edge 已启动（远程调试端口 9222）"
Write-Host "请在弹出的浏览器里手动登录百度贴吧并保持登录，然后再运行 main.py"
