import os
import smtplib
from email.mime.text import MIMEText

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

# -----------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    message = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.message}')"


# db.create_all()

def sendmail(msg):
    print(msg)
    if msg is None:
        print("Error: msg cannot be None")
    sender = os.environ.get('my_email')
    recipient = "meen79508@gmail.com"
    password = os.environ.get('my_password')
    subject = "msg from ur own website"
    content = f"hello Trap , \n\n this is an automated message from : {msg['name']} \n and msg is : {msg['message']}"

    message = MIMEText(content,'plain', 'utf-8')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = recipient

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
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
    finally:
        server.quit()


success = False


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    global success
    if request.method == 'POST':
        if success:
            return render_template("index.html", success=success)
        data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'message': request.form['message'],
        }
        sendmail(data)
        event = True
        success = event

        return render_template("index.html", msg_sent=event)

    else:
        success = False
        return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
