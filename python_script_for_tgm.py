from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import Channel, Chat
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, AddChatUserRequest
import sys
import csv
import traceback
import time
import random

api_id = 739525
api_hash = 'd8270b37a44256287bb1d93b7c557d8b'
phoneNo = '+919915130944'
client = TelegramClient(phoneNo, api_id, api_hash)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phoneNo)
    client.sign_in(phoneNo, input('Nhập mã: '))
    print("Đăng nhập thành công")

chats = []
last_date = None
chunk_size = 20000
groups = []

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)


for chat in chats:
    try:
        # if chat.megagroup == True:
        groups.append(chat)
        print(chat)
    except:
        continue


# https://python.gotrained.com/scraping-telegram-group-members-python-telethon/#Create_a_Telegram_App_and_Get_Your_Credentials
# https://python.gotrained.com/adding-telegram-members-to-your-groups-telethon-python/


print('Chọn một nhóm để loại bỏ các thành viên:')
i = 0
for g in groups:
    print(str(i) + '- ' + g.title)
    i += 1

g_index = input("Nhập số nhóm")
target_group = groups[int(g_index)]

print("Tìm nạp thành viên: ")

all_participants = []
all_participants = client.get_participants(target_group, aggressive=True)


for all_participant in all_participants:
    print(all_participant)

input_file = "./members.csv"

print('Đang lưu trong tệp ...')
with open(input_file, "w", encoding='UTF-8') as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(['username', 'user id', 'access_hash', 'name', 'group', 'group id'])
    for user in all_participants:
        if user.username:
            username = user.username
        else:
            username = ""
        if user.first_name:
            first_name = user.first_name
        else:
            first_name = ""
        if user.last_name:
            last_name = user.last_name
        else:
            last_name = ""
        name = (first_name + ' ' + last_name).strip()
        writer.writerow([username, user.id, user.access_hash, name, target_group.title, target_group.id])
print('Thành viên đã được cạo thành công.')
f.close()

########################################################################################################################

users = []
with open(input_file, encoding='UTF-8') as f:
    rows = csv.reader(f, delimiter=",", lineterminator="\n")
    next(rows, None)
    for row in rows:
        user = {}
        user['username'] = row[0]
        user['id'] = int(row[1])
        user['access_hash'] = int(row[2])
        user['name'] = row[3]
        users.append(user)

chats = []
last_date = None
chunk_size = 20000
toGroups = []

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)

for chat in chats:
    try:
        # if chat.megagroup == True:
        toGroups.append(chat)
        print(chat)
    except:
        continue

print('Chọn một nhóm để thêm thành viên:')
i = 0
for group in toGroups:
    print(str(i) + '- ' + group.title)
    i += 1

g_index = input("Nhập một số: ")
target_group = toGroups[int(g_index)]
print("*****Mục tiêu: ", target_group)

if type(target_group) == Channel:
    target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

mode = int(input("Nhập 1 để thêm theo tên người dùng hoặc 2 để thêm theo ID: "))
n = 0
for user in users:
    n += 1
    if n % 50 == 0:
        time.sleep(900)
    try:
        print("Thêm {}".format(user['id']))
        if mode == 1:
            print("UserName: ", user['username'])
            if user['username'] == "":
                continue
            user_to_add = client.get_input_entity(user['username'])

        elif mode == 2:
            user_to_add = InputPeerUser(user['id'], user['access_hash'])
            print("USerId, USerHash", user['id'], user['access_hash'])

        else:
            sys.exit("Đã chọn chế độ không hợp lệ. Vui lòng thử lại.")

        if type(target_group) == Channel:
            client(InviteToChannelRequest(target_group_entity, [user_to_add]))
            print("kênh của nó")

        elif type(target_group) == Chat:
            client(AddChatUserRequest(target_group, user_to_add, fwd_limit=50))
            print("cuộc trò chuyện của nó")

        else:
            print("Có cái gì đó không đúng!!!")

        print("Chờ 10-30 giây...")
        time.sleep(random.randrange(10, 30))
    except PeerFloodError:
        print("Nhận lỗi lũ lụt từ điện tín. Tập lệnh hiện đang dừng. Vui lòng thử lại sau một thời gian.")
    except UserPrivacyRestrictedError:
        print("Cài đặt quyền riêng tư của người dùng không cho phép bạn làm điều này. Bỏ qua.")
    except:
        traceback.print_exc()
        print("Lỗi không mong đợi")
        continue

print('Thành viên đã thêm:')
