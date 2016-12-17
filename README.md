# moodlecrawler

This tool allows you to bulk download all files from a Moodle2 server.

PSA: I don't really know Python, I just made it work.

## Requirements

* Python 3
* BeautifulSoup (bs4)
* lxml

## Config

> path = 

Path to save the files to. Must exist.

> user = 
> 
> password = 

The username and password you log in with.

> baseurl =

The base URL of the website. Example: https://moodle2.uni-wuppertal.de

> authurl = 

The URL used to login to Moodle2. Example: https://moodle2.uni-wuppertal.de/login/index.php