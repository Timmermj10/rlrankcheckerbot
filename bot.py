import discord
from discord.ext import tasks
import responses
import os
import tokens
import time
import asyncio

# Global variable for when PAUSE is enabled
PAUSE = False
# Global variable for when do start the pause process
cooldown_start_time = "06"

async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def run_discord_bot():
    TOKEN = tokens.discord_token
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running')

        # Start the daily cooldown task
        daily_cooldown.start()

    @client.event
    async def on_message(message):
        global PAUSE
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        # Prevents infinite loop of bot responding to itself, also prevents the bot from responding outside of general
        if username == str(client.user) or channel != 'general': # CHANGE THIS LINE IF YOU WANT TO DUBUG IN PERSONAL SERVER ONLY channel == 'general'
            return 

        print(f'{username} said: "{user_message}" in {channel}')

        # Prevents infinite loop of bot responding to itself, also prevents the bot from responding outside of general
        if username == client.user or channel != 'general': # CHANGE THIS LINE IF YOU WANT TO DUBUG IN PERSONAL SERVER ONLY channel == 'general'
            return 

        # The main check of if the user is trying to use the bot for something
        if user_message[0] == '!' and not PAUSE and channel == 'general':
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=False)
            return

        # Special check incase the bot is currently updating daily mmrs, so the database doesn't do a double upload and mess up the data
        if PAUSE and channel == 'general' and user_message[0] == '!':
            await message.channel.send('Currently updating daily MMR, please wait for 15 minutes')
            return

        # Special Don Request handling, if a user says hi to the bot, the bot will say hi back :)
        if 'hi timibot' in user_message and channel == 'general': # username == 'africanooo#0'
            username = username[:username.index('#')]
            await message.channel.send(f'Hi Mr. {username.capitalize()} <:happycat:1017291567519780894>')
            return

    @client.event
    async def startcooldown(duration: int):
        channel = client.get_channel(1115029693289201687) #851942788936630292
        await channel.send('Daily update starting. This process will take 15 minutes to complete')
        await asyncio.sleep(duration)
        await channel.send('Daily update has completed. Feel free to use the commands')

    @tasks.loop(hours=1)
    async def daily_cooldown():
        global cooldown_start_time
        global PAUSE
        now = time.strftime("%H")

        if now == cooldown_start_time:
            print('Sleeping!')
            PAUSE = True
            await startcooldown(900)
            PAUSE = False
            print('Awoken')
    client.run(TOKEN)