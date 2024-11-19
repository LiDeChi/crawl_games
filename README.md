# 动态资源爬虫

这是一个用于爬取网页动态加载资源的Python脚本，可以提取图片、音频和脚本文件。

## 功能特点

- 支持动态加载的网页内容
- 自动提取图片、音频和脚本文件
- 智能处理相对和绝对URL路径
- 自动创建资源分类目录
- 详细的日志记录

## 安装要求

- Python 3.8+
- Chrome浏览器

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

1. 打开 `dynamic_crawler.py` 文件
2. 修改 `main()` 函数中的 URL：
```python
url = "https://example.com"  # 替换为你要爬取的网页URL
```
3. 运行脚本：
```bash
python dynamic_crawler.py
```

## 文件结构

下载的资源将保存在 `downloaded_resources` 目录下，按以下结构组织：
```
downloaded_resources/
├── images/
├── audio/
└── scripts/
```

## 注意事项

- 请确保遵守网站的robots.txt规则
- 注意网站的访问频率限制
- 确保有足够的磁盘空间存储下载的资源
- 某些网站可能有反爬虫机制，需要适当调整等待时间

## 许可证

[MIT License](LICENSE)
