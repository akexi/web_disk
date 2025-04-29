import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from config_manager import SECRET_KEY, UPLOAD_FOLDER
from db_manager import get_db, close_db
from urllib.parse import quote

# 支持的文件预览后缀
PREVIEW_MIME = {
    'image': ['.png', '.jpg', '.jpeg', '.gif'],
    'video': ['.mp4', '.ogg', '.webm' ,'mov','m4v']
}

# 修改每页展示最大文件数量
view_page = 24  # 平铺每页展示最大文件数
list_page = 12  # 列表每页展示最大文件数

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 限制 5GB
app.teardown_appcontext(close_db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, uid, username, admin):
        self.id = uid
        self.username = username
        self.admin = admin

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM sysuser WHERE UserID=%s", (user_id,))
        row = cur.fetchone()
    return User(row['UserID'], row['UserName'], row['admin']) if row else None

def format_size(num_bytes):
    """将字节数格式化为 B/KB/MB/GB"""
    for unit in ['B','KB','MB','GB','TB']:
        if num_bytes < 1024:
            return f"{num_bytes:.2f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.2f}PB"

def build_breadcrumbs(parent_id):
    crumbs = [{'id': 'root', 'name': '根目录'}]
    if parent_id and parent_id != 'root':
        db = get_db()
        pid = int(parent_id)
        stack = []
        while pid:
            with db.cursor() as cur:
                cur.execute("SELECT id,name,parent_id FROM files WHERE id=%s", (pid,))
                row = cur.fetchone()
            if not row: break
            stack.append({'id': str(row['id']), 'name': row['name']})
            pid = row['parent_id']
        crumbs.extend(reversed(stack))
    return crumbs

def get_full_path(file):
    crumbs = build_breadcrumbs(file['parent_id'])
    names = [c['name'] for c in crumbs[1:]]
    return '/' + '/'.join(names) if names else '/'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        with db.cursor() as cur:
            # 查询用户信息
            cur.execute("SELECT * FROM sysuser WHERE UserName=%s", (username,))
            row = cur.fetchone()

        if row and check_password_hash(row['passwd'], password):  # 使用哈希密码验证
            # 登录用户
            login_user(User(row['UserID'], row['UserName'], row['admin']))
            return redirect(url_for('folder_view', parent_id='root'))

        flash('用户名或密码错误')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return redirect(url_for('folder_view', parent_id='root'))


@app.route('/folder/<parent_id>')
@login_required
def folder_view(parent_id):
    # 获取页码，默认为第1页
    page = request.args.get('page', 1, type=int)

    # 根据视图模式设置每页显示的文件数量
    view_mode = request.args.get('view', 'list')
    if view_mode == 'list':
        per_page = list_page  # 列表视图每页显示X个文件
    else:
        per_page = view_page  # 平铺视图每页显示X个文件

    db = get_db()
    if parent_id == 'root':
        sql = "SELECT * FROM files WHERE parent_id IS NULL AND user_id=%s"
        args = (current_user.id,)
    else:
        sql = "SELECT * FROM files WHERE parent_id=%s AND user_id=%s"
        args = (parent_id, current_user.id)

    # 获取总文件数
    with db.cursor() as cur:
        cur.execute(sql, args)
        total_files = cur.fetchall()
    total_files = len(total_files)

    # 计算总页数
    total_pages = (total_files // per_page) + (1 if total_files % per_page > 0 else 0)

    # 获取当前页的数据
    offset = (page - 1) * per_page
    with db.cursor() as cur:
        cur.execute(sql + " ORDER BY is_folder DESC, name ASC LIMIT %s OFFSET %s", args + (per_page, offset))
        items = cur.fetchall()

    for item in items:
        item['path'] = get_full_path(item)
        if not item['is_folder']:
            folder = os.path.join(app.config['UPLOAD_FOLDER'], str(item['id']))
            encoded = quote(item['name'])
            fpath = os.path.join(folder, encoded)
            try:
                size = os.path.getsize(fpath)
            except OSError:
                size = 0
            item['size'] = format_size(size)
        else:
            item['size'] = ''

    breadcrumbs = build_breadcrumbs(parent_id)

    return render_template('folder_view.html',
                           items=items,
                           parent_id=parent_id,
                           breadcrumbs=breadcrumbs,
                           page=page,
                           total_pages=total_pages,
                           view_mode=view_mode)


@app.route('/search')
@login_required
def search():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    pattern = f"%{q}%"

    # 根据视图模式设置每页显示的文件数量
    view_mode = request.args.get('view', 'list')
    if view_mode == 'list':
        per_page = list_page  # 列表视图每页显示X个文件
    else:
        per_page = view_page  # 平铺视图每页显示X个文件

    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM files WHERE user_id=%s AND name LIKE %s ORDER BY is_folder DESC, name ASC",
            (current_user.id, pattern)
        )
        total_files = cur.fetchall()
    total_files = len(total_files)
    total_pages = (total_files // per_page) + (1 if total_files % per_page > 0 else 0)

    offset = (page - 1) * per_page
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM files WHERE user_id=%s AND name LIKE %s ORDER BY is_folder DESC, name ASC LIMIT %s OFFSET %s",
            (current_user.id, pattern, per_page, offset)
        )
        items = cur.fetchall()

    for item in items:
        item['path'] = get_full_path(item)
        if not item['is_folder']:
            folder = os.path.join(app.config['UPLOAD_FOLDER'], str(item['id']))
            encoded = quote(item['name'])
            fpath = os.path.join(folder, encoded)
            try:
                size = os.path.getsize(fpath)
            except OSError:
                size = 0
            item['size'] = format_size(size)
        else:
            item['size'] = ''

    breadcrumbs = [{'id': None, 'name': f"搜索: {q}"}]

    return render_template('folder_view.html',
                           items=items,
                           parent_id='root',
                           breadcrumbs=breadcrumbs,
                           search_query=q,
                           page=page,
                           total_pages=total_pages,
                           view_mode=view_mode)


@app.route('/new_folder', methods=['POST'])
@login_required
def new_folder():
    raw = request.form.get('parent_id')
    pid = None if raw == 'root' else int(raw)
    name = request.form['folder_name']
    db = get_db()
    with db.cursor() as cur:
        cur.execute("INSERT INTO files (user_id,name,parent_id,is_folder) VALUES (%s,%s,%s,1)",
                    (current_user.id, name, pid))
        db.commit()
    return redirect(url_for('folder_view', parent_id=raw))

@app.route('/rename', methods=['POST'])
@login_required
def rename():
    file_id = request.form['file_id']
    new_name = request.form['new_name']
    parent = request.form.get('parent_id', 'root')

    db = get_db()
    with db.cursor() as cur:
        # 1. 先取出旧名字和类型
        cur.execute(
            "SELECT name, is_folder FROM files WHERE id=%s AND user_id=%s",
            (file_id, current_user.id)
        )
        row = cur.fetchone()
        if not row:
            flash('文件不存在')
            return redirect(url_for('folder_view', parent_id=parent))

        old_name = row['name']
        is_folder = row['is_folder']

        # 2. 如果是文件，重命名磁盘上的文件
        if not is_folder:
            folder = os.path.join(app.config['UPLOAD_FOLDER'], str(file_id))
            old_encoded = quote(old_name)
            new_encoded = quote(new_name)
            old_path = os.path.join(folder, old_encoded)
            new_path = os.path.join(folder, new_encoded)
            try:
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
            except OSError as e:
                flash(f'文件磁盘重命名失败：{e}')
                return redirect(url_for('folder_view', parent_id=parent))

        # 3. 更新数据库里的 name 字段
        cur.execute(
            "UPDATE files SET name=%s WHERE id=%s AND user_id=%s",
            (new_name, file_id, current_user.id)
        )
        db.commit()

    flash('重命名成功')
    return redirect(url_for('folder_view', parent_id=parent))

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    file_id = request.form['file_id']
    parent = request.form.get('parent_id', 'root')
    if not current_user.admin:
        flash('仅管理员可删除')
        return redirect(url_for('folder_view', parent_id=parent))
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT name,is_folder FROM files WHERE id=%s AND user_id=%s",
                    (file_id, current_user.id))
        row = cur.fetchone()
        if row['is_folder']:
            import shutil
            dir_path = os.path.join(app.config['UPLOAD_FOLDER'], str(file_id))
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
        else:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                     str(file_id), quote(row['name']))
            if os.path.exists(file_path):
                os.remove(file_path)
        cur.execute("DELETE FROM files WHERE id=%s AND user_id=%s",
                    (file_id, current_user.id))
        db.commit()
    flash(f'已删除: {row["name"]}')
    return redirect(url_for('folder_view', parent_id=parent))

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    raw = request.form.get('parent_id')
    pid = None if raw == 'root' else int(raw)
    files = request.files.getlist('files')
    db = get_db()

    try:
        for f in files:
            fn = f.filename
            encoded_name = quote(fn)
            with db.cursor() as cur:
                cur.execute("INSERT INTO files (user_id,name,parent_id,is_folder) VALUES (%s,%s,%s,0)",
                            (current_user.id, fn, pid))
                fid = cur.lastrowid
                db.commit()
            save_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(fid))
            os.makedirs(save_dir, exist_ok=True)
            f.save(os.path.join(save_dir, encoded_name))

        return jsonify({'status': 'success'})

    except Exception as e:
        print("上传失败：", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/preview/<int:file_id>')
@login_required
def preview(file_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM files WHERE id=%s AND user_id=%s",
                    (file_id, current_user.id))
        row = cur.fetchone()
    if not row or row['is_folder']:
        flash('无法预览')
        return redirect(request.referrer or url_for('index'))
    folder = os.path.join(app.config['UPLOAD_FOLDER'], str(file_id))
    encoded = quote(row['name'])
    return send_from_directory(folder, encoded)

@app.route('/download/<int:file_id>')
@login_required
def download(file_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM files WHERE id=%s AND user_id=%s",
                    (file_id, current_user.id))
        row = cur.fetchone()
    if not row or row['is_folder']:
        flash('无法下载该项')
        return redirect(request.referrer or url_for('index'))

    folder = os.path.join(app.config['UPLOAD_FOLDER'], str(file_id))
    encoded = quote(row['name'])
    return send_from_directory(
        folder,
        encoded,
        as_attachment=True,
        download_name=row['name']
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    db = get_db()
    cursor = db.cursor()

    # 获取所有可选的密保问题
    cursor.execute("SELECT QuestionID, Question FROM security_questions")
    questions = cursor.fetchall()  # [(1, '...'), (2, '...'), ...]

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 密码一致性检查
        if password != confirm_password:
            flash('两次密码输入不一致', 'danger')
            return render_template('register.html', questions=questions)

        # 获取并验证三道密保
        q1 = request.form.get('question1')
        q2 = request.form.get('question2')
        q3 = request.form.get('question3')
        a1 = request.form.get('answer1').strip()
        a2 = request.form.get('answer2').strip()
        a3 = request.form.get('answer3').strip()

        # 检查是否都选择了密保且答案不为空
        if not all([q1, q2, q3, a1, a2, a3]):
            flash('请完整填写三道密保问题及答案', 'danger')
            return render_template('register.html', questions=questions)
        # 检查密保问题不重复
        if len({q1, q2, q3}) < 3:
            flash('请选择互不相同的密保问题', 'danger')
            return render_template('register.html', questions=questions)

        # 检查用户名是否已存在
        cursor.execute("SELECT UserID FROM sysuser WHERE UserName = %s", (username,))
        if cursor.fetchone():
            flash('用户名已存在', 'danger')
            return render_template('register.html', questions=questions)

        # 插入用户
        password_hash = generate_password_hash(password)
        try:
            cursor.execute(
                "INSERT INTO sysuser (UserName, passwd ,admin) VALUES (%s, %s ,1)",
                (username, password_hash)
            )
            user_id = cursor.lastrowid

            # 插入三条密保记录
            sec_data = [
                (user_id, q1, a1),
                (user_id, q2, a2),
                (user_id, q3, a3),
            ]
            cursor.executemany(
                "INSERT INTO user_security (UserID, QuestionID, Answer) VALUES (%s, %s, %s)",
                sec_data
            )

            db.commit()
            flash('注册成功，请登录', 'success')
            return render_template('register.html', registered=True)
        except Exception as e:
            db.rollback()
            flash(f"注册失败: {str(e)}", 'danger')
            return render_template('register.html', questions=questions)

    # GET 请求展示注册页，并传递所有密保问题
    return render_template('register.html', questions=questions)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """
    step = 'username'  —— 输入用户名
    step = 'questions' —— 回答密保
    step = 'reset'     —— 重置密码表单（含确认密码）
    step = 'success'   —— 显示重置成功弹窗
    """
    db = get_db()
    cursor = db.cursor()

    # —— GET：首次进入，显示用户名输入
    if request.method == 'GET':
        return render_template('forgot_password.html', step='username')

    step = request.form.get('step')

    # —— 第一步：用户名
    if step == 'username':
        username = request.form['username'].strip()
        cursor.execute("SELECT UserID FROM sysuser WHERE UserName=%s", (username,))
        user = cursor.fetchone()
        if not user:
            flash('用户名不存在', 'error')
            return redirect(url_for('forgot_password'))

        cursor.execute("""
            SELECT q.QuestionID, q.Question
              FROM security_questions q
              JOIN user_security us ON q.QuestionID=us.QuestionID
             WHERE us.UserID=%s
             LIMIT 3
        """, (user['UserID'],))
        questions = cursor.fetchall()
        return render_template(
            'forgot_password.html',
            step='questions',
            user_id=user['UserID'],
            username=username,
            questions=questions
        )

    # —— 第二步：验证密保答案
    if step == 'questions':
        user_id = request.form['user_id']
        qids    = request.form.getlist('question_ids')
        answers = request.form.getlist('answers')
        correct = 0
        for qid, ans in zip(qids, answers):
            cursor.execute(
                "SELECT 1 FROM user_security WHERE UserID=%s AND QuestionID=%s AND Answer=%s",
                (user_id, qid, ans.strip())
            )
            if cursor.fetchone():
                correct += 1

        if correct < 2:
            flash('密保答案错误，请至少答对两题', 'error')
            return redirect(url_for('forgot_password'))

        # 进入重置密码表单
        return render_template('forgot_password.html', step='reset', user_id=user_id)

    # —— 第三步：提交新密码 & 验证确认密码
    if step == 'reset':
        user_id      = request.form['user_id']
        new_pw       = request.form['new_password'].strip()
        confirm_pw   = request.form['confirm_password'].strip()

        if new_pw != confirm_pw:
            flash('两次输入的密码不一致', 'error')
            return render_template('forgot_password.html', step='reset', user_id=user_id)

        hashed = generate_password_hash(new_pw)
        cursor.execute(
            "UPDATE sysuser SET passwd=%s WHERE UserID=%s",
            (hashed, user_id)
        )
        db.commit()
        # 显示成功弹窗
        return render_template('forgot_password.html', step='success')

    # —— 兜底
    flash('操作异常，请重试', 'error')
    return redirect(url_for('forgot_password'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
