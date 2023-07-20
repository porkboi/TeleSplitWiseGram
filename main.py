import telebot
import json
from datetime import datetime
from telebot import types
import pytz
from itertools import combinations

class transaction:
    def __init__(self,value):
        self.currency = "MYR"
        self.pax = None
        self.value = None
        self.personlist = None
        self.gstservice = None

def read_json_file(key):
    with open("fakeDb.json", "r+") as f:
        data = json.load(f)
        if key not in data:
            data[key] = {"names":[], "value":[]}
            print("Added")
            f.seek(0)
            json.dump(data, f)
            f.truncate()
            return {}
        return data.get(key)

#def add_data_to_file(key, value):
    # Load the existing data from the file
    #with open("fakeDb.json", "r+") as f:
        #data = json.load(f)

def update_json_file(key, value):
    # Load the JSON data from the file
    with open("fakeDb.json", "r+") as f:
        data = json.load(f)

    # Update the value for the specified key
    data[key] = value

    # Write the updated data back to the file
    with open("fakeDb.json", "r+") as f:
        json.dump(data, f)
        f.truncate()

telePass = read_json_file("key")
bot = telebot.TeleBot(telePass)

@bot.message_handler(commands=['start'])
def readme(message):
    bot.send_message(message.chat.id, "Hello and welcome to the Unofficial SplitWise Bot!! The Bot aims to allow Telegram users to split money among themselves on outings and trips. The main commands are written and described here: \n\n/start or /help bring this message up. \n\nTo begin a new trip, use /newtrip to start one, and REPLY to the bot at all times. \n\nIf you are declaring that you owe money, use /sum. If you are charging others, use /split. \n\nAt the end of the trip, you can view a simplified (or not) receipt using /receipt, and remember to end with /endtrip!")

# Handle '/newtrip'
@bot.message_handler(commands=['newtrip'])
def newtrip(message):
    chatid = message.chat.id
    read_json_file(chatid)
    bot.send_message(message.chat.id, f"Welcome to a new trip, to join this new trip on {str(datetime.now(pytz.timezone('Asia/Singapore')))}, reply to this message with 'LEGGO!'.")

@bot.message_handler(regexp='LEGGO!')
def handle_message(message):
    if message.reply_to_message:
        # Get the username of the person being replied to
        username = message.from_user.username
        bot.send_message(message.chat.id, f"@{username} has joined the trip.")
    else:
        bot.send_message(message.chat.id, "Please reply to the message")
    chatid = message.chat.id
    dictchat = read_json_file(chatid)
    namez = dictchat.get("names")
    namez.append(username)
    dictchat["names"] = namez
    update_json_file(chatid, dictchat)

def gen_markup(PL):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 1
    for i in PL:
        markup.add(str(i))
    return markup

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def listsimplify(lst, num):
    for i in range(num):
        for j in range(num):
            if lst[i*num+j] > lst[j*num+i]:
                lst[i*num+j] = lst[i*num+j] - lst[j*num+i]
                lst[j*num+i] = 0
            elif lst[j*num+i] > lst[i*num+j]:
                lst[j*num+i] = lst[j*num+i] - lst[i*num+j]
                lst[i*num+j] = 0
            else:
                pass
    return lst

@bot.message_handler(commands=['sum'])
def inputmeal(message):
    chatid = str(message.chat.id)
    dictchat = read_json_file(chatid)
    usernames = dictchat.get("names")
    if dictchat.get("value") == []:
        dictchat["value"] = [0 for i in range(len(usernames)**2)]
        update_json_file(chatid, dictchat)
    msg = bot.send_message(message.chat.id, "How much did you spend?")
    bot.register_next_step_handler(msg, taxselect)

def taxselect(message):
    if isfloat(message.text) == False:
        mesg = bot.reply_to(message, 'This should be a decimal. How much did u spend?')
        bot.register_next_step_handler(mesg, taxselect)
    else:
        transaction.value = message.text
        msg = bot.send_message(message.chat.id, "How much is GST + Service Charge? eg. 1.188")
        bot.register_next_step_handler(msg, sum)

def sum(message):
    chatid = str(message.chat.id)
    dictchat = read_json_file(chatid)
    usernames = dictchat.get("names")
    usernames.remove(str(message.from_user.username))
    if isfloat(message.text) == False:
        msg = bot.reply_to(message, 'This should be a decimal bro. What is the tax?')
        bot.register_next_step_handler(msg, sum)
    else:
        transaction.gstservice = message.text
        transaction.value = float(transaction.value)*float(transaction.gstservice)
        msg = bot.send_message(message.chat.id, f"Your total owed is: {transaction.value}. Who will be tanking the payment?", reply_markup=gen_markup(usernames))
        bot.register_next_step_handler(msg, confirm)

def confirm(message):
    targetuser = message.text
    chatid = str(message.chat.id)
    dictchat = read_json_file(chatid)
    usernames = dictchat.get("names")
    selfindex = usernames.index(str(message.from_user.username))
    targetindex = usernames.index(targetuser)
    values = dictchat.get("value")
    print(selfindex, targetindex)
    values[selfindex+(targetindex*len(usernames))] += float(transaction.value)
    dictchat["value"] = values
    update_json_file(chatid, dictchat)
    bot.send_message(message.chat.id, f"@{str(message.from_user.username)} now owes @{targetuser} {transaction.value}")

@bot.message_handler(commands=['split'])
def inputvalue(message):
    chatid = str(message.chat.id)
    dictchat = read_json_file(chatid)
    usernames = dictchat.get("names")
    if dictchat.get("value") == []:
        dictchat["value"] = [0 for i in range(len(usernames)**2)]
        update_json_file(chatid, dictchat)
    msg = bot.send_message(message.chat.id, "How much did you spend?")
    bot.register_next_step_handler(msg, split)

def split(message):
    chatid = str(message.chat.id)
    dictchat = read_json_file(chatid)
    usernames = dictchat.get("names")
    transaction.value = message.text
    if not isfloat(message.text):
        msg = bot.reply_to(message, 'This should be a decimal bro. How much did u spend?')
        bot.register_next_step_handler(msg, split)
    else:
        msg = bot.send_message(message.chat.id, "How many are you splitting with?", reply_markup=gen_markup(range(1,len(usernames)+1)))
        bot.register_next_step_handler(msg, selectperson)

def selectperson(message):
    chatid = str(message.chat.id)
    dictchat = read_json_file(chatid)
    usernames = dictchat.get("names")
    usernames.remove(str(message.from_user.username))
    num = int(message.text)
    transaction.pax = num
    msg = bot.send_message(message.chat.id, "Who are you splitting with?", reply_markup=gen_markup(list(combinations(usernames,num-1))))
    bot.register_next_step_handler(msg, confirmation)

def confirmation(message):
    textfrommsg = message.text[2:-2].replace("'", "")
    textfrommsg = textfrommsg.replace(" ", "")
    sharedppl = list(textfrommsg.split(","))
    transaction.personlist = sharedppl.copy()
    #print(sharedppl)
    str1 = f"@{str(message.from_user.username)} is about to charge "
    for i in range(len(sharedppl)):
        #print(sharedppl[i])
        if i == len(sharedppl)-1:
            str1 += str(str(sharedppl[i]) + " " + str(float(transaction.value)/transaction.pax) + ".")
        else:
            str1 += str(str(sharedppl[i]) + " " + str(float(transaction.value)/transaction.pax) + " and ")
    msg = bot.send_message(message.chat.id, str1, reply_markup=gen_markup(["Cancel", "Okay"]))
    bot.register_next_step_handler(msg, updater)

def updater(message):
    if message.text == "Okay":
        chatid = str(message.chat.id)
        dictchat = read_json_file(chatid)
        usernames = dictchat.get("names")
        selfindex = usernames.index(str(message.from_user.username))
        for i in transaction.personlist:
            index = usernames.index(i)
            print(index,selfindex)
            values = dictchat.get("value")
            values[index+(selfindex*len(usernames))] += float(transaction.value)/transaction.pax
            dictchat["value"] = values
            update_json_file(chatid, dictchat)
    else:
        msg = bot.reply_to(message, 'Semula')
        bot.register_next_step_handler(msg, inputvalue)

@bot.message_handler(commands=['receipt'])
def receipt(message):
    chatid = str(message.chat.id)
    dictchat = read_json_file(chatid)
    usernames = dictchat.get("names")
    values = dictchat.get("value")
    str1 = ""
    for i in range(len(usernames)):
        str2 = f"To @{usernames[i]}: \n"
        for j in range(1,len(usernames)):
            str2 += f"@{usernames[(i+j)%len(usernames)]}: {values[(i*len(usernames))+((i+j)%len(usernames))]} \n"
        str1 += str2 + "\n"
    msg = bot.send_message(message.chat.id, str1 + "\n Simplify?", reply_markup=gen_markup(["Yes", "No"]))
    bot.register_next_step_handler(msg, simplifyreceipt)

def simplifyreceipt(message):
    if message.text == "Yes":
        chatid = str(message.chat.id)
        dictchat = read_json_file(chatid)
        usernames = dictchat.get("names")
        values = dictchat.get("value")
        newlst = listsimplify(values, len(usernames))
        str1 = ""
        for i in range(len(usernames)):
            str2 = f"To @{usernames[i]}: \n"
            for j in range(1,len(usernames)):
                str2 += f"@{usernames[(i+j)%len(usernames)]}: {newlst[(i*len(usernames))+((i+j)%len(usernames))]} \n"
            str1 += str2 + "\n"
        bot.send_message(message.chat.id, str1)

@bot.message_handler(commands=['endtrip'])
def endtrip(message):
    msg = bot.send_message(message.chat.id, "Time to go home????", reply_markup=gen_markup(["Yes", "No"]))
    bot.register_next_step_handler(msg, clearance)

def clearance(message):
    if message.text == "Yes":
        chatid = str(message.chat.id)
        update_json_file(chatid, {"names":[],"value":[]})
        bot.send_message(message.chat.id, "Memory Cleared, have a safe trip home.")
    else:
        pass

bot.polling()
