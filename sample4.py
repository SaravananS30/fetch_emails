import mysql.connector
import imaplib as imp
import email
import html2text
from datetime import datetime
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Vrdella!6",
    database="mail",
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
    formated_result = {}
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
            bool_value = "SELECT EXISTS(SELECT * FROM email WHERE clientjobid = %s)"
            cursor.execute(bool_value,(id,))
            result = cursor.fetchone()[0]
            if result==1:
                sub = msg['subject']
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
                    if comment=='-':
                        comment = "no comment"
                    sql = "UPDATE email SET status = '{}' WHERE clientjobid= '{}'".format(status,id)
                    cursor.execute(sql)
                    sql1 = "UPDATE email SET comment = '{}' WHERE clientjobid= '{}'".format(comment,id)
                    cursor.execute(sql1)
                    conn.commit()
            elif result==0:
                sub=msg['subject']
                if "Requisition ID" in plain_text_content:
                    value = plain_text_content.split("Requisition ID")[1].strip('\n')
                    value = value.split("---")[0].strip()
                    formated_result["clientjobid"] = value
                if "Requisition Title" in plain_text_content:
                    value = plain_text_content.split("Requisition Title")[1].strip('\n')
                    value = value.strip().split('\n')[0].rstrip()
                    formated_result["job_title"] = value
                if "Location" in plain_text_content:
                    value = plain_text_content.split("Location")[1].strip('\n')
                    value = value.strip().split('\n')[0].rstrip()
                    formated_result["location"] = value
                if "Site" in plain_text_content:
                    value = plain_text_content.split("Site")[1].strip('\n')
                    value = value.strip().split('\n')[0].rstrip()
                    formated_result["location"] = value
                if "Requisition Start Date" in plain_text_content:
                    start = plain_text_content.split("Requisition Start Date")[1].strip('\n')
                    start = start.strip().split('\n')[0].rstrip()
                    start = datetime.strptime(start, "%Y-%m-%d").date()
                    formated_result["job_start_date"] = start
                if "Requisition End Date" in plain_text_content:
                    end = plain_text_content.split("Requisition End Date")[1].strip('\n')
                    end = end.strip().split('\n')[0].rstrip()
                    end = datetime.strptime(end, "%Y-%m-%d").date()
                    formated_result["job_end_date"] = end
                if "Business Unit" in plain_text_content:
                    value = plain_text_content.split("Business Unit")[1].strip('\n')
                    value = value.strip().split('\n')[0].rstrip()
                    formated_result["business_unit"] = value
                if "Pay Rate:" in plain_text_content:
                    value = plain_text_content.split("Pay Rate:")[1].strip('\n')
                    value = value.strip().split('\n')[0].rstrip()
                    value = re.search(r'\d+(\.\d+)?', value)
                    value = float(value.group())
                    formated_result["job_bill_rate"] = value
                if "Pay rate:" in plain_text_content:
                    value = plain_text_content.split("Pay rate:")[1].strip('\n')
                    value = value.strip().split('\n')[0].rstrip()
                    value = re.search(r'\d+(\.\d+)?', value)
                    value = float(value.group())
                    formated_result["job_bill_rate"] = value
                if "Reason" in plain_text_content:
                    value = plain_text_content.split("Reason")[1].strip('\n')
                    value = value.strip().split('\n')[0].rstrip()
                    comment = value
                    formated_result['comment'] = comment
                if "Business Unit Code" in plain_text_content:
                    value = plain_text_content.split("Business Unit Code")[1].strip('\n')
                    value = value.strip().split('\n')[0].rstrip()
                    formated_result['business_unit_code'] = value
                if "Description" in plain_text_content:
                    value = plain_text_content.split("Description")[1].strip('\n')
                    description_lines = [line.strip() for line in value.split('\n') if line.strip()]
                    st = '\n'.join(description_lines)
                    su = "### Requisition Start Date"
                    re = st.split(su)
                    result = [re[0]]

                    if "Business Unit Code" in plain_text_content:
                        value = plain_text_content.split("Business Unit Code")[1].strip('\n')
                        value = value.strip().split('\n')[0].rstrip()
                        result.append("Business_unit_code: " + value)

                    if "Site Code" in plain_text_content:
                        value = plain_text_content.split("Site Code")[1].strip('\n')
                        value = value.strip().split('\n')[0].rstrip()
                        result.append("Site_code: " + value)

                    if "Coordinator" in plain_text_content:
                        value = plain_text_content.split("Coordinator")[1].strip('\n')
                        value = value.strip().split('\n')[0].rstrip()
                        result.append("Coordinator: " + value)

                    formated_result['job_description'] = "\n".join(result)

                b = datetime.now().date()
                if 'halted' in sub:
                    status = 'halted'
                if 'closed' in sub:
                    status = 'closed'
                if start <= b and end >= b:
                    status = 'Pending'
                else:
                    status = 'Completed'
                formated_result['status'] = status

                formated_result['client'] = 'Baxter'

                sql = """
                INSERT INTO email (clientjobid, job_title, location, job_start_date, job_end_date, business_unit, job_bill_rate, job_description, status, client, business_unit_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    formated_result["clientjobid"],
                    formated_result["job_title"],
                    formated_result["location"],
                    str(formated_result["job_start_date"]),
                    str(formated_result["job_end_date"]),
                    formated_result.get("business_unit", 0),
                    formated_result.get("job_bill_rate" , 0),
                    formated_result.get("job_description", 0),
                    formated_result["status"],
                    formated_result["client"],
                    formated_result.get('business_unit_code',0)
                )

                cursor.execute(sql, values)
                conn.commit()
