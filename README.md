
# 📁 web_disk - Flask 网盘系统

这是一个基于 Python Flask 构建的简易网盘系统，支持用户登录、文件管理（上传、下载、重命名、删除）、文件夹创建和文件预览等功能。界面友好，操作简洁，适合个人或小型团队使用。

## 🚀 功能特性

- 用户登录与身份认证（基于 Flask-Login）
- 文件上传、下载、删除、重命名
- 新建文件夹
- 支持网格视图和列表视图切换
- 图片、视频、文本文件预览功能

---

## 📦 环境依赖安装

在运行 `app.py` 之前，需安装以下依赖：

```bash
pip install Flask Flask-Login pymysql Werkzeug
```

---

## ⚙️ 数据库环境配置（MySQL 8）

### 1. 创建数据库

确保你已安装 MySQL 8。使用命令行或其他数据库工具创建数据库：

```sql
CREATE DATABASE web_disk CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

### 2. 初始化数据库表结构

在项目根目录下，执行初始化脚本 `web_disk.sql`：

```bash
mysql -u your_user -p web_disk < web_disk.sql
```

> 请将 `your_user` 替换为你的 MySQL 用户名。

---

## 🛠️ 配置文件说明（`config.ini`）

请在项目根目录中创建或编辑 `config.ini` 文件，填写数据库和应用配置信息：

```ini
[mysql]
host = localhost
port = 3306
user = root
password = 123456
database = web_disk
; 请将 user 和 password 替换为你的实际数据库用户名和密码

[app]
secret_key = your_flask_secret_key
upload_folder = uploads
; upload_folder 是文件上传存储目录，建议使用绝对路径
```

---

## ▶️ 启动项目

```bash
python app.py
```

打开浏览器访问：

```
http://localhost:5000
```
