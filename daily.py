import time
import datetime
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

'''
May need to save last accessed, wait a couple minutes, and continue

Want to add it so when the task is done a message is sent over a socket to the other progam, so it knows that it can continue
'''

def grab_past_ranks():
    day = datetime.datetime.today().weekday()

    app = Flask(__name__)
    with app.app_context():
        # Connect to Database
        connection = model.get_db()

        # Grab all data from the users table
        cur = connection.execute(
            "SELECT * "
            "FROM users "
        )

        users = cur.fetchall()

        options = Options()
        # options.add_argument('--headless=new')

        model.close_db(1)

        for user in users:
            # Connect to Database
            connection = model.get_db()

            # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version="114.0.5735.90").install()), options=options)
            driver = Driver(headless2=True)

            username = user['username']
            id = user['id']
            platform = user['platform']
            print(f'{username} {id} {platform}')

            time.sleep(10)
            if platform == 'steam':
                driver.get(f'https://rocketleague.tracker.network/rocket-league/profile/steam/{id}/overview')
            elif platform == 'epic':
                driver.get(f'https://rocketleague.tracker.network/rocket-league/profile/epic/{id}/overview')
            else:
                print('Driver Error')
                return 1

            wait = WebDriverWait(driver, 15)
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'value')))
            except:
                driver.close()
                driver.quit()
                print('Player not found')
                return 1

            # Sorted by 1v1 mmr, peak 1v1 mmr, 1v1 games played (followed by 2v2 and 3v3 same format)
            elements = driver.find_elements(By.CLASS_NAME, 'value')
            mmr_values = [element.text for element in elements]

            # Get the playlists
            elements = driver.find_elements(By.CLASS_NAME, 'playlist')
            playlists = [element.text for element in elements]

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

            # print(mmr_values)
            # print(index)

            output = []
            for pos in index:
                if pos == -1:
                    output.append(-1)
                else:
                    if peak_rat:
                        location = -((len(playlists) - 1 - pos) * 3)
                    else:
                        location = -((len(playlists) - 1 - pos) * 2)
                    if location == 0:
                        if peak_rat:
                            output.append(mmr_values[location - 3])
                        else:
                            output.append(mmr_values[location - 2])
                    else:
                        if peak_rat:
                            output.append(mmr_values[location - 3])
                        else:
                            output.append(mmr_values[location - 2])

            # We now have a list of the form ['1s MMR', '2s MMR', '3s MMR']
            # Now go enter these into the database

            # print(f'{username} {day}')
            cur = connection.execute(
                "SELECT * "
                "FROM ones "
                "WHERE user = ? AND period = ? ",
                (username, day)
            )

            user = cur.fetchone()

            # print('here')
            print(username, output, day)

            # If they are already in the database Update
            if user:
                # One's update
                connection.execute(
                    "UPDATE ones "
                    "SET mmr = ? "
                    "WHERE user = ? AND period = ? ",
                    (output[0], username, day)
                )

                # Two's update
                connection.execute(
                    "UPDATE twos "
                    "SET mmr = ? "
                    "WHERE user = ? AND period = ? ",
                    (output[1], username, day)
                )

                # Three's update
                connection.execute(
                    "UPDATE threes "
                    "SET mmr = ? "
                    "WHERE user = ? AND period = ? ",
                    (output[2], username, day)
                )

            # Otherwise add
            else:
                # One's add
                connection.execute(
                    "INSERT INTO ones "
                    "VALUES ( ? , ? , ? ) ",
                    (username, output[0], day)
                )

                # Two's add
                connection.execute(
                    "INSERT INTO twos "
                    "VALUES ( ? , ? , ? ) ",
                    (username, output[1], day)
                )

                # Three's add
                connection.execute(
                    "INSERT INTO threes "
                    "VALUES ( ? , ? , ? ) ",
                    (username, output[2], day)
                )

            model.close_db(1)
    return 0

def schedule_task(scheduled_time):
    while True:
        now = time.strftime("%H:%M")
        if now == scheduled_time:
            start = time.time()
            # Stop servicing requests
            # send_pause()

            # Update the ranks
            grab_past_ranks()

            # Start servicing requests
            # send_continue()
            stop = time.time()

            # Wait for 24 hours before another execution
            elapsed = int(stop - start)
            print(elapsed)
            time.sleep(86400 - 60 - elapsed)
        else:
            # Check the time every minute (59 seconds to prevent missing the minute)
            time.sleep(59)

if __name__ == '__main__':
    # Run the rank updating script
    scheduled_time = "06:00"
    schedule_task(scheduled_time)
    stopped = grab_past_ranks()

    # If the driver or the search fails, try again
    # Can make this better by setting where we failed and start the process again from there
    while stopped:
        grab_past_ranks()
