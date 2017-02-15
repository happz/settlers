"""
Functions for sending e-mails.
"""

__author__              = 'Milos Prchlik'
__copyright__           = 'Copyright 2010 - 2012, Milos Prchlik'
__contact__             = 'happz@happz.cz'
__license__             = 'http://www.php-suit.com/dpl'

import smtplib
import email
import email.message
import email.utils
import email.mime.text

import hlib

def send_email(app, sender, recipient, subject, body):
  if not sender.startswith('From: '):
    sender = 'From: ' + sender

  if not recipient.startswith('To: '):
    recipient = 'To: ' + recipient

  header_charset = 'ISO-8859-1'

  for body_charset in 'UTF-8', 'US-ASCII', 'ISO-8859-1':
    try:
      body.encode(body_charset)
    except UnicodeError:
      pass
    else:
      break

  sender_name, sender_addr = email.utils.parseaddr(sender)
  recipient_name, recipient_addr = email.utils.parseaddr(recipient)

  sender_name = str(email.Header.Header(unicode(sender_name), header_charset))
  recipient_name = str(email.Header.Header(unicode(recipient_name), header_charset))

  sender_addr = sender_addr.encode('ascii')
  recipient_addr = recipient_addr.encode('ascii')

  # pylint: disable-msg=W0631
  msg = email.mime.text.MIMEText(body.encode(body_charset), 'plain', body_charset)
  msg['From'] = email.utils.formataddr((sender_name, sender_addr))
  msg['To'] = email.utils.formataddr((recipient_name, recipient_addr))
  msg['Subject'] = email.Header.Header(unicode(subject), header_charset)

  smtp = smtplib.SMTP(app.config['mail.server'])
  smtp.sendmail(sender, recipient, msg.as_string())
  smtp.quit()
