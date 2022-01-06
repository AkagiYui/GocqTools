# GocqTools

#### 管理Go-cqhttp的工具

立项日期: 2021-12-26

自己玩玩，练习Python用的

2022新年快乐

其实下面那个使用方法应该是还没写完整的，可能还是跑不起来

---

## 食用方法

0. 确保你的Python版本大于等于 `3.8.0`
1. 一些库的安装

   ```shell
   pip3 install wheel gevent psutil colorlog python-dotenv requests websocket-client sqlalchemy bottle jwt paste pymysql jinja2 PyMuPDF
   ```
2. 你需要修改配置文件 `config.json`

   配置文件中已列出了所有目前可用的配置项

   你需要修改数据库配置和Web端口
3. 跑起来

   ```shell
   python3 .\main.py
   ```
4. 访问Web管理页面
5. 用配置文件里的账号密码登录

---

## 一些说明

这是一个耦合度很高的结构体系
里面有已经写好的功能

当然你也可以自己写新功能
但是我感觉挺不友好的

占卜数据库文件：`zhan_bu.sql` 请自行导入

技术栈 `SQLAlchemy` `bottle` `paste` `jinja2`

代码ToDo List

- [X]  `.env`覆盖 `config.json`
- [ ]  Web管理
- [ ]  功能分号管理

功能ToDo List

- [X]  我吃啥
- [X]  服务器信息
- [X]  占卜
- [X]  PDF转PNG

目前想不到有什么要做的
有需要的话可以提issue

注意：Web页面未做任何安全措施，请勿随意暴露端口至公网

---

# 更新日志

## 0.2.0 `2022-01-06`

✨ 新增自定义功能 自定义字典类 `AyDict`

✨ 新增自定义功能 文件格式判断函数 `get_file_format` 用文件头判断文件格式

✨ 新增自定义功能 关闭print类 `HiddenPrints` 添加装饰符 `@HiddenPrints` 可暂时重定向输出至空

✨ 新增自定义功能 数字转汉字函数 `int_to_Chinese` 支持小范围内数字

✨ 新增自定义功能 获取自身运行时长函数 `self_uptime`

✨ 新增自定义功能 获取开机时长函数 `macine_uptime`

✨ 新增自定义功能 获取自身ip函数 `get_self_ip`

## 0.1.5 `2022-01-06`

✨ 新增功能 `PDF转PNG` 群聊发送PDF文件转换为图片预览

✨ 新增功能 `占卜` 发送 `求签` `解签` 体验

## 0.1.1 `2022-01-04`

⬆️ 优化代码结构

✨ 新增web端首页

✨ 新增功能 `server_info`

```
⤴️ 服务器信息
⤵️
登录用户：QQ昵称(QQ号)
收发消息数：10188/212
操作系统：Windows 10.0.19041
Python版本：3.10.0
系统CPU使用率：55.8%
脚本CPU使用率：1.5%
系统内存使用率：56.4886%
脚本内存使用率：0.3419%
系统启动时长：2 days, 18:54:53
脚本运行时长：0:05:41
```

## 0.0.4 `2022-01-03`

⬆️ 优化代码结构

✨ 新增web框架

## 0.0.3 `2021-12-29`

✨ 新增终止信号捕抓

✨ 新增GocqConnection `已连接事件`

✨ 新增GocqConnection `心跳检测`

⬆️ 优化 `mysql连接关闭`

🔄 `SQLAlchemy引擎`改为 `PyMySQL`

⬆️ 优化 `我吃啥`

```
⤴️ 有啥吃
⤵️ 胡辣汤

⤴️ 都有啥吃
⤵️ 胡辣汤 盖浇饭
```

## 0.0.2 `2021-12-27`

✨ 新增功能 `我吃啥`

```
⤴️ 我吃啥 新增 胡辣汤
⤵️ 已新增 胡辣汤

⤴️ 我吃啥
⤵️ 胡辣汤
```

## 0.0.1 `2021-12-26`

✨ 构建框架
️
