from sched import scheduler
from time import time, sleep
import netifaces
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


email_user = "geobrickspy@gmail.com"
email_password = "Geobricks2014"
email_address = "geobrickspy@gmail.com"

seconds_interval = 3600 #seconds
s = scheduler(time, sleep)

email_header = "PGeo - IP Service"
email_body = "<html><head></head>" \
             "<body>" \
             "<div style='padding-top:10px;'>IP: {{IP}}</div>" \
             "</body>" \
             "</html>"


def task(start, interval, func):
    event_time = start
    var = 1
    while var == 1:
        s.enterabs(event_time, 0, func, ())
        event_time += interval
        s.run()
        sleep(interval)


def send_ip():
    ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
    html = email_body.replace("{{IP}}", ip)
    send_email(email_user, email_address, email_password, email_header, html)


def send_email(user, to, pwd, header, body, smtp="smtp.gmail.com", smtp_port=587):
    to = to
    gmail_user = user
    gmail_pwd = pwd
    smtpserver = smtplib.SMTP(smtp, smtp_port)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = header
    msg['From'] = gmail_user
    msg['To'] = to
    part = MIMEText(body, 'html')
    msg.attach(part)
    smtpserver.sendmail(gmail_user, to, msg.as_string())
    smtpserver.close()

if __name__ == '__main__':
    task(time(), seconds_interval, send_ip)
