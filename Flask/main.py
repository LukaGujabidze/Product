from flask import Flask,render_template,url_for,request,redirect,flash
import hashlib

app = Flask(__name__)

@app.route("/logo.png")
def image():
    return render_template("logo.png")

@app.route('/img_avatar2.png')
def png():
    return render_template('img_avatar2.png')    

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home.html', methods=['GET','POST'])
def h():
    return render_template('home.html')    

@app.route('/sign.html', methods=['GET', 'POST'])
def sign():
    return render_template('sign.html')

@app.route('/account.html', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        result = request.form
        name = result.get('uname')
        passowrd = result.get('psw').encode('UTF-8')
        hashed_pass = hashlib.sha256(passowrd).hexdigest()
        mail = result.get('semail')
        file = open('database.txt')
        read_file = file.read()
        if name and hashed_pass and mail in read_file:
            return render_template('account.html', user=name)
        else:
            return render_template('not_account.html', user=name)

    return render_template('account.html')


@app.route('/not_account.html')
def not_acc():
    return render_template('not_account.html')

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


@app.route('/reg_account.html', methods=['GET', 'POST'])
def reg_acc():
    if request.method == 'POST':
        result = request.form
        username = result.get('username')
        email = result.get('email')
        if result.get('passw') == result.get('psw-repeat'):
            password = result.get('psw-repeat').encode('UTF-8')
            hashed_pass = hashlib.sha256(password).hexdigest()
            with open('database.txt','a') as file:
                file.write(f'\n{username}/{email}/{hashed_pass}')
                file.close()
            return render_template('reg_account.html',user=username)
        
        return render_template('reg_account.html',user=username)        

@app.route('/error.html')
def error():
    return render_template('error.html')

@app.route('/privacy.html')
def privasy():
    return render_template('privacy.html')

if __name__ == '__main__':
    app.run(debug=True)






