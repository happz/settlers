import clr

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
clr.AddReference("System.Net")
clr.AddReference("System.Web")
clr.AddReference("System.Web.Extensions")

import System.Windows.Forms
import System.Drawing
import System.Net
import System.IO
import System.Text
import System.Web

LABEL = 'Osadníci - Hlídáček'
CONFIG_FILE = 'settlers.conf'
URI = 'http://osadnici-test.happz.cz/pull_notify_at'

API_TOKEN = ''

def json_decode(str):
  return System.Web.Script.Serialization.JavaScriptSerializer().DeserializeObject(str)

class APIRequest(object):
  def __init__(self, uri):
    super(APIRequest, self).__init__()

    System.Net.ServicePointManager.Expect100Continue = False

    self.uri = uri
    self.bytes = System.Text.Encoding.ASCII.GetBytes('api_token=' + API_TOKEN)

  def run(self):
    req = System.Net.WebRequest.Create(self.uri)

    req.ContentType = 'application/x-www-form-urlencoded'
    req.Method = 'POST'
    req.ContentLength = self.bytes.Length

    req_stream = req.GetRequestStream()
    req_stream.Write(self.bytes, 0, self.bytes.Length)
    req_stream.Close()

    res = req.GetResponse()
    return System.IO.StreamReader(res.GetResponseStream()).ReadToEnd()

class ErrorDialog(System.Windows.Forms.Form):
  def __init__(self, msg):
    super(ErrorDialog, self).__init__()

    self.Text = LABEL
    self.Width = 300
    self.Height = 200

    self.label = System.Windows.Forms.Label(Text = msg, Location = System.Drawing.Point(25, 25), Width = 250, Height = 100)
    self.button = System.Windows.Forms.Button(Text = 'OK', Location = System.Drawing.Point(25, 125), Width = 125)

    self.button.Click += self.onExit
    self.CancelButton = self.button

    self.Controls.Add(self.label)
    self.Controls.Add(self.button)

  def onExit(self, sender, event):
    self.Close()

  @staticmethod
  def report(msg):
    ed = ErrorDialog(msg)
    ed.ShowDialog()

class Main(object):
  def __init__(self):
    super(Main, self).__init__()

    self.request = APIRequest(URI)

    cm = System.Windows.Forms.ContextMenu()

    mi = System.Windows.Forms.MenuItem("Exit")
    mi.Click += self.onExit
    cm.MenuItems.Add(mi)

    self.notifyIcon = System.Windows.Forms.NotifyIcon()
    self.notifyIcon.Icon = System.Drawing.Icon("favicon.ico")
    self.notifyIcon.Visible = True
    self.notifyIcon.ContextMenu = cm
    self.notifyIcon.BalloonTipTitle = LABEL

    self.onTick(None, None)    

    timer = System.Windows.Forms.Timer()
    timer.Interval = 300000
    timer.Tick += self.onTick
    timer.Start()

  def onTick(self, sender, event):
    reply = self.request.run()
    reply = json_decode(reply)

    if reply['status'] != 200:
      return

    events = reply['events']

    msg = []
    if events['on_turn']:
      msg.append('Jste na tahu! Čeká %i her.' % events['on_turn'])

    if events['chat']:
      msg.append('Nové příspěvky na nástěnce! Celkem %i neprečtených.' % events['chat'])

    if len(msg) > 0:
      self.notifyIcon.BalloonTipText = '\n'.join(msg)
      self.notifyIcon.ShowBalloonTip(1000)

  def onExit(self, sender, event):
    self.notifyIcon.Visible = False
    System.Windows.Forms.Application.Exit()

if __name__ == "__main__":
  def exceptionHandler(sender, event):
    # Big long nasty .NET exception
    print event.Exception
    print

    # The Exception object (not much information)
    # sys.exc_info() doesn't return anything useful here
    e = event.Exception.Data['PythonExceptionInfo']
    print e

    # A hack suggested by Dino Viehland which
    # gets you a nicely formatted exception
    from IronPython.Hosting import PythonEngine
    pyE = PythonEngine()
    print pyE.FormatException(event.Exception)

  System.Windows.Forms.Application.ThreadException += System.Threading.ThreadExceptionEventHandler(exceptionHandler)
  System.Windows.Forms.Application.SetUnhandledExceptionMode(System.Windows.Forms.UnhandledExceptionMode.CatchException)

  if not System.IO.File.Exists(CONFIG_FILE):
    ErrorDialog.report('Stahněte si konfigurační soubor z webu hry (Nastavení => API klíč => Stahnout) a uložte jej do adresáře s hlídáčkem.')
    System.Environment.Exit(1)

  with open(CONFIG_FILE, 'r') as f:
    cf = json_decode(f.read())

    API_TOKEN = cf['api_token']

  main = Main()
  try:
    System.Windows.Forms.Application.Run()

  except KeyboardInterrupt:
    main.onExit(None, None)
