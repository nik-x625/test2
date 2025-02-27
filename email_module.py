'''
bla bla doc here
'''

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logger_custom import get_module_logger

DEFAULT_ADDRESS = 'mabolfathi@gmail.com'

FROMADDR = "wpmessages1050@gmail.com"
PASSWORD = 'vqqfnnsdvcqshzrj'  # 'jthn5g_4bdf4nn224kbjshhive'

logger = get_module_logger(__name__)


def send_email_contact(message_dict):
    '''
    This method is called by Flask route of '/contact'
    '''

    try:
        toaddr = DEFAULT_ADDRESS

        logger.debug('picked from queue, in send_email_contact method')

        msg = MIMEMultipart()
        msg['From'] = "QLines Contact Page"
        msg['To'] = toaddr
        msg['Subject'] = message_dict['subject']

        message_html = '''
        Submitted in portal: {}
        Subject: {}
        First name: {}
        Last name: {}
        Email address: {}
        Date/Time: {}

        Message:
        {}
        '''.format("QLines contact form",
                   message_dict['subject'],
                   message_dict['first_name'],
                   message_dict['last_name'],
                   message_dict['email'],
                   message_dict['datetime'],
                   message_dict['message']
                   )

        logger.debug(
            'picked from queue, in send_email_contact method, going to login to gmail and submit the email')

        # 'message_dict['message'], 'plain'))
        msg.attach(MIMEText(message_html, 'plain'))
        text = msg.as_string()

        # login to gmail sender account
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        logger.debug('login - going to')
        server.login(FROMADDR, PASSWORD)
        logger.debug('login - done')

        logger.debug(
            'picked from queue, in send_email_contact method, the login result is: '+str(text))

        # main sending action
        server.sendmail(FROMADDR, toaddr, text)
        server.quit()
        logger.debug(
            'picked from queue, in send_email_contact method, the email sending attempt done')

        return True
    except Exception as e:
        logger.error(e)


def send_email_signup(message_dict):
    '''
    This method is called by Flask route of '/signup'

    message_dict =  {
                    'email':'test_email@abc.xxx,
                    'confirmation_link': 'https://qlines.net/confirmation/sdfsdfwekjfnwekrng'
                    }
    '''

    logger.debug(
        'picked from queue, in send_email_signup \
        method - start, message_dict: %f ' % message_dict)

    # todo: fix this later
    email = message_dict['email']
    if not email:
        email = DEFAULT_ADDRESS

    # create message metadata
    msg = MIMEMultipart()
    msg['From'] = "QLines sign-up"
    msg['To'] = email
    msg['Subject'] = "Confirm your email address!"

    logger.debug('# send_email_signup, sending to: '+str(email))
    logger.debug('# send_email_signup, msg body: '+str(msg))

    # create message body
    message_html = '''
    Confirm your email address!
    Link: {}

    '''.format(message_dict['confirmation_link'],
               )

    logger.debug(
        'picked from queue, in send_email_signup method, going to login to gmail and submit the email')

    # 'message_dict['message'], 'plain'))
    msg.attach(MIMEText(message_html, 'plain'))
    text = msg.as_string()

    # login to gmail sender account
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(FROMADDR, PASSWORD)

    logger.debug(
        'picked from queue, in send_email_signup method, the login result is: '+str(text))

    # main sending action
    server.sendmail(FROMADDR, email, text)
    server.quit()
    logger.debug(
        'picked from queue, in send_email_signup method, the email sending attempt done')

    return True


def submit_email_for_newsletter(message_dict):
    msg = MIMEMultipart()
    msg['From'] = "QLines newsletter form"
    msg['To'] = DEFAULT_ADDRESS
    msg.attach(MIMEText(str(message_dict), 'plain'))
    msg['Subject'] = 'Request for newsletter'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(FROMADDR, PASSWORD)
    text = msg.as_string()
    server.sendmail(FROMADDR, DEFAULT_ADDRESS, text)
    server.quit()
    return True

def send_general_text_email(message_text, subject):
    msg = MIMEMultipart()
    msg['From'] = "QLines alerting form"
    msg['To'] = DEFAULT_ADDRESS
    msg.attach(MIMEText(message_text, 'plain'))
    msg['Subject'] = subject

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(FROMADDR, PASSWORD)
    text = msg.as_string()
    server.sendmail(FROMADDR, DEFAULT_ADDRESS, text)
    server.quit()
    return True


def send_email_async(msg, toaddr=None):
    '''
    This method is called by RQ Worker
    '''

    if not toaddr:
        toaddr = DEFAULT_ADDRESS

    logger.debug('# in async email func, start....')

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(FROMADDR, PASSWORD)
    text = msg.as_string()
    server.sendmail(FROMADDR, toaddr, text)
    server.quit()

    logger.debug('# fromaddr: '+str(FROMADDR))
    logger.debug('# toaddr: '+str(toaddr))
    logger.debug('# text: '+str(text))

    logger.debug('# in async email func, end....')

    return True


def send_email_contact__old(message_dict):
    '''
    This method is called by Flask route of '/contact'
    '''

    msg = MIMEMultipart()
    msg['From'] = "QLines"
    msg['To'] = DEFAULT_ADDRESS
    msg['Subject'] = message_dict['subject']

    message_html = '''
    Submitted in portal: {}
    Subject: {}
    First name: {}
    Last name: {}
    Email address: {}
    Date/Time: {}

    Message:
    {}
    '''.format("QLines contact form",
               message_dict.get('subject', ''),
               message_dict.get('first_name', ''),
               message_dict.get('last_name', ''),
               message_dict.get('email', ''),
               message_dict.get('datetime', ''),
               message_dict.get('message', '')
               )

    logger.debug('# contact contents to send as email: '+str(message_html))

    msg.attach(MIMEText(message_html, 'plain'))

    try:
        send_email_async(msg)
    except Exception as e:
        logger.debug('# email enqueue error: '+str(e))
        return False
    return "The message sent successfully!"

    return "The message sent successfully!"


if __name__ == "__main__":
    #send_email_contact({'first_name': '', 'last_name': '', 'email': '',
    #                    'subject': '', 'message': 'xx', 'datetime': 'fff'})
    
    send_general_text_email('some simple email test', 'test subject')
