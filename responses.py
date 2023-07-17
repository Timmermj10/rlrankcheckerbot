import model
import tokens
import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def handle_response(message) -> str:
    p_message = message.lower()

    p_message_split = p_message.split()

    if p_message_split[0] == 'help':
        return "register: how to register your account with the bot\nsteam: used to register steam account\nepic: used to register epic account"

    if p_message_split[0] == 'register':
        return "Please register using the commands 'steam' or 'epic'"
    
    if p_message_split[0] == 'steam':
        if len(p_message_split) != 2:
            return 'Please format like below\n!steam "steam_id'

        steam_id = p_message_split[1]

        ranks = get_ranks(steam_id, 'steam')

        if len(ranks) == 2:
            return f'{ranks[0]}\n{ranks[1]}'
        else:
            return f'**--{ranks[9]}\'s Ranks--**\n\nRanked 1v1:\n\tCurrent MMR: {ranks[0]}\n\tPeak MMR: {ranks[1]}\n\tGames Played: {ranks[2]}\nRanked 2v2:\n\tCurrent MMR: {ranks[3]}\n\tPeak MMR: {ranks[4]}\n\tGames Played: {ranks[5]}\nRanked 3v3:\n\tCurrent MMR: {ranks[6]}\n\tPeak MMR: {ranks[7]}\n\tGames Played: {ranks[8]}'

        # Connect to Database
        # connection = model.get_db()

    if p_message_split[0] == 'epic':
        if len(p_message_split) != 2:
            return 'Please format like below\n!epic "epic_id'

        epic_id = p_message_split[1]

        ranks = get_ranks(epic_id, 'epic')
        
        if len(ranks) == 2:
            return f'{ranks[0]}\n{ranks[1]}'
        else:
            return f'**--{ranks[9]}\'s Ranks--**\n\nRanked 1v1:\n\tCurrent MMR: {ranks[0]}\n\tPeak MMR: {ranks[1]}\n\tGames Played: {ranks[2]}\nRanked 2v2:\n\tCurrent MMR: {ranks[3]}\n\tPeak MMR: {ranks[4]}\n\tGames Played: {ranks[5]}\nRanked 3v3:\n\tCurrent MMR: {ranks[6]}\n\tPeak MMR: {ranks[7]}\n\tGames Played: {ranks[8]}'

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
