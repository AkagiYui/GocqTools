# GocqTools

### 管理Go-cqhttp的工具

立项日期: 2021-12-26

自己玩玩，练习Python用的

2022新年快乐

***
使用了`SQLAlchemy` `bottle` `paste`

支持`.env`文件覆盖`config.json`
***
# 更新内容
## v0.0.4 `2022-01-03`
优化 代码结构

新增 `bottle`web框架
## v0.0.3 `2021-12-29`
新增 终止信号捕抓

新增 `GocqConnection.is_connected()`

新增 `GocqConnection`心跳检测

优化 `mysql连接关闭`

优化 `SQLAlchemy引擎`改为`PyMySQL`

优化 `我吃啥`
```
发送：有啥吃
回复：胡辣汤

发送：都有啥吃
回复：胡辣汤 盖浇饭
```
## v0.0.2 `2021-12-27`
新增 `我吃啥`
```
发送：我吃啥 新增 胡辣汤
回复：已新增 胡辣汤

发送：我吃啥
回复：胡辣汤
```
## v0.0.1 `2021-12-26`
构建框架
