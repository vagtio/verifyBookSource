# VerifyBookSource

阅读书源生成、校验工具v2.1



定时每天零点更新校验、过滤完成的书源：

https://gitdl.cn/https://raw.githubusercontent.com/vagtio/verifyBookSource/main/results/valid_books.json

声明源书源来自 https://github.com/shidahuilang/shuyuan 

我只是做了整合二次检验、过滤

## 项目


运行要求：

Python3.10以上


原理：

检验书源的网址能不能打开，过虑关键字

## 功能

1. 自定义运行线程：线程越多就越快，但也不介意太多，容易将有效书源判断为无效书源。
2. 文件支持本地文件和文件直链 默认书源url源自 https://github.com/shidahuilang/shuyuan
3. 支持重复书源去重、过滤
4. 自定义输出文件路径
5. 可一键运行 使用默认配置book/config.json

运行效果：

```sh
D:\Users\SkyQian\Documents\GitHub\verifyBookSource\dist# app.exe
欢迎使用书源校验工具（VerifyBookSource v2.1）
作者：勿埋我心 - SkyQian
Github：https://github.com/Qiantigers/verifyBookSource
我的博客：https://www.skyqian.com
----------------
是否使用config.json文件？（不使用则通过命令行输入配置）（y/n）n
本地文件路径/文件直链URL：https://xiao.ml/shuyuan/7
书源输出路径（为空则为当前目录，目录最后带斜杠）：
请输入工作线程，填写数字（并不是越大越好）：64
是否去重？（y/n）y
是否过滤特定关键词的书源？（y/n）y
请输入要过滤的关键词，用逗号分隔：登录,验证
2024-08-11 22:03:13,731 - INFO - 开始处理书源...
2024-08-11 22:03:13,732 - INFO - 开始检查书源...
2024-08-11 22:03:13,732 - INFO - 正在加载书源...
----------------
检查进度:  80%|████████████████████████████████████████████████████████████████▊                | 4306/5385 [10:34<01:03, 16.93it/s]
2024-08-11 22:16:47,089 - INFO - 正在去除重复...
2024-08-11 22:16:47,101 - INFO - 正在过滤书源...
2024-08-11 22:16:47,107 - INFO - 共过滤掉 0 个书源
2024-08-11 22:16:47,111 - INFO - 共过滤掉 0 个书源
2024-08-11 22:16:47,111 - INFO - 处理完成！
2024-08-11 22:16:47,111 - INFO - 正在保存结果...
2024-08-11 22:16:47,525 - INFO - 结果已保存到 ./
2024-08-11 22:16:47,526 - INFO - 总书源数: 4305
2024-08-11 22:16:47,526 - INFO - 有效书源数: 2722
2024-08-11 22:16:47,526 - INFO - 无效书源数: 1583
2024-08-11 22:16:47,526 - INFO - 成功率: 63.23%

----------------
成果报表
书源总数：4305
有效书源数：2722
无效书源数：1583
成功率：63.23%
重复书源数：0
耗时：813.38秒

输入任意键退出……

```

## 致谢

我们想要特别感谢以下仓库和它们的贡献者，他们的工作对我的项目产生了重要影响：

 :star: [shuyuan](https://github.com/shidahuilang/shuyuan)：香色闺阁+阅读3.0书源+源阅读+爱阅书香+千阅+花火阅读+读不舍手+IPTV源+IPA巨魔应用=自动更新
 
 :star: [VerifyBookSource](https://github.com/WuSuoV/verifyBookSource)：校验阅读书源，生成有效书源和无效书源。支持书源去重、多线程

我们非常感激开源社区的贡献和支持。
