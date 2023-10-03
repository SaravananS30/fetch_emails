import mysql.connector
import imaplib as imp
import email
from datetime import datetime
import html2text

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Vrdella!6",
    database="task",
)
cursor = conn.cursor()
imapHostServer = 'imap.gmail.com'
imapVar = imp.IMAP4_SSL(imapHostServer)
imapUserEmail= 'saravanan@vrdella.com'
imapPassword = 'vwxz bznq xbgl xcsl'
imapVar.login(imapUserEmail, imapPassword)
imapVar.select('Inbox')
result, data = imapVar.uid('search', None, '(UNSEEN)')
inbox_item_list = data[0].split()
email_list = []

for item in inbox_item_list:
    result, email_data = imapVar.uid('fetch', item, '(RFC822)')
    raw_email = email_data[0][1].decode("UTF-8")
    msg = email.message_from_string(raw_email)
    sub = msg['subject']
    import re
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get_content_type() == "text/html":
            html_content = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
            plain_text_content = html2text.html2text(html_content)
            if "Requisition ID" in plain_text_content:
                value = plain_text_content.split("Requisition ID")[1].strip('\n')
                value = value.split("---")[0].strip()
                id = value
            if 'halted' in sub:
                status = 'halted'
            if 'closed' in sub:
                status = 'closed'
            if "Reason" in plain_text_content:
                value = plain_text_content.split("Reason")[1].strip('\n')
                value = value.strip().split('\n')[0].rstrip()
                comment = value

            bool_value = "SELECT EXISTS(SELECT * FROM email_fetch WHERE clientjobid = %s)"
            cursor.execute(bool_value,(id,))
            result = cursor.fetchone()[0]
            if result==1:
                sql = "UPDATE email_fetch SET status = '{}' WHERE clientjobid= '{}'".format(status,id)
                cursor.execute(sql)
                sql1 = "UPDATE email_fetch SET comment = '{}' WHERE clientjobid= '{}'".format(comment,id)
                cursor.execute(sql1)
                conn.commit()
