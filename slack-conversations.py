import requests
import sys
import datetime
from datetime import date
from decimal import Decimal

SLACK_API_TOKEN = "" # get one from https://api.slack.com/docs/oauth-test-tokens
CHANNEL_NAME = sys.argv[1]
CHANNEL_NOT_FOUND = 'Channel Not Found'
SLACK_API_URL_CHANNEL_LIST = 'https://slack.com/api/channels.list?token=%s'
SLACK_API_URL_CONVO_HISTORY = 'https://slack.com/api/conversations.history?token=%s&channel=%s'
SLACK_API_URL_CONVO_REPLIES = 'https://slack.com/api/conversations.replies?token=%s&channel=%s&ts=%s'
SLACK_API_URL_ALL_USERS_LIST = 'https://slack.com/api/users.list?token=%s'
SLACK_API_URL_MEMBER_CONVO_LIST = 'https://slack.com/api/conversations.members?token=%s&channel=%s'
MESSAGES = 'messages'
CHANNELS = 'channels'
THREAD_TS = "thread_ts"
REPLY_USERS = "reply_users"
MEMBERS = 'members'
ERROR = 'error'
ERROR_MSG = 'Error Retrieving Channels: %s'
ID = 'id'
BOT_ID = "bot_id"
HALLWAY_BOT_ID = ""
HALLWAY_USER_ID = ""
NAME = 'name'
TS = "ts"
TAB = "\t"
URL_ENCODE_DOT = "%2E"
TEXT = "text"
DOT = "."
SPACE = " "
JOINED_THE_CALL = " joined the call"
LONG_NAME_LENGTH = 14
SHORT_NAME_LENGTH = 6
found_users = []
found_user_names = []
found_users_count = []
total_hallway_convos = 0
most_participants = 0
least_participants = 10000000
most_participants_convo = ""
least_participants_convo = ""

channel_list_ret = requests.get(SLACK_API_URL_CHANNEL_LIST % SLACK_API_TOKEN).json()

def index(l, f):
     return next((i for i in range(len(l)) if f(l[i])), None)

def find_name(l, name, sub):
    ret = []
    t = None
    if sub != None:
        t = index(l, lambda item: item[sub] == name)
    else:
        t = index(l, lambda item: item == name)
    if (t == None):
        ret.append(None)
        ret.append(-1)
    else:
        ret.append(l[t])
        ret.append(t)

    return ret

if ERROR in channel_list_ret:
    print(ERROR_MSG % channel_list_ret[ERROR])
else:
    channel_list = channel_list_ret[CHANNELS]
    channel = CHANNEL_NOT_FOUND

    for c in channel_list:
        if NAME in c:
            if c[NAME] == CHANNEL_NAME:
                channel = c
                

    if (channel == CHANNEL_NOT_FOUND):
        print(channel)
    else:
        convo_history = requests.get(SLACK_API_URL_CONVO_HISTORY % (SLACK_API_TOKEN, channel[ID])).json()
        messages = convo_history[MESSAGES]
        for message in messages:
            if BOT_ID in message:
                bot_reply = 0
                if (message[BOT_ID] == HALLWAY_BOT_ID):
                    if REPLY_USERS in message:
                        reply_users = message[REPLY_USERS]
                        for idx,val in enumerate(reply_users):                            
                            if val == HALLWAY_USER_ID:
                                total_hallway_convos = total_hallway_convos + 1
                                ts = str(message[TS])
                                ts = ts.replace(DOT, URL_ENCODE_DOT)
                                url = SLACK_API_URL_CONVO_REPLIES % (SLACK_API_TOKEN, channel[ID], ts)
                                convo_replies = requests.get(url).json()
                                rmessages = convo_replies[MESSAGES]     
                                for reply in rmessages:
                                    if BOT_ID in reply:                                        
                                        if reply[BOT_ID] == HALLWAY_BOT_ID and JOINED_THE_CALL in reply[TEXT]:
                                            bot_reply = bot_reply + 1                                            
                                            uid = reply[TEXT].replace(JOINED_THE_CALL, "").replace("<@","").replace(">","")
                                            if len(found_users) > 0:
                                                element = find_name(found_users,uid, None)
                                                if (element[0] == None):
                                                    found_users.append(uid)
                                                    found_users_count.append(1)
                                                else:
                                                    found_users_count[element[1]] = found_users_count[element[1]] + 1
                                            else:
                                                found_users.append(uid)
                                                found_users_count.append(1)

                            if bot_reply > most_participants:
                                most_participants = bot_reply
                                most_participants_convo = datetime.datetime.fromtimestamp(Decimal(message[TS]))

                            if bot_reply <= least_participants:
                                least_participants = bot_reply
                                least_participants_convo = datetime.datetime.fromtimestamp(Decimal(message[TS]))

    member_info = requests.get(SLACK_API_URL_MEMBER_CONVO_LIST % (SLACK_API_TOKEN, channel[ID])).json()
    if MEMBERS in member_info:
        members = member_info[MEMBERS]
        user_info_list = requests.get(SLACK_API_URL_ALL_USERS_LIST % SLACK_API_TOKEN).json()
        if MEMBERS in user_info_list:
            users_list = user_info_list[MEMBERS]
            users = list(filter(lambda u: u[ID] in members, users_list))
            for user in found_users:
                    ui = find_name(users, user, ID)
                    if ui[0] != None:
                        found_user_names.append(ui[0].get(NAME))

    for idx,val in enumerate(found_users):
        if len(found_user_names) > idx and len(found_users_count) > idx:
            tt = TAB
            if (len(found_user_names[idx]) < LONG_NAME_LENGTH):
                tt = tt + TAB
                if len(found_user_names[idx]) < SHORT_NAME_LENGTH:
                    tt = tt + TAB
            print(found_users[idx] + SPACE + found_user_names[idx] + tt + str(found_users_count[idx]))

    print()
    print("Total Hallway Participants:\t\t" + str(len(found_user_names)))
    print("Total Hallway Conversations:\t\t" + str(total_hallway_convos))
    print("Most participants in Conversation:\t" + str(most_participants))
    print("Most participated in Conversation:\t" + str(most_participants_convo))
    print("Least participants in Conversation:\t" + str(least_participants))
    print("Least participated in Conversation:\t" + str(least_participants_convo))
                        



