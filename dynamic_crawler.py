from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import os
import time
import urllib.parse
import logging
import requests
from datetime import datetime

class BrowserResourceMonitor:
    def __init__(self, save_dir='downloaded_resources'):
        self.save_dir = save_dir
        self.setup_logging()
        self.setup_driver()
        self.setup_directories()
        self.downloaded_files = set()  # 避免重复下载

    def setup_logging(self):
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('resource_monitor.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # 使用固定的用户数据目录，这样重启后可以继续使用同一个配置
        user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrome_user_data')
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        chrome_options.add_experimental_option('perfLoggingPrefs', {
            'enableNetwork': True,
            'enablePage': True,
        })
        chrome_options.set_capability('goog:loggingPrefs', {
            'performance': 'ALL',
            'browser': 'ALL'
        })
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("成功启动Chrome浏览器")
        except Exception as e:
            self.logger.error(f"启动Chrome浏览器时出错: {str(e)}")
            raise

    def setup_directories(self):
        # 创建按日期组织的资源目录
        current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_save_dir = os.path.join(self.save_dir, current_date)
        
        for dir_name in ['images', 'audio', 'video', 'scripts', 'documents', 'others']:
            full_path = os.path.join(self.current_save_dir, dir_name)
            os.makedirs(full_path, exist_ok=True)

    def get_resource_type(self, url, content_type=''):
        """根据URL和内容类型确定资源类型"""
        url_lower = url.lower()
        content_type_lower = content_type.lower()

        # 图片文件
        if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico']) or 'image' in content_type_lower:
            return 'images'
        # 音频文件
        elif any(ext in url_lower for ext in ['.mp3', '.wav', '.ogg', '.m4a']) or 'audio' in content_type_lower:
            return 'audio'
        # 视频文件
        elif any(ext in url_lower for ext in ['.mp4', '.webm', '.mkv', '.flv', '.m3u8']) or 'video' in content_type_lower:
            return 'video'
        # 脚本文件
        elif any(ext in url_lower for ext in ['.js', '.jsx', '.ts', '.tsx']) or 'javascript' in content_type_lower:
            return 'scripts'
        # 文档文件
        elif any(ext in url_lower for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt']):
            return 'documents'
        # 其他文件
        else:
            return 'others'

    def download_file(self, url, resource_type, request_id=None):
        """下载资源文件"""
        try:
            # 检查是否已下载
            if url in self.downloaded_files:
                return False
            
            # 获取文件名
            file_name = os.path.basename(urllib.parse.urlparse(url).path)
            if not file_name or '.' not in file_name:
                file_name = f"{int(time.time())}_{hash(url) & 0xffffffff}"
            
            # 设置保存路径
            save_path = os.path.join(self.current_save_dir, resource_type, file_name)
            
            # 处理blob URL
            if url.startswith('blob:'):
                try:
                    # 使用CDP命令获取blob内容
                    result = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                    if result and 'body' in result:
                        if result.get('base64Encoded', False):
                            import base64
                            data = base64.b64decode(result['body'])
                        else:
                            data = result['body'].encode('utf-8')
                        
                        with open(save_path, 'wb') as f:
                            f.write(data)
                        self.downloaded_files.add(url)
                        self.logger.info(f"成功下载blob资源: {file_name}")
                        return True
                except Exception as e:
                    self.logger.error(f"下载blob资源时出错 {url}: {str(e)}")
                    return False
            
            # 处理普通URL
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                self.downloaded_files.add(url)
                self.logger.info(f"成功下载 {resource_type}: {file_name} 从 {url}")
                return True
            else:
                self.logger.warning(f"下载失败 {url}, 状态码: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"下载文件时出错 {url}: {str(e)}")
            return False

    def process_network_log(self):
        """处理网络日志并下载资源"""
        logs = self.driver.get_log('performance')
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                
                # 处理网络请求
                if ('Network.responseReceived' in log['method'] or 
                    'Network.loadingFinished' in log['method']):
                    
                    # 确保response字段存在
                    if 'params' not in log or 'response' not in log['params']:
                        continue
                        
                    response = log['params']['response']
                    url = response.get('url', '')
                    content_type = response.get('mimeType', '')
                    status = response.get('status', 0)
                    request_id = log['params'].get('requestId')
                    
                    # 跳过非资源请求
                    if not url or url.startswith('data:') or 'chrome-extension://' in url:
                        continue
                        
                    # 跳过特定的状态码
                    if status in [204, 401, 404, 405]:
                        continue
                        
                    # 跳过分析和跟踪服务的请求
                    if any(domain in url.lower() for domain in [
                        'google-analytics.com',
                        'doubleclick.net',
                        'deltadna.net',
                        'braze.eu'
                    ]):
                        continue
                    
                    resource_type = self.get_resource_type(url, content_type)
                    self.download_file(url, resource_type, request_id)
                    
            except KeyError:
                continue
            except json.JSONDecodeError:
                continue
            except Exception as e:
                self.logger.error(f"处理网络日志时出错: {str(e)}")

    def monitor_browser(self):
        """持续监控浏览器活动"""
        try:
            self.logger.info("开始监控浏览器资源...")
            self.logger.info(f"资源将保存在: {self.current_save_dir}")
            
            while True:
                try:
                    self.process_network_log()
                    time.sleep(1)  # 避免过度消耗CPU
                except Exception as e:
                    self.logger.error(f"监控过程中出错: {str(e)}")
                    continue
                    
        except KeyboardInterrupt:
            self.logger.info(f"监控被用户手动停止")
            self.logger.info(f"共下载 {len(self.downloaded_files)} 个文件")
        finally:
            self.driver.quit()

def main():
    monitor = BrowserResourceMonitor()
    monitor.monitor_browser()

if __name__ == "__main__":
    main()
