from datetime import datetime
from flask import Flask,render_template,flash,redirect,url_for,session,request
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from werkzeug.security import generate_password_hash,check_password_hash



app = Flask(__name__)

app.secret_key = 'ahsg'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:xxxxx@127.0.0.1:3306/novels'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), db.ForeignKey('user.email'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_number'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())

    # 定义与 User 模型的关系
    user = db.relationship('User', backref='history')

    # 定义与 Book 模型的关系
    book = db.relationship('Books', backref='history')

    # 定义与 Chapter 模型的关系
    chapter = db.relationship('Chapters', backref='history')




class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), db.ForeignKey('user.email'), nullable=False)

    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)  # 关联的书籍 ID

    # 定义外键关系
    book = db.relationship('Books', backref='bookmarks')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Books(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(30))
    description = db.Column(db.Text)

class Chapters(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    book_id = db.Column(db.Integer,db.ForeignKey(Books.id),nullable = False)
    chapter_number = db.Column(db.Integer)
    title = db.Column(db.String(30))
    content = db.Column(db.Text)


def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'email' not in session:
            flash("请先登录")
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return decorated_function


@app.context_processor
def inject_username():
    email = session.get('email')
    return dict(email=email)



@app.route('/bookmarks')
@login_required
def bookmarks():
    user_email = session['email']
    bookmarks = Bookmark.query.filter_by(user_email=user_email).all()
    return render_template('bookmarks.html', bookmarks=bookmarks)

# 删除收藏路由
@app.route('/remove_bookmark/<int:bookmark_id>', methods=['POST'])
@login_required
def remove_bookmark(bookmark_id):
    bookmark = Bookmark.query.get_or_404(bookmark_id)
    db.session.delete(bookmark)
    db.session.commit()
    flash('收藏已移除！', 'success')
    return redirect(url_for('bookmarks'))


@app.route('/toggle_bookmark/<int:article_id>', methods=['POST'])
@login_required
def toggle_bookmark(article_id):
    # 获取当前用户的邮箱，这里假设你已经实现了用户认证和登录功能
    user_email = session['email']

    # 获取文章对象
    article = Books.query.get_or_404(article_id)

    # 检查用户是否已经收藏了该文章
    bookmark = Bookmark.query.filter_by(user_email=user_email, book_id=article_id).first()

    # 如果用户已经收藏了文章，并且当前点击的是取消收藏，则删除该收藏记录
    if bookmark and not request.json['checked']:
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({'success': True})

    # 如果用户没有收藏文章，并且当前点击的是收藏，则创建一条新的收藏记录
    if not bookmark and request.json['checked']:
        bookmark = Bookmark(user_email=user_email, book_id=article_id)
        db.session.add(bookmark)
        db.session.commit()
        return jsonify({'success': True})

    # 如果以上条件都不满足，则返回操作失败
    return jsonify({'success': False})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']

        # 检查密码是否匹配
        if password != password2:
            flash('两次密码不匹配！', 'error')
            return redirect(url_for('register'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("该邮箱已经被注册过","error")
            return redirect(url_for('register'))

        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('注册成功，请登录！', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # 查询用户是否存在
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            flash('登录成功！', 'success')
            session['email'] = user.email
            # 这里可以设置登录状态
            return redirect(url_for('index'))
        else:
            flash('邮箱或密码错误！', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email',None)
    flash('已退出登录')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('thefirst.html')


@app.route('/search')
@login_required
def search():
    query = request.args.get('query')
    if query:
        book_results = Books.query.filter(Books.title.like(f'%{query}%')).all()
        if book_results:
            book_id = book_results[0].id
            return redirect(url_for('article',id=book_id))

    else:
        return redirect(url_for('index'))
    return render_template('thefirst.html',not_found=True)




@app.route('/autocomplete', methods=['GET'])
@login_required
def autocomplete():
    query = request.args.get('query')
    if query:
        # 在书籍表中搜索含有关键词的记录
        books = Books.query.filter(Books.title.like(f'%{query}%')).all()
        # 提取匹配的书籍标题
        book_titles = [book.title for book in books]
        return jsonify(book_titles)
    return jsonify([])  # 如果搜索关键词为空，返回空列表






@app.route('/articles')
@login_required
def articles():
    '''db = MysqlUtil()
    sql = 'select * from books order by id DESC limit 5'
    articles = db.fetchall(sql)'''
    articles = Books.query.all()
    if articles:
        return render_template('novels.html',articles=articles)
    else:
        msg = '暂无'
        return render_template('novels.html',msg=msg)


@app.route('/article/<string:id>/')
@login_required
def article(id):
    '''db = MysqlUtil()
    sql = "select chapter_number from chapters where id = '%s'" % id
    chapters = db.fetchall(sql)'''
    chapters = Chapters.query.filter_by(book_id=id)
    return render_template('chapters.html', id=id, chapters=chapters)

@app.route('/article/<string:id>/<string:chapter_number>')
@login_required
def chapters(id,chapter_number):
    '''db = MysqlUtil()
    sql = "select content from chapters where bookid = '%s',chapter_number = '%s'".format(id, chapter_number)'''

    #content = db.fetchall(sql)
    content = Chapters.query.filter_by(book_id=id,chapter_number=chapter_number).first()
    if session.get('email'):
        user_email = session['email']
        history_entry = History(user_email=user_email,book_id=id,chapter_id=chapter_number)
        db.session.add(history_entry)
        db.session.commit()
    return render_template('article.html',content=content)


@app.route('/history')
@login_required
def history_records():
    user_email = session.get('email')
    if user_email:
        contents = History.query.filter_by(user_email=user_email).order_by(History.timestamp.desc()).all()
        return render_template('history.html', contents=contents)
    else:
        return redirect(url_for('index'))
