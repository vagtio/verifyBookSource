import json
import os.path
import time
from book.book import BookSourceManager


def main():
    """主函数，处理用户输入并执行书源处理流程"""
    print("欢迎使用书源校验工具（VerifyBookSource v2.2）\n"
          "作者：勿埋我心 - SkyQian\n"
          "Github：https://github.com/Qiantigers/verifyBookSource\n"
          "我的博客：https://www.skyqian.com\n"
          f"{'-' * 16}")

    config_path = 'book/config.json'
    if input('是否使用config.json文件？（不使用则通过命令行输入配置）（y/n）').lower() == 'n':
        # 通过命令行输入配置
        config = {
            'path': input('本地文件路径/文件直链URL：'),
            'outpath': input('书源输出路径（为空则为当前目录，目录最后带斜杠）：') or './',
            'workers': int(input('请输入工作线程，填写数字（并不是越大越好）：')),
            'dedup': input('是否去重？（y/n）'),
            'filter': input('是否过滤特定关键词的书源？（y/n）'),
            'keywords_to_filter': input('请输入要过滤的关键词，用逗号分隔：').split(',') if input(
                '是否过滤特定关键词的书源？（y/n）').lower() == 'y' else []
        }
        # 保存配置到文件
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4, sort_keys=False)
    else:
        # 从文件加载配置
        if not os.path.exists(config_path):
            print('config.json文件不存在，请检查一下。或者使用命令行输入配置。')
            return
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

    # 创建BookSourceManager实例
    manager = BookSourceManager(config['path'], config)

    # 开始处理书源
    start_time = time.time()
    results = manager.process_books(int(config['workers']))
    elapsed_time = time.time() - start_time

    # 保存结果
    manager.save_results(results, config['outpath'])

    # 分析结果
    analysis = manager.analyze_results(results)

    # 打印报告
    print(f"\n{'-' * 16}\n"
          "成果报表\n"
          f"书源总数：{analysis['total']}\n"
          f"有效书源数：{analysis['valid']}\n"
          f"无效书源数：{analysis['invalid']}\n"
          f"成功率：{analysis['success_rate']:.2f}%\n"
          f"重复书源数：{(analysis['total'] - analysis['valid'] - analysis['invalid']) if config.get('dedup') == 'y' else '未选择去重'}\n"
          f"耗时：{elapsed_time:.2f}秒\n")

    input('输入任意键退出……')


if __name__ == '__main__':
    main()
