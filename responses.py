import model
import tokens
import requests
import json
import time
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def handle_response(message) -> str:
    p_message = message.lower()

    p_message_split = p_message.split('/')

    command = p_message_split[0]

    # Help message used to get people familiar with the bot
    if command == 'help':
        return "**Register your account with the bot**\nUse !register followed by your **name** (Timi), your **steamid** (76561198157520925) or **epicid** (VerbalShrimp46), and the platform you are using (**steam**/**epic**) with commas between all sections\nUpdate your registration with **!update**\nRank check players already registered with **!rank** followed by the players **name**\nSee who is currently registered with the bot with **!players**, feel free to include a range of players by formatting your request with **!player 1 10** (the bot will default to 1-10)\nYou can also do a one-time lookup with the **!steam** and **!epic** commands followed by the **steamid** or **epicid**"

    # Where the player will register to go into the database for easy lookup
    if command == 'register':
        if len(p_message_split) != 4:
            return "Please register using the format: **!register Timi 76561198157520925 steam**"

        else:
            username = p_message_split[1]
            id = p_message_split[2]
            platform = p_message_split[3]

            app = Flask(__name__)
            with app.app_context():
                # Connect to Database
                connection = model.get_db()

                # First check to make sure that the user is not already registered
                # If already registered do nothing and return saying that if they would like to update registration go to !update

                # Insert the register player into database
                connection.execute(
                    "INSERT INTO users(username, id, platform) "
                    "VALUES ( ? , ? , ? ) ",
                    (username, id, platform)
                )

                model.close_db(1)
            return f"Successfully registered {username}\n{platform}id is {id}"

    # Used to update a players registration
    if command == 'update':
        if len(p_message_split) != 5:
            return "Please update registration using the format: **!update Timi *new_name* 76561198157520925 steam**"

        else:
            username = p_message_split[1]
            new_username = p_message_split[2]
            id = p_message_split[3]
            platform = p_message_split[4]

            app = Flask(__name__)
            with app.app_context():
                # Connect to Database
                connection = model.get_db()

                # Update the registration to match the new registration
                connection.execute(
                    "UPDATE users "
                    "SET username = ?, id = ?, platform = ? "
                    "WHERE username = ? ",
                    (new_username, id, platform, username)
                )

                model.close_db(1)
            return f"Successfully updated {username}\n{platform}id is {id}"

    # Used to search a player by name from the database
    if command == 'rank':
        if len(p_message_split) != 2:
            return "Please use the rank command with the format: **!rank Timi**"

        else: 
            username = p_message_split[1]

            app = Flask(__name__)
            with app.app_context():
                # Connect to Database
                connection = model.get_db()

                # Grab the id and platform of the user
                cur = connection.execute(
                    "SELECT id, platform "
                    "FROM users "
                    "WHERE username = ? ",
                    (username, )
                )

                user = cur.fetchone()

                if not user:
                    return "This user is not registered with the bot\nPlease check your spelling, or use the !players command to find everyone already registered with the bot"

                id = user['id']
                id.replace(' ', '%20')
                platform = user['platform']

                model.close_db(1)

                ranks = get_ranks(id, platform)

                if len(ranks) == 2:
                    return f'{ranks[0]}\n{ranks[1]}'
                else:
                    return f'**--{ranks[9]}\'s Ranks--**\n\nRanked 1v1:\n\tCurrent MMR: {ranks[0]}\n\tPeak MMR: {ranks[1]}\n\tGames Played: {ranks[2]}\nRanked 2v2:\n\tCurrent MMR: {ranks[3]}\n\tPeak MMR: {ranks[4]}\n\tGames Played: {ranks[5]}\nRanked 3v3:\n\tCurrent MMR: {ranks[6]}\n\tPeak MMR: {ranks[7]}\n\tGames Played: {ranks[8]}'

    # Used to output the players that are already registered with the bot
    if command == 'players':
        if len(p_message_split) == 3:
            x = int(p_message_split[1]) - 1
            y = int(p_message_split[2]) - 1

            if y - x > 10 or y - x < 0 or (y < 0 or x < 0):
                return "Please keep the selected players within increments of 10\nFor example, 1-10, 11-20, ect..."

        elif len(p_message_split) == 1:
            x = 0
            y = 9
        else:
            return "Please format the !players command as either **!players** or **!players x y**"

        app = Flask(__name__)
        with app.app_context():
            # Connect to Database
            connection = model.get_db()

            # Grab all player usernames from the database
            cur = connection.execute(
                "SELECT * "
                "FROM users "
            )

            users = cur.fetchall()

            model.close_db(1)

            if not users:
                return "There are currently no players registered with the bot"

            users = users[x:y+1]
            if len(users) != (y - x + 1):
                y = x + len(users) - 1

            output = f'**Players {x+1}-{y+1}**\n'

            if not users:
                return "There are not enough players registered with the bot"

            for user in users: 
                username = user['username']
                id = user['id']
                platform = user['platform']
                output += f'{username} {id} {platform}\n'

            return output

    # Single search for players with steamid
    if command == 'steam':
        if len(p_message_split) != 2:
            return 'Please format like below\n!steam "steam_id'

        steam_id = p_message_split[1]

        ranks = get_ranks(steam_id, 'steam')

        if len(ranks) == 2:
            return f'{ranks[0]}\n{ranks[1]}'
        else:
            return f'**--{ranks[9]}\'s Ranks--**\n\nRanked 1v1:\n\tCurrent MMR: {ranks[0]}\n\tPeak MMR: {ranks[1]}\n\tGames Played: {ranks[2]}\nRanked 2v2:\n\tCurrent MMR: {ranks[3]}\n\tPeak MMR: {ranks[4]}\n\tGames Played: {ranks[5]}\nRanked 3v3:\n\tCurrent MMR: {ranks[6]}\n\tPeak MMR: {ranks[7]}\n\tGames Played: {ranks[8]}'

    # Single search for players with epicid 
    if command == 'epic':
        if len(p_message_split) != 2:
            return 'Please format like below\n!epic "epic_id'

        epic_id = p_message_split[1]

        ranks = get_ranks(epic_id, 'epic')
        
        if len(ranks) == 2:
            return f'{ranks[0]}\n{ranks[1]}'
        else:
            return f'**--{ranks[9]}\'s Ranks--**\n\nRanked 1v1:\n\tCurrent MMR: {ranks[0]}\n\tPeak MMR: {ranks[1]}\n\tGames Played: {ranks[2]}\nRanked 2v2:\n\tCurrent MMR: {ranks[3]}\n\tPeak MMR: {ranks[4]}\n\tGames Played: {ranks[5]}\nRanked 3v3:\n\tCurrent MMR: {ranks[6]}\n\tPeak MMR: {ranks[7]}\n\tGames Played: {ranks[8]}'

    # RLCS Fan Vote, with mmr values for 2v2 and 3v3 games figure out a % chance of winning for both teams to win. Based on current and peak mmr, matches played, and current streak

    # Spaces in epicid doesn't work

    # If they haven't played a playlist, the ranks will not show up, have to write logic with alternative methods of displaying ranks

# This logic doesn't work if they have not played certain gamemodes. Will need to update the logic to work with what gamemodes are shown and available

# Search for for 1v1 2v2 3v3 gamemodes seperately using the .index(string) function and index into the ranks array with the index provided. If there is no match, return as all zeros
def get_ranks(username, platform):
    options = Options()
    options.add_argument('--headless=new')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    if platform == 'steam':
        driver.get(f'https://rocketleague.tracker.network/rocket-league/profile/steam/{username}/overview')
    elif platform == 'epic':
        driver.get(f'https://rocketleague.tracker.network/rocket-league/profile/epic/{username}/overview')
    else:
        return ['Error']


    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'value')))
    except:
        driver.close()
        driver.quit()
        return ['Player Not Found', 'Please Make Sure the Data in the System is Correct Before Searching Again']

    # Sorted by 1v1 mmr, peak 1v1 mmr, 1v1 games played (followed by 2v2 and 3v3 same format)
    elements = driver.find_elements(By.CLASS_NAME, 'value')
    mmr_values = [element.text for element in elements]

    # Get the playlists
    elements = driver.find_elements(By.CLASS_NAME, 'playlist')
    playlist = elements[0].text

    # Get the username
    element = driver.find_element(By.CLASS_NAME, 'trn-ign__username')
    username = element.text

    driver.close()
    driver.quit()

    if playlist =='Ranked Duel 1v1':
        mmr_values = mmr_values[9:18]
    else:
        mmr_values = mmr_values[12:21]

    mmr_values.append(username)

    return mmr_values
