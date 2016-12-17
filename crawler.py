import configparser
import os
import os.path
import re
import requests
import time
import urllib3
import urllib

from bs4 import BeautifulSoup


def download_file(session, url, dir):
    dl_page = session.get(url)
    if 'class="resourceworkaround"' not in dl_page:
        dl_link = dl_page.url
    else:
        dl_page = dl_page.text.split(
            'class="resourceworkaround">')[1].split('link to view')[0]
        soup = BeautifulSoup(dl_page, 'lxml')
        dl_link = soup.find('a').get('href')
    if 'resource' not in dl_link:
        return None
    web_file = session.get(dl_link)
    print(web_file.url)


def download_folder(session, url, output_dir):
    pass


def download_course(session, url, name, output_dir):
    path = output_dir + name + '/'
    if not os.path.isdir(path):
        os.mkdir(path)
        print('Created directory for course ' + name)
    else:
        print('Course ' + name + ' exists')
    course_page = session.get(url)
    soup = BeautifulSoup(course_page.text, 'lxml')
    # course_folders = soup.find_all(class_='activity folder modtype_folder')
    course_folders = soup.find_all('li')
    course_folders = soup.find_all(class_='modtype_folder')

    for folder in course_folders:
        folder_name = folder.text
        folder_link = folder.find('a').get('href')

    course_links = soup.find(class_='course-content').find(class_='weeks')
    if course_links is not None:
        course_links = course_links.find_all('a')
        for link in course_links:
            download_file(session, link.get('href'), path)


dir = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(dir, 'config.ini'))

baseurl = config.get('DEFAULT', 'baseurl')
authurl = config.get('DEFAULT', 'authurl')
username = config.get('DEFAULT', 'user')
password = config.get('DEFAULT', 'password')
output_dir = config.get('DEFAULT', 'path')

# print('URL: ' + url)
# print('Download directory: ' + output_dir)
# print('Username: ' + username)
# print('Password: hidden')

session = requests.Session()
jar = requests.cookies.RequestsCookieJar()
payload = {'username': username, 'password': password}

r = session.post(authurl, data=payload)
content = r.text

if '<div id="frontpage-course-list">' not in content:
    print('Error')
    exit(1)

courses = content.split('<div id="frontpage-course-list">')[1].split(
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
    download_course(session, course[1], course[0], output_dir)
    # if not os.path.isdir(output_dir + course[0] + '/'):
    #     os.mkdir(output_dir + course[0])
    # r = session.get(course[1])
    # soup = BeautifulSoup(r.text, 'lxml')
    # course_links = soup.find(class_='course-content').find(class_='weeks')

    # if course_links is not None:
    #     course_links = course_links.find_all('a')
    # else:
    #     continue
    # for link in course_links:
    # current_dir = output_dir + course[0] + '/'
    # href = link.get('href')
    # if 'resource' in href:
    #     time.sleep(1)
    #     dl_page = session.get(href)
    #     dl_page = dl_page.text.split(
    #         'class="resourceworkaround">')[1].split('link to view')[0]
    #     dl_soup = BeautifulSoup(dl_page, 'lxml')
    #     dl_link = dl_soup.find('a').get('href')
    #     web_file = session.get(dl_link)
    #     filename = current_dir + \
    #         urllib.parse.unquote(web_file.url).split('/')[-1]
    #     if os.path.isfile(filename):
    #         print('File exists: ' + filename)
    #     else:
    #         print('Saving: ' + filename)
    #         file = open(filename, 'wb')
    #         file.write(web_file.content)
    #         file.close()
    #         web_file.close()
