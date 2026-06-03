"""下载Zpix像素风字体"""
import urllib.request
import os

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
FONT_PATH = os.path.join(FONT_DIR, "zpix.ttf")
ZPIX_URL = "https://github.com/SolidZORO/zpix-pixel-font/releases/download/v3.1.11/zpix.ttf"

os.makedirs(FONT_DIR, exist_ok=True)

# 清理旧的不完整文件
if os.path.exists(FONT_PATH):
    size = os.path.getsize(FONT_PATH)
    if size < 6000000:
        print(f"删除不完整文件 ({size} bytes)...")
        os.remove(FONT_PATH)
    else:
        print(f"Zpix字体已存在且完整 ({size} bytes)，跳过下载")
        exit(0)

print(f"正在下载Zpix字体...")
print(f"URL: {ZPIX_URL}")
print(f"目标: {FONT_PATH}")

try:
    urllib.request.urlretrieve(ZPIX_URL, FONT_PATH)
    size = os.path.getsize(FONT_PATH)
    if size > 6000000:
        print(f"下载完成！文件大小: {size} bytes ({size/1024/1024:.1f} MB)")
    else:
        print(f"警告：文件可能不完整 ({size} bytes)，预期约 6.85 MB")
except Exception as e:
    print(f"下载失败: {e}")
    print()
    print("请手动下载Zpix字体：")
    print("1. 访问 https://github.com/SolidZORO/zpix-pixel-font/releases")
    print("2. 下载最新版 zpix.ttf")
    print(f"3. 放置到 {FONT_DIR}")
    print("游戏将使用系统黑体(SimHei)作为降级字体")
