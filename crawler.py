import configparser
import getpass
import os
import os.path
import re
import requests
import time
import urllib
import urllib3

from bs4 import BeautifulSoup
from colorama import Fore, Style
from zipfile import ZipFile


class Crawler:

    def __init__(self):
        self.session = requests.Session()
        self.app_path = os.path.dirname(os.path.abspath(__file__))

    def prompt_password(self):
        print('Password for ' + self.username + ' on ' + self.auth_url + ':')
        self.password = getpass.getpass()

    def print_config(self):
        print('Base-URL: ' + self.base_url)
        print('Auth-URL: ' + self.auth_url)
        print('Username: ' + self.username)
        print('Password: hidden')
        print('Download directory: ' + self.download_dir)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(self.app_path, 'config.ini'))
        self.base_url = config.get('DEFAULT', 'baseurl')
        self.auth_url = config.get('DEFAULT', 'authurl')
        self.username = config.get('DEFAULT', 'user')
        self.password = config.get('DEFAULT', 'password')
        self.download_dir = config.get('DEFAULT', 'path')
        if self.password is '':
            self.prompt_password()
            print()
        self.print_config()
        print()

    def login(self):
        payload = {'username': self.username, 'password': self.password}
        page = self.session.post(self.auth_url, payload)
        if '<div id="frontpage-course-list">' not in page.text:
            print('Error: Login failed')
            exit(1)
        else:
            print('Login successful')
            print()

    def download_file(self, path, link):
        try:
            page = self.session.get(link)
            page = page.text.split('class="resourceworkaround">')[1].split(
                'link to view')[0]
            soup = BeautifulSoup(page, 'lxml')
            link = soup.find('a').get('href')
            if 'resource' in link:
                web_file = self.session.get(link)
                filename = urllib.parse.unquote(web_file.url).split('/')[-1]
                path = os.path.join(path, filename)
                if (os.path.isfile(path)):
                    print('\tFile exists: ' + filename)
                else:
                    print('\tSaving file: ' + filename)
                    file = open(path, 'wb')
                    file.write(web_file.content)
                    file.close()
                    web_file.close()
        except KeyboardInterrupt:
            raise
        except:
            print(
                Fore.RED + '\tError downloading file: ' + link +
                Style.RESET_ALL)

    def download_folder(self, name, path, link):
        try:
            if not os.path.isdir(path):
                os.mkdir(path)
                print('\tCreated folder: ' + path)
            else:
                print('\tFolder exists: ' + path)
            payload = {'id': link.split('id=')[1]}
            dl_link = self.base_url + '/mod/folder/download_folder.php'
            print('\tDownloading folder: ' + name)
            web_file = self.session.post(dl_link, payload)
            zip_file_path = os.path.join(path, 'folder.zip')
            file = open(zip_file_path, 'wb')
            file.write(web_file.content)
            file.close()
            web_file.close()
            zip_file = ZipFile(zip_file_path)
            print('\tExtracting...')
            zip_file.extractall(path=path)
            zip_file.close()
            os.remove(zip_file_path)
        except KeyboardInterrupt:
            raise
        except:
            print(
                Fore.RED + '\tError downloading folder: ' + name +
                Style.RESET_ALL)

    def download_course(self, name, link):
        path = os.path.join(self.download_dir, name)
        if not os.path.isdir(path):
            os.mkdir(path)
            print('Course ' + name + ': created directory')
        else:
            print('Course ' + name + ': directory exists')
        page = self.session.get(link)
        soup = BeautifulSoup(page.text, 'lxml')
        folders = soup.find_all(class_='modtype_folder')

        for folder in folders:
            folder_name = folder.text
            folder_name = folder_name.replace(
                folder.find(class_='accesshide').text, '')
            folder_name = folder_name.replace('/', '')
            folder_name = folder_name.replace(' ', '_')
            folder_path = os.path.join(path, folder_name)
            folder_link = folder.find('a').get('href')
            self.download_folder(folder_name, folder_path, folder_link)

        links = soup.find(class_='course-content')
        if links is not None:
            links = links.find_all('a')
            for link in links:
                link = link.get('href')
                if link is not None and 'resource' in link:
                    self.download_file(path, link)

    def download_enrolled_courses(self):
        page = self.session.get(self.base_url)
        courses = page.text.split(
            '<div id="frontpage-course-list">')[1].split(
            '<span class="skip-block-to" id="skipmycourses"></span>')[0]
        regex = re.compile('<span class="coursename">(.*?)</span>')
        course_list = regex.findall(courses)

        for course_string in course_list:
            soup = BeautifulSoup(course_string, 'lxml')
            a = soup.find('a')
            course_name = a.text.replace('/', '')
            course_name = course_name.replace(' ', '_')
            course_link = a.get('href')
            self.download_course(course_name, course_link)

    def download(self):
        self.login()
        self.download_enrolled_courses()


crawler = Crawler()
crawler.load_config()
crawler.download()
