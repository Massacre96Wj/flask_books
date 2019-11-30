from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

'''
1.配置数据库
2.添加书和作者
3.添加数据
4.使用模板查询数据
5.使用wtf显示处理
6.实现逻辑处理
'''
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:123@localhost:3306/flask_books"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'books'

# 创建数据库对象
db = SQLAlchemy(app)

# 定义书和作者模型
class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)

    # 引用
    books = db.relationship('Book', backref='author')

    # 定义将来查看的格式
    def __repr__(self):
        return 'Author:{}'.format(self.name)

class Book(db.Model):

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    def __repr__(self):
        return 'Book:{0}{1}'.format(self.name, self.author_id)

# 创建表单类
class AuthorForm(FlaskForm):
    author = StringField('作者', validators=[DataRequired()])
    book = StringField('书籍', validators=[DataRequired()])
    submit = SubmitField('提交')


@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    author = Author.query.get(author_id)

    if author:
        try:
            # 先删除书籍再删除作者
            Book.query.filter_by(author_id=author.id).delete
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash("删除作者失败")
            db.session.rollback()
    else:
        flash('作者找不到')

    return redirect(url_for('index'))


@app.route('/delete_book/<book_id>')
def delete_book(book_id):

    # 1.查询
    book = Book.query.get(book_id)

    # 2.判断
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除书籍失败')
            db.session.rollback()
    else:
        # 3.提示出错
        flash('书籍找不到')

    # redirect()重定向，需要传入网址
    # url_for()传入视图函数名，返视图函数名的路由地址
    return redirect(url_for('index'))


@app.route("/", methods=['GET', 'POST'])
def index():
    # 创建自定义表单
    author_form = AuthorForm()

    '''
    验证逻辑：
    1.调用wtf验证
    2.通过后获取数据
    3，判断作者是否存在
    4.判断书籍是否存在，如果没有添加，反之提示错误
    5.作者不存在，添加作者书籍
    6.验证不通过提示错误
    '''
    if author_form.validate_on_submit():
        author_name = author_form.author.data
        book_name = author_form.book.data

        author = Author.query.filter_by(name=author_name).first()
        if author:
            book = Book.query.filter_by(name=book_name).first()
            if book:
                flash('已经存在同名书籍')
            else:
                try:
                    new_book = Book(name=book_name, author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    flash('添加书失败')
                    db.session.rollback()
        else:
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()

                new_book = Book(name=book_name, author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()

            except Exception as e:
                print(e)
                flash('添加作者书籍失败')
                db.session.rollback()
    else:
        if request.method == 'POST':
            flash("参数不全")

    # 查询所有的作者信息传给模板
    authors = Author.query.all()
    return render_template("books.html", authors=authors, form=author_form)


db.drop_all()
db.create_all()

#  生成数据
au1 = Author(name='老王')
au2 = Author(name='老代')
au3 = Author(name='老刘')

db.session.add_all([au1, au2, au3])
db.session.commit()

bk1 = Book(name='老王回忆录', author_id=au1.id)
bk2 = Book(name='我读书少', author_id=au1.id)
bk3 = Book(name='征服', author_id=au2.id)
bk4 = Book(name='少男', author_id=au3.id)
bk5 = Book(name='少女', author_id=au3.id)

db.session.add_all([bk1, bk2, bk3, bk4, bk5])
db.session.commit()

if __name__ == '__main__':
    app.run()

