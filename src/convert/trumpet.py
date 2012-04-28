import convert

import lib.trumpet

class Convertor(convert.Convertor):
  def __init__(self, *args, **kwargs):
    super(Convertor, self).__init__('trumpet', *args, **kwargs)

  def run(self):
    r = self.db.query('SELECT `value1`, `value2` FROM `trumpet` WHERE `name` = \'board\'')
    lib.trumpet.Board().text = r[0][1]

    r = self.db.query('SELECT `value1`, `value2` FROM `trumpet` WHERE `name` = \'forgot_password_mail\'')
    lib.trumpet.PasswordRecoveryMail().subject = r[0][0]
    lib.trumpet.PasswordRecoveryMail().text = r[0][1]

    r = self.db.query('SELECT `value1`, `value2` FROM `trumpet` WHERE `name` = \'vacation_termination\'')
    lib.trumpet.VacationTermination().text = r[0][1]

convert.CONVERTORS['trumpet'] = Convertor
