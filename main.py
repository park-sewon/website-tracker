import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib
import time
from urllib.request import urlopen, Request
import datetime
from copy import deepcopy

remove_pid = []
active_pid = []
log = []
mail_log = []
record = []
pid_index = 0
email_address = ''
email_pw = ''

def send_email(pid, rec, title, content):
    global email_address
    global email_pw
    if pid not in active_pid:
        return

    mail_content = content
    #The mail addresses and password
    sender_address = email_address
    sender_pass = email_pw
    receiver_address = rec

    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = title   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.ehlo()
    session.starttls() #enable security
    session.ehlo()
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()

    print('Mail Sent')


def new_pid():
    global pid_index
    npid = pid_index
    pid_index = pid_index + 1
    return npid


def update_log(pid, time):
    if pid not in active_pid:
        return

    global log
    flag = False
    for idx, (p, t) in enumerate(log):
        if p == pid:
            log[idx] = (p, time)
            flag = True
    if not flag:
        log.append((pid, time))

def update_mail_log(pid, time):
    if pid not in active_pid:
        return

    global mail_log
    flag = False
    for idx, (p, t) in enumerate(mail_log):
        if p == pid:
            mail_log[idx] = (p, time)
            flag = True
    if not flag:
        mail_log.append((pid, time))

def remove_log(pid):
    global log
    j = -1
    for idx, (p, t) in enumerate(log):
        if p == pid:
            j = idx
            break
    if j == -1:
        pass
    else:
        log.pop(j)

def remove_mail_log(pid):
    global mail_log
    j = -1
    for idx, (p, t) in enumerate(mail_log):
        if p == pid:
            j = idx
            break
    if j == -1:
        pass
    else:
        mail_log.pop(j)





def check_update(pid, url_text, rec, dur = 300):
    global record
    global remove_pid
    record.append((pid, url_text, rec, dur))

    # setting the URL you want to monitor
    url = Request(url_text,
                   headers={'User-Agent': 'Mozilla/5.0'})

    # to perform a GET request and load the
    # content of the website and store it in a var
    response = urlopen(url).read()

    # to create the initial hash
    currentHash = hashlib.sha224(response).hexdigest()
    escape = False
    while not escape:
        i = 0
        while i < dur:
            i = i + 1
            time.sleep(1)
            if pid in remove_pid:
                escape = True
                break

        try:
            time.sleep(dur)

            # perform the get request and store it in a var
            newresponse = urlopen(url).read()
            newHash = hashlib.sha224(newresponse).hexdigest()

            if newHash != currentHash:
                send_email(pid, rec, 'changed detected at '+url_text, 'previously:\n'+str(response)+'\n\n'+'now:\n'+str(newresponse))
                update_mail_log(pid, datetime.datetime.now())

            update_log(pid, datetime.datetime.now())

            # create a hash
            currentHash = deepcopy(newHash)

        # To handle exceptions
        except Exception as e:
            print("error happened in tracking "+url_text +" ("+datetime.datetime.now() +")")


    remove_pid.remove(pid)

import _thread

def main():
    global remove_pid
    global active_pid
    global email_address
    global email_pw
    email_con = False
    while not email_con:
        print('--Enter your gmail address:')
        email_address = input()
        print('--Enter your gmail password:')
        email_pw = input()
        try:
            mail_content = "test email"
            #The mail addresses and password
            sender_address = email_address
            sender_pass = email_pw
            receiver_address = email_address

            #Setup the MIME
            message = MIMEMultipart()
            message['From'] = sender_address
            message['To'] = receiver_address
            message['Subject'] = "test"   #The subject line
            #The body and the attachments for the mail
            message.attach(MIMEText(mail_content, 'plain'))
            #Create SMTP session for sending the mail
            session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
            session.ehlo()
            session.starttls() #enable security
            session.ehlo()
            session.login(sender_address, sender_pass) #login with mail_id and password
            text = message.as_string()
            session.sendmail(sender_address, receiver_address, text)
            session.quit()
            email_con = True
        except:
            print('-- cannot send an email using the address and passoword')

    while True:
        print('-- Enter a command (help is for help)')
        x = input()
        if x == 'add':
            print('--- Please enter the url that you want to track:')
            url_text = input()
            print('--- Please enter the email address you want to get alarmed with:')
            rec = input()
            print('--- Please enter the refresh duration in second (60 is min):')
            dur = int(input())
            if dur < 60:
                dur = 60
#             run thread

            print('--- are you sure with adding this? [y]')
            print(url_text + ', ' + rec + ', ' + str(dur))
            resp = input()
            if resp == 'y':
                pid = new_pid()
                _thread.start_new_thread(check_update, (pid, url_text, rec, dur))
                print('--- added the website on track')
                active_pid.append(pid)

        elif x == 'list':
            print('--- the below websites are currently tracked:')
            for (pid, url_text, rec, dur) in record:
                if pid in remove_pid:
                    pass
                else:
                    print(str(pid) + ', '+url_text + ', ' + rec + ', ' + str(dur))

        elif x == 'remove':
            print('--- please type the id of the website that you want to stop track:')
            rpid = int(input())
            if rpid in active_pid:
                remove_pid.append(int(rpid))
                active_pid.remove(pid)
                remove_log(pid)
                remove_mail_log(pid)

        elif x == 'status':
            print('--- see the most recent updates: (current time: '+str(datetime.datetime.now())+')')
            for (p, t) in log:
                for (pid, url_text, rec, dur) in record:
                    if pid == p:
                        print('---- last update: '+str(t)+' ('+url_text+')')

        elif x == 'help':
            print('--- there are three commands: add, list, remove, status. Enjoy')


if __name__ == "__main__":
    main()
