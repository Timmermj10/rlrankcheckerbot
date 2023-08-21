import model
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver

def handle_response(message) -> str:
    p_message = message.lower()

    p_message_split = p_message.split('/')

    command = p_message_split[0]

    # Help message used to get people familiar with the bot
    if command == 'help':
        return "***Separate all portions of the command with '/'***\n\n**--Register your account with the bot--**\n\t***!register*** followed by your **name** (Timi), **steamid64** (76561198157520925) or **epicid** (VerbalShrimp46), and the platform (**steam**/**epic**)\n\n\t***!!! EXAMPLE OF REGISTRATION: !register/Timi/76561198157520925/steam !!!***\n\n**--Update your registration--**\n\t***!update*** followed by **current name** (Timi), **new name** (TimiBoy), **steamid64** (76561198157520925) or **epicid** (VerbalShrimp46), and platform (**steam**/**epic**)\n\n\t***!!! EXAMPLE OF UPDATING: !update/Timi/TimiBoy/76561198157520925/steam !!!***\n\n**--Rank check players already registered with the bot--**\n\t***!rank*** followed by the players **name** (Timi)\n\n\t***!!! EXAMPLE OF RANK CHECKING: !rank/Timi !!!***\n\n**--See who is currently registered with the bot--**\n\t**!players**, feel free to include a range of players by formatting your request with **!players/1/10** (the bot will default to 1-10)\n\n\t***!!! EXAMPLE OF CHECKING REGISTRATION: !players/11/20 !!!***\n\n**--One-time rank-check--**\n\t**!steam** and **!epic** commands followed by the **steamid** or **epicid**\n\n\t***!!! EXAMPLE OF ONE TIME RANK-CHECK: !epic/VerbalShrimp46 !!!***\n\n**--Find steamid64--**\n\tIf you need help finding your steamid64 you can use command **!id** followed by your custom portion of your steam url!\n\n\t***!!! EXAMPLE OF GETTING STEAMID64: !id/rltimi !!!***\n\n**Remember to always include slashes between sections of the command!**\n\n*--Comming soon: history command--*\n\t**Track how your friends are doing over the past week in their games!**"

    # Where the player will register to go into the database for easy lookup
    if command == 'register':
        if len(p_message_split) != 4:
            return "Please register using the format: **!register/Timi/76561198157520925/steam**"

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
                cur = connection.execute(
                    "SELECT * "
                    "FROM users "
                    "WHERE username = ? OR id = ?  ",
                    (username, id)
                )

                user = cur.fetchone()

                if user: 
                    model.close_db(1)
                    return "There is already a user registered with this name or id\nUse update to update the registration or check !players to see everyone that is already registered!"

                # Insert the register player into database
                connection.execute(
                    "INSERT INTO users(username, id, platform) "
                    "VALUES ( ? , ? , ? ) ",
                    (username, id, platform)
                )

                model.close_db(1)
            return f"Successfully registered {username}\n{platform}id is {id}"

    # Used to update a players registration
    # CHECK IF WE CAN JUST HAVE THEM UPDATE NAME AND OR NAME AND PLATFORM
    if command == 'update':
        if len(p_message_split) != 5:
            return "Please update registration using the format: **!update/Timi/*new_name*/76561198157520925/steam**"

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
            return "Please use the rank command with the format: **!rank/Timi**"

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
                    return f'**--{ranks[12]}\'s Ranks--**\n\nRanked 1v1:\n\tCurrent MMR: {ranks[0]}\n\tSeason Peak MMR: {ranks[1]}\n\tGames Played: {ranks[2]}\n\tStreak: {ranks[3]}\nRanked 2v2:\n\tCurrent MMR: {ranks[4]}\n\tSeason Peak MMR: {ranks[5]}\n\tGames Played: {ranks[6]}\n\tStreak: {ranks[7]}\nRanked 3v3:\n\tCurrent MMR: {ranks[8]}\n\tSeason Peak MMR: {ranks[9]}\n\tGames Played: {ranks[10]}\n\tStreak: {ranks[11]}'

    # Used to output the players that are already registered with the bot

    # Update this to only take one input (1-z) and display that page of 10 players

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
            return "Please format the !players command as either **!players** or **!players/x/y**"

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
                output += f'{username} **+** {id} **+** {platform}\n'

            return output

    # Single search for players with steamid
    if command == 'steam':
        if len(p_message_split) != 2:
            return 'Please format like below\n!steam/"steam_id'

        steam_id = p_message_split[1]

        ranks = get_ranks(steam_id, 'steam')

        if len(ranks) == 2:
            return f'{ranks[0]}\n{ranks[1]}'
        else:
            return f'**--{ranks[12]}\'s Ranks--**\n\nRanked 1v1:\n\tCurrent MMR: {ranks[0]}\n\tSeason Peak MMR: {ranks[1]}\n\tGames Played: {ranks[2]}\n\tStreak: {ranks[3]}\nRanked 2v2:\n\tCurrent MMR: {ranks[4]}\n\tSeason Peak MMR: {ranks[5]}\n\tGames Played: {ranks[6]}\n\tStreak: {ranks[7]}\nRanked 3v3:\n\tCurrent MMR: {ranks[8]}\n\tSeason Peak MMR: {ranks[9]}\n\tGames Played: {ranks[10]}\n\tStreak: {ranks[11]}'

    # Single search for players with epicid 
    if command == 'epic':
        if len(p_message_split) != 2:
            return 'Please format like below\n!epic/"epic_id'

        epic_id = p_message_split[1]

        ranks = get_ranks(epic_id, 'epic')
        
        if len(ranks) == 2:
            return f'{ranks[0]}\n{ranks[1]}'
        else:
            return f'**--{ranks[12]}\'s Ranks--**\n\nRanked 1v1:\n\tCurrent MMR: {ranks[0]}\n\tSeason Peak MMR: {ranks[1]}\n\tGames Played: {ranks[2]}\n\tStreak: {ranks[3]}\nRanked 2v2:\n\tCurrent MMR: {ranks[4]}\n\tSeason Peak MMR: {ranks[5]}\n\tGames Played: {ranks[6]}\n\tStreak: {ranks[7]}\nRanked 3v3:\n\tCurrent MMR: {ranks[8]}\n\tSeason Peak MMR: {ranks[9]}\n\tGames Played: {ranks[10]}\n\tStreak: {ranks[11]}'

    # Delete command that can be used to delete people from the database (maybe make this function assessable to certain users)
    if command == 'delete':
        if len(p_message_split) != 2:
            return "Please delete registration using the format: **!delete/Timi**"
        else:
            username = p_message_split[1]

            app = Flask(__name__)
            with app.app_context():
                # Connect to Database
                connection = model.get_db()

                # Delete the user from the database
                connection.execute(
                    "DELETE "
                    "FROM users "
                    "WHERE username = ? ",
                    (username, )
                )

                model.close_db(1)

                return f'Successfully deleted registration for {username}'

    # History command that grabs the users mmrs over the past 7 days (if they have been registered with the bot over those 7 days)

    # This command will work by looking up all users in the database once per day (midnight USEAST STD) and putting those values into an alternate table with the value of the day (1-7 *update the inverval on a weekly basis) Then when someone searches for a player we will grab the mmr values stored in the database and output them formatted according to the values returned from the database lookup.
    if command == 'history':
        # Create logic to search through the tables and output weeks mmr values for the selected player
        return 'Work in progress'

    # Command that can be used to get the steamid64 if the user has a custom steamurl
    if command == 'id':
        if len(p_message_split) != 2:
            return "Please use the format: **!id/*custom_url_portion***"

        else:
            custom = p_message_split[1]

            # if custom[0:5] == 'http':
            #     split_url = custom.split('/')
            #     custom = split_url[4]

            id = get_steamid64(custom)

            return f'Your steamid64 is **{id}**'

def get_ranks(username, platform):
    options = Options()
    options.add_argument('--headless=new')

    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version="114.0.5845.96").install()), options=options) # 116.0.5799.0 114.0.5735.90
    # driver = webdriver.Chrome(service=ChromeService('/Users/jaketimmerman/Desktop/Personal/chromedriver-mac-x64/chromedriver.exe'), options=options)
    # driver = webdriver.Chrome(options=options)
    driver = Driver(uc=True, headless=True)

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
    playlists = [element.text for element in elements]

    # Get the streaks
    elements = driver.find_elements(By.CLASS_NAME, 'matches')
    streaks = [element.text for element in elements]

    # Get the username
    element = driver.find_element(By.CLASS_NAME, 'trn-ign__username')
    username = element.text

    # Get the column names
    elements = driver.find_elements(By.CLASS_NAME, 'trn-table__column--left')
    columns = [element.text for element in elements]

    # To classify if the user has a peak rating available for display
    peak_rat = 0
    if 'Peak Rating' in columns:
        peak_rat = 1

    driver.close()
    driver.quit()

    index = []

    try:
        ones = playlists.index('Ranked Duel 1v1')
        index.append(int(ones))
    except:
        index.append(-1)
    try:
        twos = playlists.index('Ranked Doubles 2v2')
        index.append(int(twos))
    except:
        index.append(-1)
    try:
        threes = playlists.index('Ranked Standard 3v3')
        index.append(int(threes))
    except:
        index.append(-1)

    output = []
    for pos in index:
        if pos == -1:
            output.extend(['N/A', 'N/A', 'N/A'])
        else:
            if peak_rat:
                location = -((len(playlists) - 1 - pos) * 3)
            else:
                location = -((len(playlists) - 1 - pos) * 2)
            if mmr_values[location - 2] == '' and peak_rat:
                mmr_values[location - 2] = mmr_values[location - 3]
            if location == 0:
                if peak_rat:
                    output.extend(mmr_values[location - 3:])
                else:
                    output.append(mmr_values[location - 2])
                    output.append('N/A')
                    output.append(mmr_values[location - 1])
            else:
                if peak_rat:
                    output.extend(mmr_values[location - 3: location])
                else:
                    output.append(mmr_values[location - 2])
                    output.append('N/A')
                    output.append(mmr_values[location - 1])

        # Streak Work
        streak = streaks[pos]
        streak = streak[streak.index('\n')+1:]
        if 'Loss' in streak:
            streak = streak[streak.index('.')+2:]
            streak += ' :crying_cat_face:'
            output.append(streak)
        if 'Win' in streak:
            streak = streak[streak.index('.')+2:]
            streak += ' <:happycat:1017291567519780894>'
            output.append(streak)


    output.append(username)

    return output

def get_steamid64(custom):
    options = Options()
    options.add_argument('--headless=new')

    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version="114.0.5735.90").install()), options=options)
    driver = Driver(uc=True, headless=False)

    driver.get(f'https://steamid.io/lookup/{custom}')

    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'key')))
    except:
        driver.close()
        driver.quit()
        return 'Steamid not found, Please make sure you are only entering the custom portion of the steamURL, not the whole URL'

    elements = driver.find_elements(By.CLASS_NAME, 'value.short')
    values = [element.text for element in elements]

    steamid = values[2]

    return steamid



'''
**Fixed Bugs and QOL Updates**

    Spaces in epicid doesn't work
        Fixed by using a / as the delimiter rather than spaces

    If they haven't played a playlist, the ranks will not show up, have to write logic with alternative methods of displaying ranks
        Fixed by writing logic to search the playlists array for the locations of the mmrs for each playlist

    Layout of text (especially !players) to make it more readable
'''

'''
**Future updates**

    Change the if chain to a SWITCH statement for improved speeds

    Allow players to search for specific gamemodes rather than just 1v1, 2v2, and 3v3

    Get a players progress over the week, outputs a players mmr over the week including a change in the mmr, maybe make a graph, who knows a lot can be done with this idea

    RLCS fan vote type system where player chooses players that would face off, and the system would return a % chance of who would win. Write the algorithm to use mmr, matches played, current win/loss streak, etc.

'''