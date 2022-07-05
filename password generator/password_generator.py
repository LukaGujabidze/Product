import random
import string
from flask import Flask,render_template,request

app = Flask(__name__)

def password_gen():
    upper_letters = random.choice(string.ascii_uppercase)
    lower_letters = random.choice(string.ascii_lowercase)
    numbers = random.choice(string.digits)
    special_char = random.choice(string.punctuation)

    # List containing 4 different types of characters
    password_list = [upper_letters, lower_letters, numbers, special_char]

    password = random.choice(password_list)
    return password


def func(self):    
    password_character = []

    for count in range(0, self):
        password_character.append(password_gen())
    

    return "".join(password_character)


@app.route('/')
def index():
   return render_template('index.html')

@app.route('/index.html')
def index1():
   return render_template('index.html')   


@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      char = result.get('char')
      password = func(int(char))
      return render_template("result.html",password = password)


if __name__ == '__main__':
   app.run(debug = True)