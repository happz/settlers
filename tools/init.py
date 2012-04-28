import sys

import hlibz.env
import hlibz.sql

import hruntime

hlibz.env.init_env(sys.argv[1])

import lib.datalayer

if 'root' in hruntime.dbroot:
  del hruntime.dbroot['root']

hruntime.dbroot['root'] = lib.datalayer.Root()
hruntime.dbroot = hruntime.dbroot['root']

sqldb = hlibz.sql.DataBase(host = 'localhost', unix_socket = '/var/run/mysqld/mysqld.sock', user = 'settlers', passwd = 'wahX6eey9ne2AkoK', db = 'settlers')
sqldb.open()
sql = sqldb.connect()

# init trumpet data
import lib.trumpet

r = sql.query("SELECT `value1`, `value2` FROM `trumpet` WHERE `name` = 'board'")
lib.trumpet.Board().text = r[0][1]

r = sql.query("SELECT `value1`, `value2` FROM `trumpet` WHERE `name` = 'forgot_password_mail'")
lib.trumpet.ForgotPasswordMail().subject = r[0][0]
lib.trumpet.ForgotPasswordMail().text = r[0][1]

r = sql.query("SELECT `value1`, `value2` FROM `trumpet` WHERE `name` = 'motd'")
lib.trumpet.MOTD().text = r[0][1]

r = sql.query("SELECT `value1`, `value2` FROM `trumpet` WHERE `name` = 'vacation_termination'")
lib.trumpet.VacationTermination().text = r[0][1]

# init localization data
r = sql.query("SELECT `language`, `name`, `value` FROM `localization`")
for e in r:
  hruntime.dbroot.localization.languages[e[0]][e[1]] = e[2]

# init users
u = lib.datalayer.User('SYSTEM', 'foobar', 'osadnici@happz.cz')
hruntime.dbroot.users[u.name] = u

u = lib.datalayer.User('happz', '955db0b81ef1989b4a4dfeae8061a9a6', 'happz@happz.cz')
u.admin = True
hruntime.dbroot.users[u.name] = u

hruntime.db.commit()
