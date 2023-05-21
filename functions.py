import pymongo
import dns
import os
from flask import session
import random
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

client = pymongo.MongoClient(os.getenv("clientm"))
usersdb = client.Users
profilescol = usersdb.Profiles
hourlycol = usersdb.Hourly

def makeaccount(username, password):
  try:
    passhash = generate_password_hash(password)
    document = [{
      "Username": username,
      "Password": passhash,
      "Money": 500,
      "Land": [0],
      "Hourly": 0,
      "Created": str(datetime.datetime.now()),
      "Description": None
    }]
    profilescol.insert_many(document)
    return True
  except:
    return False

def addcookie(key, value):
  session[key] = value

def delcookie(keyname):
  session.clear()

def getcookie(key):
  try:
    if (x := session.get(key)):
      return x
    else:
      return False
  except:
    return False

def gethashpass(username):
  myquery = { "Username": username }
  mydoc = profilescol.find(myquery)
  for x in mydoc:
    return x['Password']
  return False

# def getuserid(id):
#   myquery = { "_id": int(id) }
#   mydoc = profilescol.find(myquery)
#   for x in mydoc:
#     return True
#   return False

def getuser(username):
  myquery = { "Username": username }
  mydoc = profilescol.find(myquery)
  for x in mydoc:
    if x.get("Deleted", None) == None:
      return x
    return False
  return False

def checkusernamealready(username):
  myquery = { "Username": username }
  mydoc = profilescol.find(myquery)
  for x in mydoc:
    return True
  return False

def additemtogrid(username, item):
  user = getuser(username)
  usergrid = user['Land']
  items = ['Land', 'Grass', 'Water', 'Garden']
  if item not in items:
    return "This is not a real item!"
  price = {"Land": 100, "Grass": 200, "Water": 300, "Garden": 600}
  hourlys = {"Land": 1, "Grass": 2, "Water": 3, "Garden": 6}
  if len(usergrid) == 1500:
    return "You can't have any more grid spaces!"
  if user['Money'] < price[item]:
    return "You don't have enough money!"
  newmoney = user['Money'] - price[item]
  newgrid = usergrid
  newgrid.append(items.index(item))
  user2 = user
  del user2['Land']
  user2['Land'] = newgrid
  del user2['Money']
  user2['Money'] = newmoney
  newhourly = user['Hourly'] + hourlys[item]
  del user2['Hourly']
  user2['Hourly'] = newhourly
  profilescol.delete_one({"Username": username})
  profilescol.insert_many([user2])
  return True

def checkhourly():
  try:
    hourly = {"_id": 1}
    mydoc = hourlycol.find(hourly)
    if mydoc[0]['Hourly'] == False:
      return False
    else:
      return True
  except:
    return True

def rolldice(username, number, bet):
  bet = int(bet)
  if int(bet) < 10:
    return "You have to bet more than 10!"
  if int(bet) > 1000:
    return "You have to bet less than 1000!"
  if getuser(username)['Money'] < int(bet):
    return f"You don't have {str(bet)}!"
  dice = random.randint(1,6)
  if int(dice) == int(number):
    user = getuser(username)
    user2 = user
    money = user2['Money']
    del user2['Money']
    user2['Money'] = int(money) + int(bet * 6)
    delete = {"_id": user['_id']}
    profilescol.delete_one(delete)
    profilescol.insert_many([user2])
    return f"The dice rolled {str(dice)}! You won {str(int(bet) * 6)}!"
  else:
    user = getuser(username)
    user2 = user
    money = user2['Money']
    del user2['Money']
    user2['Money'] = int(money) - int(bet)
    delete = {"_id": user['_id']}
    profilescol.delete_one(delete)
    profilescol.insert_many([user2])
    return f"The dice rolled {str(dice)}! You lost {str(bet)}!"

def flipcoin(username, side, bet):
  bet = int(bet)
  if int(bet) < 10:
    return "You have to bet more than 10!"
  if int(bet) > 250:
    return "You have to bet less than 250!"
  if int(getuser(username)['Money']) < int(bet):
    return f"You don't have {str(bet)}!"
  coin = random.choice(['heads', 'tails'])
  if side == coin:
    user = getuser(username)
    user2 = user
    money = user2['Money']
    del user2['Money']
    user2['Money'] = int(money) + int(bet)
    delete = {"_id": user['_id']}
    profilescol.delete_one(delete)
    profilescol.insert_many([user2])
    return f"The coin flipped {coin}! You won {str(bet)}!"
  else:
    user = getuser(username)
    user2 = user
    money = user2['Money']
    del user2['Money']
    user2['Money'] = int(money) - int(bet)
    delete = {"_id": user['_id']}
    profilescol.delete_one(delete)
    profilescol.insert_many([user2])
    return f"The coin flipped {str(coin)}! You lost {str(bet)}!"

def cupgame(username, number, bet):
  bet = int(bet)
  if int(bet) < 10:
    return "You have to bet more than 10!"
  if int(bet) > 1000:
    return "You have to bet less than 1000!"
  if int(getuser(username)['Money']) < int(bet):
    return f"You don't have {str(bet)}!"
  cup = random.randint(1,3)
  if int(number) == int(cup):
    user = getuser(username)
    user2 = user
    money = user2['Money']
    del user2['Money']
    user2['Money'] = int(money) + int(bet * 3)
    delete = {"_id": user['_id']}
    profilescol.delete_one(delete)
    profilescol.insert_many([user2])
    return f"The ball was in cup number {str(cup)}! You won {str(int(bet) * 3)}!"
  else:
    user = getuser(username)
    user2 = user
    money = user2['Money']
    del user2['Money']
    user2['Money'] = int(money) - int(bet)
    delete = {"_id": user['_id']}
    profilescol.delete_one(delete)
    profilescol.insert_many([user2])
    return f"The ball was in cup number {str(cup)}! You lost {str(bet)}!"

def sellland(username, index):
  try:
    index = int(index)
    user = getuser(username)
    land = user['Land'][int(index)]
    items = ['Land', 'Grass', 'Water', 'Garden']
    landtype = items[land]
    price = {"Land": 50, "Grass": 100, "Water": 150, "Garden": 300}
    getback = price[landtype]
    user2 = user
    newmoney = user2['Money'] + getback
    del user2['Money']
    user2['Money'] = newmoney
    allland = user2['Land']
    del allland[index]
    del user2['Land']
    user2['Land'] = allland
    profilescol.delete_one({"Username": username})
    profilescol.insert_many([user2])
    return True
  except:
    return "That is not real land on your grid!"

def cf(num1,num2):
  n=[]
  for i in range(1, min(num1, num2)+1): 
    if num1%i==num2%i==0: 
      n.append(i)
  return n

def generatequestion():
  length = random.choice([1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900])
  width = random.choice([500, 600, 700, 800, 900, 400, 300, 200, 100, 50])
  allcf = cf(length, width)
  side = random.choice(allcf)
  two = random.randint(1,2)
  if two == 1:
    pass
  else:
    side = side / 2
  answer = (length * width) / (side * side)
  return length, width, side, answer

def solvequestion(length, width, side):
  answer = (length * width) / (side * side)
  return answer

def addmoney(username, money):
  user = getuser(username)
  user2 = user
  oldmoney = user['Money']
  newmoney = oldmoney + money
  del user2['Money']
  user2['Money'] = newmoney
  profilescol.delete_one({"Username": username})
  profilescol.insert_many([user2])

# allvars = generatequestion()
# print(allvars[3])
# solve = solvequestion(allvars[0], allvars[1], allvars[2])
# print(solve)