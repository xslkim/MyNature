"""
Blender 启动时自动开启 BlenderMCP socket server。
用法：blender --python start_with_mcp.py
或者直接双击用 Blender 打开本文件（需先在 Preferences > File Paths > Scripts 配置）。
"""
import bpy

# 延迟 1 秒启动 server，等 Blender UI 完全就绪
def _start_mcp_server():
    try:
        bpy.ops.blendermcp.start_server()
        print("[start_with_mcp] MCP socket server started on localhost:9876")
    except Exception as e:
        print(f"[start_with_mcp] start_server failed: {e}")

# 用 timer 确保在主线程、UI 就绪后执行
bpy.app.timers.register(_start_mcp_server, first_interval=1.0)
