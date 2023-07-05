from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

all_books = []

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new_books_collection.db"
db = SQLAlchemy()
db.init_app(app)


class Book(db.Model):
    name = db.Column(db.String(250), primary_key=True, unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/', methods=["GET", "POST"])
def home():
    if len(all_books) == 0:
        with app.app_context():
            all_books_object = Book.query.all()
            for book in all_books_object:
                my_book = {}
                my_book["name"] = book.name
                my_book["author"] = book.author
                my_book["rating"] = book.rating
                all_books.append(my_book)

    if request.method == "POST":
        data = request.form
        new_data = {}
        new_data["name"] = data["name"]
        new_data["author"] = data["author"]
        new_data["rating"] = data["rating"]
        all_books.append(new_data)
        print(all_books)
        with app.app_context():
            new_book = Book(name=data["name"], author=data["author"], rating=data["rating"])
            db.session.add(new_book)
            db.session.commit()

        print(all_books)

    return render_template("index.html", all_books=all_books)


@app.route("/add")
def add():
    return render_template("add.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        # UPDATE RECORD
        # this method is used for method "POST"
        book_name = request.form["name"]
        book_to_update = db.get_or_404(Book, book_name)
        book_to_update.rating = request.form["rating"]
        db.session.commit()

        # Cleaning the list
        all_books.clear()
        with app.app_context():
            all_books_object = Book.query.all()
            for book in all_books_object:
                my_book = {}
                my_book["name"] = book.name
                my_book["author"] = book.author
                my_book["rating"] = book.rating
                all_books.append(my_book)

        return redirect(url_for('home'))

    book_name = request.args.get('name')
    book_selected = db.get_or_404(Book, book_name)
    return render_template("edit.html", book=book_selected)


@app.route("/delete")
def delete():
    # this method is used for method "GET"
    book_name = request.args.get('name')
    # DELETE A RECORD BY ID
    # book_to_delete = db.get_or_404(Book, book_name)
    # Alternative way to select the book to delete.
    book_to_delete = db.session.execute(db.select(Book).where(Book.name == book_name)).scalar()
    db.session.delete(book_to_delete)
    db.session.commit()
    all_books.clear()
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True)
