# GocqTools

#### 管理Go-cqhttp的工具

立项日期: 2021-12-26

自己玩玩，练习Python用的

2022新年快乐

其实下面那个使用方法应该是还没写完整的，可能还是跑不起来

---

## 使用方法

0. 确保你的Python版本大于等于 `3.8.0`
   ```shell
   python3 --version
   ```
   
1. 一些依赖的安装
   ```shell
   sudo apt install ffmpeg fluidsynth
   ```
   以上仅为我测试环境debian系统的安装方法

   根据自己的系统让环境变量里有ffmpeg与fluidsynth即可

   ```shell
   python3 -m pip install wheel distro gevent psutil colorlog python-dotenv requests websocket-client sqlalchemy bottle pyjwt paste pymysql jinja2 PyMuPDF
   ```
   
2. 你需要修改配置文件 `config.json`

   配置文件中已列出了所有目前可用的配置项

   你需要修改数据库配置和Web端口(数据库要结构我还没说明...)

3. 跑起来

   ```shell
   python3 ./main.py
   ```
   
4. 访问Web管理页面

5. 用配置文件里的账号密码登录

---

## 一些说明

这是一个耦合度不低的结构体系
里面有已经写好的功能

当然你也可以自己写新功能
但是我感觉现阶段挺不友好的

用到了 `SQLAlchemy` `bottle` `paste` `jinja2`

###### 代码TODO List

- [X]  `.env`覆盖 `config.json`
- [ ]  Web管理
- [ ]  功能分号管理
- [ ]  解决文件过大导致base64过长

###### 功能TODO List

- [X]  我吃啥
- [X]  服务器信息
- [X]  占卜
- [X]  PDF转PNG
- [x]  Midi转语音
- [ ]  是什么

已完成的功能说明可以查看[功能说明](docs/functions.md)

目前想不到有什么要做的

有需要的话可以提issue(其实我不太会用issue，强迫自己用以达到学习的目的)

注意：Web页面未做任何安全措施，请勿随意暴露端口至公网

---

# 更新日志

## 0.3.0 `2022-01-17`

`U` 更新`服务器信息`支持显示Linux发行版

`A` 新增自定义功能 `文本转Midi`类

`A` 新增功能`Midi转语音`
> `S` 演奏1155665-4433221-
> 
> `R` `小星星语音`

## 0.2.5 `2022-01-13`

`F` 调整README，不使用emoji，减少系统间差异

`F` 修复Web端静态资源目录错误

`F` 修复Web启动情况提示错误

`F` `我吃啥`取消全库查询

`U` 优化`占卜` 支持解当天签`解签`

`U` 优化`我吃啥` 支持批量新增`我吃啥 新增 金汤肥牛 红烧牛肉`

`U` 优化`我吃啥` 支持群内食物`吃啥`与个人食物`我吃啥`

`A` 新增功能 群里@机器人，检测在线情况

`A` 消息支持接收群成员身份 键`sender.role`

`A` 新增自定义功能 自定义字符串类`AyStr`

`A` `我吃啥`支持群管理员删除群内食物

`A` 类`CqCode`新增`at`

`A` 类`CqCode`新增`record` 支持发送语音

`A` 类`CqCode`新增`record_local` 支持发送本地音频文件

> 发送语音需要go-cqhttp端环境变量含有`ffmpeg`

## 0.2.1 `2022-01-07`
`F` 自定义功能 函数`int_to_Chinese`改名为`int_to_chinese`

`U`  优化`占卜` 支持中文解签`解签二十三`

`A` 新增Web端登录/退出功能

`A` 新增自定义功能 两个汉字转数字函数 `chinese_to_int` `chinese_to_int_e`


## 0.2.0 `2022-01-06`

`A` 新增自定义功能 自定义字典类 `AyDict`

`A` 新增自定义功能 文件格式判断函数 `get_file_format` 用文件头判断文件格式

`A` 新增自定义功能 关闭print类 `HiddenPrints` 添加装饰符 `@HiddenPrints` 可暂时重定向输出至空

`A` 新增自定义功能 数字转汉字函数 `int_to_Chinese` 支持小范围内数字

`A` 新增自定义功能 获取自身运行时长函数 `self_uptime`

`A` 新增自定义功能 获取开机时长函数 `macine_uptime`

`A` 新增自定义功能 获取自身ip函数 `get_self_ip`

## 0.1.5 `2022-01-06`

`A` 新增功能 `PDF转PNG` 群聊发送PDF文件转换为图片预览

`A` 新增功能 `占卜` 发送 `求签` `解签` 体验

## 0.1.1 `2022-01-04`

`U`  优化代码结构

`A` 新增web端首页

`A` 新增功能 `server_info`

> `S`服务器信息
>
> `R`
> ```
> 登录用户：QQ昵称(QQ号)
> 收发消息数：10188/212
> 操作系统：Windows 10.0.19041
> Python版本：3.10.0
> 系统CPU使用率：55.8%
> 脚本CPU使用率：1.5%
> 系统内存使用率：56.4886%
> 脚本内存使用率：0.3419%
> 系统启动时长：2 days, 18:54:53
> 脚本运行时长：0:05:41
> ```

## 0.0.4 `2022-01-03`

`U`  优化代码结构

`A` 新增web框架

## 0.0.3 `2021-12-29`

`A` 新增终止信号捕抓

`A` 新增GocqConnection `已连接事件`

`A` 新增GocqConnection `心跳检测`

`F`  优化 `mysql连接关闭`

`F` `SQLAlchemy引擎`改为 `PyMySQL`

`U`  优化 `我吃啥`

> `S`有啥吃
> `R`胡辣汤
> 
> `S`都有啥吃
> `R`胡辣汤 盖浇饭

## 0.0.2 `2021-12-27`

`A` 新增功能 `我吃啥`

> `S`我吃啥 新增 胡辣汤
> `R`已新增 胡辣汤
> 
> `S`我吃啥
> `R`经典麦辣鸡腿堡套餐

## 0.0.1 `2021-12-26`

`A` 构建框架
️
