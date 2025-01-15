# 动态资源爬虫

这是一个用于爬取网页动态加载资源的Python脚本，支持自动下载和分类各种网页资源。

## 功能特点

- 支持动态加载的网页内容
- 自动提取和分类多种资源类型：
  - 图片（jpg, jpeg, png, gif, webp, svg, ico）
  - 音频（mp3, wav, ogg, m4a）
  - 视频（mp4, webm, mkv, flv, m3u8）
  - 脚本文件（js, jsx, ts, tsx）
  - 文档（pdf, doc, docx, xls, xlsx, txt）
  - 其他资源
- 智能处理相对和绝对URL路径
- 自动按日期时间创建资源目录
- 避免重复下载相同资源
- 详细的日志记录系统
- 持久化的Chrome配置

## 安装要求

- Python 3.8+
- Chrome浏览器
- Selenium WebDriver

## 安装步骤

1. 克隆仓库：
```bash
git clone [repository-url]
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 基础使用

1. 创建一个新的爬虫实例：
```python
from dynamic_crawler import BrowserResourceMonitor

# 使用默认下载目录
monitor = BrowserResourceMonitor()

# 或指定自定义下载目录
monitor = BrowserResourceMonitor(save_dir='my_downloads')
```

2. 启动监控：
```python
monitor.monitor_browser()
```

3. 在Chrome浏览器中：
   - 浏览器会自动打开
   - 手动输入要爬取的网址
   - 浏览网页，脚本会自动检测和下载资源
   - 可以访问多个页面，脚本会持续监控
   - 按 Ctrl+C 停止监控

### 自定义使用

如果要修改默认行为，可以编辑 `dynamic_crawler.py` 中的以下部分：

1. Chrome选项配置（在 `setup_driver` 方法中）：
```python
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
# 添加其他Chrome选项...
```

2. 资源类型配置（在 `get_resource_type` 方法中）：
```python
# 添加或修改文件扩展名和内容类型的判断规则
if any(ext in url_lower for ext in ['.jpg', '.jpeg', ...]):
    return 'images'
```

### 使用示例

1. 基本使用示例：
```python
from dynamic_crawler import BrowserResourceMonitor

def main():
    # 创建监控器实例
    monitor = BrowserResourceMonitor()
    
    # 开始监控
    monitor.monitor_browser()

if __name__ == "__main__":
    main()
```

2. 自定义下载目录示例：
```python
from dynamic_crawler import BrowserResourceMonitor

def main():
    # 指定自定义下载目录
    monitor = BrowserResourceMonitor(save_dir='game_resources')
    
    # 开始监控
    monitor.monitor_browser()

if __name__ == "__main__":
    main()
```

### 运行提示

1. 首次运行时：
   - 确保已安装所有依赖
   - 检查Chrome浏览器版本与WebDriver版本是否匹配
   - 确保有足够的磁盘空间

2. 运行过程中：
   - 可以查看终端输出的日志信息
   - 检查 `resource_monitor.log` 文件获取详细日志
   - 观察 `downloaded_resources` 目录中的文件组织情况

3. 停止程序：
   - 按 Ctrl+C 可以安全地停止程序
   - 程序会显示下载文件总数
   - Chrome浏览器会自动关闭

## 文件结构

下载的资源将按日期时间保存在 `downloaded_resources` 目录下，具体结构如下：
```
downloaded_resources/
└── YYYYMMDD_HHMMSS/
    ├── images/      # 图片文件
    ├── audio/       # 音频文件
    ├── video/       # 视频文件
    ├── scripts/     # 脚本文件
    ├── documents/   # 文档文件
    └── others/      # 其他类型文件
```

## 日志记录

脚本运行时会生成详细的日志记录，保存在 `resource_monitor.log` 文件中。日志包含：
- 浏览器启动状态
- 资源下载进度
- 错误信息和异常处理

## 注意事项

- 确保有足够的磁盘空间存储下载的资源
- 下载大量资源时可能需要较长时间
- 部分网站可能有反爬虫机制，请遵守网站的使用条款
