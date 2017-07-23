#p4k album grabber
from selenium import webdriver
import smtplib
import base64
from email.mime.text import MIMEText
import sched, time
import win32gui, win32con

toplist = []
winlist = []

def enum_callback(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

def checkBNM(sc):
    #setup email info
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    frm = "BNM Script"
    to = "yourPrimaryEmailAddress@gmail.com"
    username = "emailAddressToSendFrom@gmail.com"
    password = base64.standard_b64decode('yourBase64EncodedPassword')
    server.login(username,password)

    with open("musiclist.txt", 'r') as readMe:
        listOfAlbums = []
        for line in readMe:
            listOfAlbums.append(line)

    driver = webdriver.PhantomJS(executable_path='C:\Path\To\Your\Pantomjs.exe')

    #finds and minimizes the window that phantomjs opens
    try:
        win32gui.EnumWindows(enum_callback, toplist)
        phantom = [(hwnd, title) for hwnd, title in winlist if 'phantom' in title.lower()]
        phantom = phantom[0]
        win32gui.ShowWindow(phantom[0], win32con.SW_MINIMIZE)
        del winlist[:]
        del toplist[:]
    except:
        pass

    driver.get("http://pitchfork.com/reviews/best/albums/?page=1")
    albums = driver.find_elements_by_class_name('review')

    writeToMe = open("musiclist.txt", 'a')

    newAlbums = []

    for album in albums:
        link = album.find_element_by_class_name('album-link').get_attribute("href")
        artist = album.find_element_by_class_name('artist-list').text
        title = album.find_element_by_class_name('title').text
        try:
            genre = album.find_element_by_css_selector('ul.genre-list.before.inline').text
        except:
            genre = "NO GENRE LISTED"

        alreadyAdded = False
        for listed in listOfAlbums:
            pieces = listed.split(" - ")
            if (pieces[0] == artist and pieces[1] == title) or (not artist) or (not title):
                alreadyAdded = True

        if alreadyAdded == False:
            string = artist + " - " + title + " - " + genre + '\n'
            albumInfo = []
            albumInfo.append(string)
            albumInfo.append(link + "")
            newAlbums.append(albumInfo)

    for newAlbumInfo in newAlbums:
        theString = newAlbumInfo[0]
        theLink = newAlbumInfo[1]

        driver.get(theLink)
        writeToMe.write(theString)
        score = "Score: " + driver.find_element_by_class_name('score').text + '\n'
        msg = "\r\n".join([
          "From: " + frm,
          "To: " + to,
          "Subject: Best New Music from Pitchfork",
          "",
          theString + score + theLink
          ])
        server.sendmail(frm, to, msg)

    writeToMe.close()
    server.quit()
    driver.quit()
    #runs script again after 2 hours
    s.enter(7200, 1, checkBNM, (sc,))

if __name__ == "__main__":
    #sets script to run after 2 hours
    s = sched.scheduler(time.time, time.sleep)
    s.enter(7200, 1, checkBNM, (s,))
    s.run()