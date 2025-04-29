# web_disk Flask 网盘系统

这是一个使用 Python Flask 构建的简易网盘系统，支持用户登录、文件管理（上传、下载、重命名、删除）、文件夹创建、文件预览等功能，界面友好，适合个人或小型团队使用。

## 🚀 功能特性

- 用户登录与身份认证（基于 Flask-Login）
- 文件上传
- 文件下载、删除、重命名
- 支持网格视图和列表视图切换
- 图片、视频、文本文件预览

## 运行app.py前安装依赖环境
pip install Flask Flask-Login pymysql Werkzeug

## ⚙️ 数据库环境配置
1. 创建数据库
首先，确保你已经安装了。使用 MySQL 客户端或者其他数据库管理工具，创建一个名为 web_disk 的数据库：

2. 执行数据库初始化脚本
在项目的根目录下，使用以下命令执行 migrations.sql 文件，以初始化数据库表结构：

mysql -u your_user -p webdisk_db < migrations.sql
请将 your_user 替换为你的 MySQL 用户名。执行该命令后，系统会提示你输入密码。

如果你使用的是 GUI 工具（如 MySQL Workbench 或 phpMyAdmin），也可以直接加载并执行 migrations.sql 文件。

3. 配置数据库连接
编辑 config.ini 文件，填写你的数据库连接信息：

ini
复制
编辑
[mysql]
host = localhost
user = your_user
password = your_password
database = webdisk_db
请将 your_user 和 your_password 替换为你实际的数据库用户名和密码。
