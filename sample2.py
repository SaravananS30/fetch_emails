import imaplib as imp
import email
from datetime import datetime
import html2text


def fetch_emails(imapUserEmail, imapPassword):
    msgs = []
    imapHostServer = 'imap.gmail.com'
    #     imapUserEmail= 'saravanan@vrdella.com'
    #     imapPassword = 'vwxz bznq xbgl xcsl'
    imapVar = imp.IMAP4_SSL(imapHostServer)
    imapVar.login(imapUserEmail, imapPassword)
    imapVar.select('alabama')
    #     result, data = imapVar.uid('search', None, '(UNSEEN)')
    result, data = imapVar.uid('search', "FROM", "jobs_della@vrdella.com")
    inbox_item_list = data[0].split()
    for item in inbox_item_list:
        result, email_data = imapVar.uid('fetch', item, '(RFC822)')
        raw_email = email_data[0][1].decode("UTF-8")
        msg = email.message_from_string(raw_email)
        msgs.append(msg)
    return msgs


def format(msgs):
    response = []
    for msg in msgs:
        result = {}
        sub = msg['subject']
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                plain_text_content = html2text.html2text(html_content)
                if "Requisition" in sub:
                    value = ''.join(filter(str.isdigit, sub))
                    result['Requisition ID'] = value
                if "closed" in sub:
                    result['Status'] = "Closed"
                if "Hold" in sub:
                    result['Status'] = "On Hold"
                comment = plain_text_content.split('The following')[1].split(".")[0].strip().capitalize()
                result['Comment'] = comment
                response.append(result)
    return response
