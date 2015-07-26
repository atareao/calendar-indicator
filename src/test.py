import sys
 
_login_success = False
def login():
  from gobject import MainLoop
  from dbus.mainloop.glib import DBusGMainLoop
  from ubuntuone.platform.credentials import CredentialsManagementTool
 
  global _login_success
  _login_success = False
 
  DBusGMainLoop(set_as_default=True)
  loop = MainLoop()
 
  def quit(result):
    global _login_success
    loop.quit()
    if result:
            _login_success = True
 
  cd = CredentialsManagementTool()
  d = cd.login()
  d.addCallbacks(quit)
  loop.run()
  if not _login_success:
    sys.exit(1)
 
if len(sys.argv) <= 1:
  login()
  sys.exit(1)
 
if sys.argv[1] == "login":
  login()
