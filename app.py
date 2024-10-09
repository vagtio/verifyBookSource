import os
import json
import time
import sys
from book.book import BookSourceManager

def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于开发环境和 PyInstaller 打包后的环境 """
    try:
        # PyInstaller 创建临时文件夹并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_or_create_config():
    """ 加载或创建配置文件 """
    config_paths = resource_path('book/config.json')

    # 检查是否在 GitHub Actions 环境中运行
    if 'GITHUB_ACTIONS' in os.environ:
        # 在 CI 环境中，尝试加载 config.json
        if os.path.exists(config_paths):
            with open(config_paths, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 如果文件不存在，使用环境变量或默认值
            return {
                'path': os.environ.get('BOOK_SOURCE_PATH', ''),
                'outpath': os.environ.get('OUTPUT_PATH', './'),
                'workers': int(os.environ.get('WORKERS', 4)),
                'dedup': os.environ.get('DEDUP', 'true').lower() == 'true',
                'filter': os.environ.get('FILTER', 'false').lower() == 'true',
                'keywords_to_filter': os.environ.get('KEYWORDS_TO_FILTER', '').split(',')
            }
    else:
        # 本地环境
        if input('是否使用config.json文件？（y/n）').lower() == 'n':
            config = {}
            config['path'] = input('本地文件路径/文件直链URL：')
            config['outpath'] = input('书源输出路径（为空则为当前目录，目录最后带斜杠）：') or './'
            config['workers'] = int(input('请输入工作线程，填写数字（并不是越大越好）：'))
            config['dedup'] = input('是否去重？（y/n）').lower() == 'y'
            filter_option = input('是否过滤特定关键词的书源？（y/n）').lower()
            config['filter'] = filter_option == 'y'
            if config['filter']:
                config['keywords_to_filter'] = input('请输入要过滤的关键词，用逗号分隔：').split(',')
            else:
                config['keywords_to_filter'] = []
            with open(config_paths, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4, sort_keys=False)
            return config
        else:
            if not os.path.exists(config_paths):
                print('config.json文件不存在，请检查一下。或者使用命令行输入配置。')
                return None
            with open(config_paths, 'r', encoding='utf-8') as f:
                return json.load(f)

def main():
    print("欢迎使用书源校验生成工具（VerifyBookSource v2.1）\n"
          f"{'-' * 16}")

    config = load_or_create_config()
    if config is None:
        return

    manager = BookSourceManager(config['paths'], config)
    start_time = time.time()
    results = manager.process_books(int(config['workers']))
    elapsed_time = time.time() - start_time
    manager.save_results(results, config['outpath'])
    analysis = manager.analyze_results(results)




    print(f"\n{'-' * 16}\n"
          "成果报表\n"
          f"书源总数：{analysis['total']}\n"
          f"有效书源数：{analysis['valid']}\n"
          f"无效书源数：{analysis['invalid']}\n"
          f"成功率：{analysis['success_rate']:.2f}%\n"
          f"重复书源数：{(analysis['total'] - analysis['valid'] - analysis['invalid']) if config['dedup'] else '未选择去重'}\n"
          f"耗时：{elapsed_time:.2f}秒\n")

    # 只在非 GitHub Actions 环境中等待用户输入
    if 'GITHUB_ACTIONS' not in os.environ:
        input('输入任意键退出……')

if __name__ == '__main__':
    main()
