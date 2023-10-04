import imaplib as imp
import email
from datetime import datetime
import html2text
import mysql.connector


def fetch_emails(imapUserEmail, imapPassword):
    imapHostServer = 'imap.gmail.com'
    imapVar = imp.IMAP4_SSL(imapHostServer)
    imapVar.login(imapUserEmail, imapPassword)
    imapVar.select('Inbox')
    result, data = imapVar.uid('search', '(UNSEEN)')
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
                formated_result = {}

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
                if "Business Unit Code" in plain_text_content:
                    value = plain_text_content.split("Business Unit Code")[1].strip('\n')
                    value = value.strip().split('\n')[0].rstrip()
                    formated_result['business_unit_code'] = value
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
                if start <= b and end >= b:
                    formated_result['status'] = 'Pending'
                else:
                    formated_result['status'] = 'Completed'

                formated_result['client'] = 'Baxter'
                email_list.append(formated_result)

    return email_list


def database(email_list):
    # Connect to your MySQL database
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Vrdella!6",
        database="mail",

    )

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Loop through the JSON response and insert each record into the MySQL table

    sql = """
        INSERT INTO email (clientjobid, job_title, location, job_start_date, job_end_date, business_unit, job_bill_rate, job_description, status, client, business_unit_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

    values = []
    for record in details:
        values.append(
            (
                record["clientjobid"],
                record["job_title"],
                record["location"],
                str(record["job_start_date"]),
                str(record["job_end_date"]),
                record["business_unit"],
                record["job_bill_rate"],
                record["job_description"],
                record["status"],
                record["client"],
                record['business_unit_code']
            )
        )
    print(values)
    # Execute the SQL INSERT statement with executemany
    cursor.executemany(sql, values)

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and database connection
    cursor.close()
    conn.close()


details = fetch_emails(imapUserEmail='saravanan@vrdella.com', imapPassword='vwxz bznq xbgl xcsl')
database(details)
