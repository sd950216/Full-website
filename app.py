import os
import smtplib
from email.mime.text import MIMEText

from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

# -----------------------------------
app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(16)  # Set a secret key for session management
db = SQLAlchemy(app)

class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    message = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.message}')"


db.create_all()


def send_mail(msg):
    if msg is None:
        return "Error: msg cannot be None"

    sender = os.environ.get('my_email')
    recipient = os.environ.get('recipient_email')
    password = os.environ.get('my_password')
    subject = "Message from your website"
    content = f"Hello Trap,\n\nThis is an automated message from: {msg['name']}\nMessage: {msg['message']}"

    message = MIMEText(content, 'plain', 'utf-8')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = recipient

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.ehlo()
            server.login(sender, password)
            server.sendmail(sender, recipient, message.as_string())
            print("Email sent successfully")

            data = Database(name=msg['name'], email=msg['email'], message=msg['message'])
            db.session.add(data)
            db.session.commit()

    except Exception as e:
        print("Failed to send email")
        print(e)


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if 'success' in session:
            return render_template("index.html", msg_sent=session['success'])

        data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'message': request.form['message'],
        }

        send_mail(data)
        session['success'] = True
        return render_template("index.html", msg_sent=True)

    else:
        session.pop('success', None)
        return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
