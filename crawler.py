import configparser
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


def download_file(session, url, dir):
    try:
        dl_page = session.get(url)
        dl_page = dl_page.text.split(
            'class="resourceworkaround">')[1].split('link to view')[0]
        soup = BeautifulSoup(dl_page, 'lxml')
        dl_link = soup.find('a').get('href')
        if 'resource' in dl_link:
            web_file = session.get(dl_link)
            filename = dir + urllib.parse.unquote(web_file.url).split('/')[-1]
            if os.path.isfile(filename):
                print('\t' + 'File exists: ' + filename)
            else:
                print('\t' + 'Saving file: ' + filename)
                file = open(filename, 'wb')
                file.write(web_file.content)
                file.close()
                web_file.close()
    except:
        print(
            Fore.RED + '\t' + 'Error downloading file: ' + url + Style.RESET_ALL)


def download_folder(session, url, baseurl, output_dir, name):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
        print('\t' + 'Created folder: ' + output_dir)
    else:
        print('\t' + 'Folder exists: ' + output_dir)
    payload = {'id': url.split('id=')[1]}
    folder_dl_url = baseurl + '/mod/folder/download_folder.php'
    print('\t' + 'Downloading folder: ' + name)
    zip_folder = session.post(folder_dl_url, payload)
    zipfile_name = output_dir + '/' + 'folder.zip'
    file = open(zipfile_name, 'wb')
    file.write(zip_folder.content)
    file.close()
    zip_folder.close()
    zipfile = ZipFile(zipfile_name)
    print('\t' + 'Extracting...')
    zipfile.extractall(path=output_dir)
    zipfile.close()
    os.remove(zipfile_name)


def download_course(session, url, baseurl, name, output_dir):
    path = output_dir + name + '/'
    if not os.path.isdir(path):
        os.mkdir(path)
        print('Created directory for course ' + name)
    else:
        print('Course ' + name + ' exists')
    course_page = session.get(url)
    soup = BeautifulSoup(course_page.text, 'lxml')
    course_folders = soup.find_all('li')
    course_folders = soup.find_all(class_='modtype_folder')

    for folder in course_folders:
        folder_name = folder.text
        folder_name = folder_name.replace(
            folder.find(class_='accesshide').text, '')
        folder_name = folder_name.replace('/', '')
        folder_name = folder_name.replace(' ', '_')
        folder_link = folder.find('a').get('href')
        folder_path = path + folder_name
        download_folder(
            session, folder_link, baseurl, folder_path, folder_name)

    course_links = soup.find(class_='course-content')  # .find(class_='weeks')
    if course_links is not None:
        course_links = course_links.find_all('a')
        for link in course_links:
            link = link.get('href')
            if link is not None and 'resource' in link:
                download_file(session, link, path)


def download_enrolled(session, baseurl, output_dir):
    page = session.get(baseurl)

    courses = page.text.split('<div id="frontpage-course-list">')[1].split(
        '<span class="skip-block-to" id="skipmycourses"></span>')[0]

    regex = re.compile('<span class="coursename">(.*?)</span>')
    course_list = regex.findall(courses)
    courses = []

    for course_string in course_list:
        soup = BeautifulSoup(course_string, 'lxml')
        a = soup.find('a')
        course_name = a.text.replace('/', '')
        course_name = course_name.replace(' ', '_')
        course_link = a.get('href')
        courses.append([course_name, course_link])

    for course in courses:
        download_course(session, course[1], baseurl, course[0], output_dir)


dir = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(dir, 'config.ini'))

baseurl = config.get('DEFAULT', 'baseurl')
authurl = config.get('DEFAULT', 'authurl')
username = config.get('DEFAULT', 'user')
password = config.get('DEFAULT', 'password')
output_dir = config.get('DEFAULT', 'path')

print('Base-URL: ' + baseurl)
print('Auth-URL: ' + authurl)
print('Download directory: ' + output_dir)
print('Username: ' + username)
print('Password: hidden\n')

session = requests.Session()
payload = {'username': username, 'password': password}

r = session.post(authurl, data=payload)
content = r.text

if '<div id="frontpage-course-list">' not in content:
    print('Error')
    exit(1)

download_enrolled(session, baseurl, output_dir)
