# moodlecrawler

This tool allows you to bulk download all files from a Moodle2 server.

The code ist based on this Moodle downloader: https://github.com/vinaychandra/Moodle-Downloader

## Requirements

* Python 3
* BeautifulSoup (bs4)
* colorama
* lxml

## Config

> path = 

Path to save the files to. Must exist.

> user = 
> 
> password = 

The username and password you log in with. When you leave the password empty, you will be prompted
for it.

> baseurl =

The base URL of the website. Example: https://moodle2.uni-wuppertal.de

> authurl = 

The URL used to login to Moodle2. Example: https://moodle2.uni-wuppertal.de/login/index.php