
import subprocess

def runscript(name):
	args = ('./interact', name,)
	p = subprocess.Popen(args)
	p.wait()
	if p.wait() != 0:
		raise Exception('return value of startup script was non-zero')
# 'nmcli nm enable true'

def startup():
	runscript('startup')
def interrupt_user():
	# now is a opportunity to get the users attention.
	runscript('interrupt')

def check_news():
	# fetch news items, continue notification stream, etc.
	runscript('check-news')



