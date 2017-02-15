import sys

from twisted.mail.smtp import sendmail
from twisted.internet.task import react
from email.mime.text import MIMEText
from twisted.internet import reactor


def sendMail(recipients, subject, text):
    def errback(failure):
        failure.printTraceback(file = sys.stderr)

    message = MIMEText(text)
    message['Subject'] = subject
    message['From'] = 'osadnici@happz.cz'
    message['To'] = ', '.join(recipients)

    defer = sendmail('localhost', 'osadnici@happz.cz', recipients, message, reactor = reactor)
    defer.addErrback(errback)
