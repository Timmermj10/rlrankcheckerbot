# rlrankcheckerbot
This is a Discord bot that uses Selenium and ChromeDriver to access the ranks of players in an online game called Rocket League

It also has Database capabilities to make the repetitive search of players easier for the user 
  The Database holds the player's name, steamID/epicID (specific to each individual player of the game), and the platform they use
  This allows the user only to need the players name to use the command !search/{name} rather than having to repeatedly use the !steam/!epic commands with the corresponding steamID/epicID

Made this as a side project because I thought it would be fun for our community Discord server

Updates:
*Starting to include updates on the work I'm doing for the bot because I wasn't able to give one of my friends an accurate estimate on how long I've been working on it. I figured it would be cool to keep track of all the updates and approximate time spent!*

  August 18th:
    Yesterday the bot went down after weeks of successful operation. This occurred because of an update to ChromeDriver download URL links. This led to an issue where the program would error out saying that the current ChromeDriver could only function with versions of Google Chrome 114. After a bit of research, I found a quick fix using SeleniumBase, a well-maintained branch of Selenium that already had a fix for the URL issue. I found this solution in the follow-ups to a [GitHub post](https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/1477). *The specific follow-up can be found [here](https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/1477#issuecomment-1680867979)*. The fix was as simple as dropping the old web driver formatting for the ChromeDriver and using the built-in Driver from Seleniumbase! I also did a few minor upgrades including a custom response, downtime for the daily script, and the addition of a win streak display. ~6 hours

  August 20th:
    Made some nice QOL updates today. I updated the main !help command to make it more fleshed out as well as readable. I also restricted the bot to certain channels because it wasoperatingg outside of where we wanted it to. The 'hi' command that I made specifically for one of our server members turned out to be executed a bit more than I liked (the method searched for any piece of the string that had 'hi' in it rather than the word 'hi' standalone within the string). So I updated it to only execute when 'hi timibot' is in the string. I also made it so anyone could say hi, and the bot would respond back Hi Mr. {Discord Username}, a few people felt left out :(. I also made it so the restricted use of the bot between 6:00 and 6:15 only outputted when commands were used. Lastly, I updated the Discord Task to output that the pause was taking place at 6:00 am EST (when the daily checks actually happen within the daily.py script! ~90 mins
