from flask import Flask, render_template, redirect, request
import os
from functions import getcookie, getuser, gethashpass, addcookie, checkusernamealready, makeaccount, delcookie, additemtogrid, checkhourly, sellland, cupgame, flipcoin, rolldice, generatequestion, solvequestion, addmoney
from string import printable
from werkzeug.security import check_password_hash
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

@app.route("/")
def index():
  return render_template("index.html", logged=getcookie("User"))

@app.route("/login")
def loginpage():
  if getcookie("User") == False:
    return render_template("login.html")
  else:
    return redirect("/")

@app.route("/signup")
def signuppage():
  if getcookie("User") == False:
    return render_template("signup.html")
  else:
    return redirect("/")

@app.route("/login", methods=['GET', 'POST'])
def loginfunc():
  if request.method == 'POST':
    if getcookie("User") != False:
      return redirect("/")
    username = request.form['username']
    if getuser(username) == False:
      return render_template("error.html", error="That is not a username!")
    password = request.form['password']
    if check_password_hash(gethashpass(username), password) == False:
      return render_template("error.html", error="Wrong password!")
    addcookie("User", username)
    return redirect("/")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
  if request.method == 'POST':
    if getcookie("User") != False:
      return redirect("/")
    username = request.form['username']
    if len(username) > 25:
      return render_template("error.html", error="Your username cannot have more than 25 letters!")
    if len(username) < 2:
      return render_template("error.html", error="You have to have more than 2 letters in your username!")
    if set(username).difference(printable):
      return render_template("error.html", error="Your username cannot contain any special characters!")
    if username != username.lower():
      return render_template("error.html", error="Your username has to be all lowercase!")
    if checkusernamealready(username) == True:
      return render_template("error.html", error="A user already has this username! Try another one.")
    password = request.form['password']
    passworda = request.form['passwordagain']
    if password != passworda:
      return render_template("error.html", error="The two passwords don't match!")
    if len(password) > 25:
      return render_template("error.html", error="Your password cannot have more than 25 letters!")
    if len(password) < 2:
      return render_template("error.html", error="You have to have more than 2 letters in your password!")
    if set(password).difference(printable):
      return render_template("error.html", error="Your password cannot contain any special characters!")
    func = makeaccount(username, password)
    if func == True or func == None:
      addcookie("User", username)
      return redirect("/")
    else:
      return render_template("error.html", error=f"Error! Account not created! Try again.")

@app.route("/logout")
def logout():
  if getcookie("User") == False:
    return redirect("/")
  delcookie("all")
  return redirect("/")

@app.route("/grid")
def grid():
  if getcookie("User") == False:
    return redirect("/login")
  return render_template("grid.html", user=getuser(getcookie("User")))

@app.route("/additemtogrid/<item>")
def additemtogridfunc(item):
  if getcookie("User") == False:
    return redirect("/login")
  func = additemtogrid(getcookie("User"), item)
  ishourly = checkhourly()
  if ishourly == True:
    return render_template("error.html", error="Hourlies is being handed out right now. Try again in a minute")
  if func == True:
    return redirect("/grid")
  else:
    return render_template("error.html", error=func)

@app.route("/profile")
def profile():
  if getcookie("User") == False:
    return redirect("/login")
  user = getuser(getcookie("User"))
  user['Value'] = user['Hourly'] * 100
  return render_template("profile.html", user=user)

@app.route("/whatarepolyominoes")
def whatarepolyominoes():
  return render_template("what.html", logged=getcookie("User"))

@app.route("/sellland/<index>")
def selllandpage(index):
  if getcookie("User") == False:
    return redirect("/login")
  func = sellland(getcookie("User"), index)
  if func == True:
    return redirect("/grid")
  else:
    return render_template("grid.html", text=func, user=getuser(getcookie("User")))

@app.route("/cupgame", methods=['POST', 'GET'])
def cupgamefunc():
  if request.method == 'POST':
    if getcookie("User") == False:
      return redirect("/login")
    bet = request.form['bet']
    number = request.form['number']
    func = cupgame(getcookie("User"), number, bet)
    return render_template("gambling.html", text=func)

@app.route("/flipcoin", methods=['POST', 'GET'])
def flipcoinfunc():
  if request.method == 'POST':
    if getcookie("User") == False:
      return redirect("/login")
    side = request.form['side']
    bet = request.form['bet']
    func = flipcoin(getcookie("User"), side, bet)
    return render_template("gambling.html", text=func)

@app.route("/rolldice", methods=['POST', 'GET'])
def rolldicefunc():
  if request.method == 'POST':
    if getcookie("User") == False:
      return redirect("/login")
    number = request.form['number']
    bet = request.form['bet']
    func = rolldice(getcookie("User"), number, bet)
    return render_template("gambling.html", text=func)

@app.route("/gambling")
def gambling():
  if getcookie("User") == False:
    return redirect("/login")
  return render_template("gambling.html")

@app.route("/question")
def questionpage():
  if getcookie("User") == False:
    return redirect("/login")
  question = generatequestion()
  length = question[0]
  width = question[1]
  side = question[2]
  return render_template("question.html", length=length, width=width, side=side)

@app.route("/questions/<length>/<width>/<side>", methods=['POST', 'GET'])
def questionanswer(length, width, side):
  if request.method == 'POST':
    if getcookie("User") == False:
      return redirect("/login")
    try:
      guess = request.form['number']
      answer = solvequestion(float(length), float(width), float(side))
      if float(guess) == float(answer):
        addmoney(getcookie("User"), 10)
        question = generatequestion()
        length = question[0]
        width = question[1]
        side = question[2]
        return render_template("question.html", text="You got the question right and got 10 Money! Try another question!", length=length, width=width, side=side)
      else:
        question = generatequestion()
        length = question[0]
        width = question[1]
        side = question[2]
        return render_template("question.html", text="You got the question wrong and didn't get any money! Try another question!", length=length, width=width, side=side)
    except:
      question = generatequestion()
      length = question[0]
      width = question[1]
      side = question[2]
      return render_template("question.html", text="An error occured, please try another question!", length=length, width=width, side=side)