from flask import Flask, render_template, redirect, url_for, request, make_response, session
import os

from sqlalchemy import create_engine, text

app = Flask(__name__)

app.secret_key = "flask_blogs"

UPLOAD_FOLDER = "static/images"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

connection_string = "mysql+mysqlconnector://root:@localhost/flask_blogs"
engin = create_engine(connection_string, echo=True)

blogs = []


@app.route("/")
def home():
    with engin.connect() as conn:

        result = conn.execute(text(
            "SELECT blogs.*, user_tbl.fname, user_tbl.lname FROM blogs JOIN user_tbl ON blogs.user_id = user_tbl.user_id"))
        blogs = []
        for row in result.all():
            blogs.append(row)

        print(len(blogs))

    return render_template("home.html", blogs=blogs, title="Home")


@app.route("/login", methods=['POST', 'GET'])
def login():

    showAlert = False

    if request.method == 'GET':
        return render_template("login.html", showAlert=showAlert, title="Login")
    elif request.method == 'POST':
        data = request.form

        with engin.connect() as conn:

            query = "SELECT * FROM user_tbl WHERE email = :email AND password = :password"

            result = conn.execute(text(query), {
                "email": data["email"],
                "password": data["password"],
            })

            print("row count ", result.rowcount)

            if result.rowcount == 1:
                session['user_id'] = result.all()[0][0]
                return redirect(url_for('home'))

            showAlert = True
            return render_template("login.html", showAlert=showAlert, title="Login")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html", title="Register")
    elif request.method == 'POST':
        data = request.form
        print(data)

        with engin.connect() as conn:

            query = "INSERT INTO user_tbl(fname, lname, email, password, address, city, state, zip) VALUES (:fname, :lname, :email, :password, :address, :city, :state, :zip)"

            result = conn.execute(text(query), {
                "fname": data["fname"],
                "lname": data["lname"],
                "email": data["email"],
                "address": data["address"],
                "password": data["password"],
                "city": data["city"],
                "state": data["state"],
                "zip": data["zip"],
            })

            conn.commit()

            if result.rowcount == 1:
                return redirect(url_for("login"))

        return render_template("register.html", title="Register")

    return "<h3> Invalid Request </h3>"


@app.route("/addblog", methods=['GET', 'POST'])
def addBlog():

    if request.method == 'GET':
        return render_template("addblog.html")
    elif request.method == 'POST':

        data = request.form
        image = request.files['image']
        imageName = image.filename
        user_id = session['user_id']

        query = "INSERT INTO blogs (title, description, image, user_id) VALUES (:title, :description, :image, :user_id)"

        with engin.connect() as conn:

            result = conn.execute(text(query), {
                "title": data['title'],
                "description": data['description'],
                "image": imageName,
                "user_id": user_id,
            })

            conn.commit()

        image.save(os.path.join(app.config['UPLOAD_FOLDER'], imageName))
        return redirect(url_for('home'))


@app.route("/myblogs")
def myblogs():

    query = "SELECT blogs.*, user_tbl.fname, user_tbl.lname FROM blogs JOIN user_tbl ON blogs.user_id = user_tbl.user_id WHERE blogs.user_id = :user_id"

    with engin.connect() as conn:

        result = conn.execute(text(query), {
            "user_id": session['user_id']
        })

        blogs = []

        for row in result.all():
            blogs.append(row)

    return render_template("myblogs.html", blogs=blogs)


@app.route("/blog_details/<blog_id>")
def blog_details(blog_id):

    query = "SELECT blogs.*, user_tbl.fname, user_tbl.lname FROM blogs JOIN user_tbl ON blogs.user_id = user_tbl.user_id WHERE blogs.blog_id = :blog_id"

    with engin.connect() as conn:

        result = conn.execute(text(query), {
            "blog_id": blog_id
        })

        blog = result.first()

        return render_template("blog_details.html", blog=blog)


@app.route("/edit_blog/<blog_id>", methods=['GET', 'POST'])
def edit_blog(blog_id):

    if request.method == 'GET':

        query = "SELECT blogs.*, user_tbl.fname, user_tbl.lname FROM blogs JOIN user_tbl ON blogs.user_id = user_tbl.user_id WHERE blogs.blog_id = :blog_id"

        with engin.connect() as conn:

            result = conn.execute(text(query), {
                "blog_id": blog_id
            })

            blog = result.first()

            return render_template('edit_blog.html', blog=blog)

    if request.method == 'POST':

        data = request.form

        query = "UPDATE blogs SET title = :title, description = :description WHERE  blog_id = :blog_id"

        with engin.connect() as conn:

            result = conn.execute(text(query), {
                "title": data['title'],
                "description": data["description"],
                "blog_id": blog_id
            })

            conn.commit()

            return redirect(url_for('myblogs'))


@app.route("/delete_blog/<blog_id>")
def delete_blog(blog_id):

    query = "DELETE FROM blogs WHERE blog_id = :blog_id"

    with engin.connect() as conn:

        result = conn.execute(text(query), {
            "blog_id": blog_id
        })

        conn.commit()

        return redirect(url_for('myblogs'))


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
