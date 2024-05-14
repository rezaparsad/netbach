import asyncio
import os
import sys

import django
import jdatetime
from pyrogram import Client, idle
from pyrogram.enums.chat_type import ChatType

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from config.settings import redis
from account.models import Ticket, User
from cloud.models import ServerRent
from django.contrib.humanize.templatetags import humanize


red, green, yellow, purple, default = '\033[31m', '\033[32m', '\033[33m', '\033[35m', '\033[0m'
app = Client(
    "netbach",
    api_id=1296817,
    api_hash='bfcc80f70227102061e5f20edfa11185',
    bot_token='6760615561:AAEdN2HxB9-cKZvo8rbpbK6vnEek3L-KkYE',
    lang_code='en'
)
admins = [1799980896]


async def private_message(message):
    chat_id = message.chat.id
    text = message.text

    if text == "/start":
        await message.reply("Welcome to NetBach bot !")

    elif text == "/traffic":
        await message.reply("Getting data from datacenters ... !")
        servers = ServerRent.objects.filter(is_active=True)
        statistics = ""
        counter = 1
        for server in servers:
            response = server.get_datacenter().server_traffic(server)
            statistics += str(counter) + " - " + server.ipv4 + " : "
            if response["status"] is True:
                statistics += (humanize.intcomma(response["outgoing_traffic"] // 1000000000) + " / "
                               + humanize.intcomma(int(server.server.traffic) // 1000))
            else:
                statistics += "Error"

            statistics += "\n"
            counter += 1
        counter = 0
        text = ''
        for stat in statistics.split('\n'):
            text += stat + '\n'
            if counter >= 50:
                await app.send_message(
                    message.chat.id,
                    text,
                    reply_to_message_id=message.id
                )
                text = ''
                counter = 0
            counter += 1
        await message.reply("Done ✅")

    elif text == "/servers":
        servers = ServerRent.objects.filter(is_active=True)
        statistics = ""
        counter = 1
        for server in servers:
            statistics += str(counter) + " - " + server.ipv4 + " : "
            statistics += humanize.intcomma(server.cost) + " - "
            statistics += jdatetime.datetime.fromgregorian(datetime=server.created).strftime('%Y/%m/%d | %H:%M:%S')
            statistics += "\n"
            counter += 1
        counter = 0
        text = ''
        for stat in statistics.split('\n'):
            text += stat + '\n'
            if counter >= 50:
                await app.send_message(
                    message.chat.id,
                    text,
                    reply_to_message_id=message.id
                )
                text = ''
                counter = 0
            counter += 1
        await message.reply("Done ✅")

    elif message.reply_to_message and message.reply_to_message.text:
        ticket_pk = int(message.reply_to_message.text.split("\n")[0].split(" ")[-1])
        ticket = Ticket.objects.get(pk=ticket_pk)
        admin_user = User.objects.get(username="netbach")
        Ticket.objects.create(user=admin_user, pack=ticket.pack, content=text)
        ticket.pack.status = "answer_given"
        ticket.pack.save()
        await message.reply("Done ✅")


@app.on_message()
async def handler(_, message):
    if message.chat.id in admins and message.chat.type == ChatType.PRIVATE:
        await private_message(message)


async def check_for_new_ticket():
    while True:
        try:
            tickets = redis.smembers("TicketList")
            for ticket_pk in tickets:
                redis.srem("TicketList", ticket_pk)
                try:
                    ticket = Ticket.objects.get(pk=int(ticket_pk))
                    pack = ticket.pack
                    text = (
                        f"New Ticket {ticket.pk}" + "\n\n" +
                        f"User : {ticket.user}" + "\n" +
                        f"Category : {pack.category}" + "\n\n" +
                        f"Title : 👇\n\n{pack.title}" + "\n\n" +
                        f"Content : 👇\n\n{ticket.content}"
                    )
                except Exception as e:
                    print(e)
                    continue

                for admin in admins:
                    await app.send_message(admin, text)
                    await asyncio.sleep(5)
        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(30)


async def main():
    await app.start()
    info = await app.get_me()
    print("\n")
    print(green + f'>>> Bot NetBach is online !')
    print(red + '   >>> ' + yellow + f'First Name : {info.first_name}')
    print(red + '   >>> ' + yellow + f'User Id : {info.id}')
    print(red + '   >>> ' + yellow + f'UserName : {info.username}')
    print(green + '>>> Written By Reza Parsa !' + default)
    asyncio.get_event_loop().create_task(check_for_new_ticket())


if __name__ == '__main__':
    asyncio.get_event_loop().create_task(main())
    idle()

