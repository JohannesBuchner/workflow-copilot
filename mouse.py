from Xlib import display

root = None
def get_root_window():
	global root
	if root is None:
		root = display.Display().screen().root
	return root

def mousepos():
    """mousepos() --> (x, y) get the mouse coordinates on the screen (linux, Xlib)."""
    data = get_root_window().query_pointer()._data
    return data["root_x"], data["root_y"]


def test():
	print("The mouse position on the screen is {0}".format(mousepos()))

def writelog(logfile, sleeptime):
	import time, sys
	out = file(logfile, 'a')
	while True:
		time.sleep(sleeptime)
		# sudo evtest /dev/input/by-path/platform-i8042-serio-0-event-kbd
		x, y = mousepos()
		out.write("{0}\n".format(dict(x=x, y=y, time=time.time())))
	out.close()

def mouse_velocity_feed(sleeptime):
	import time
	xlast, ylast = mousepos()
	while True:
		time.sleep(sleeptime)
		x, y = mousepos()
		v = ((xlast - x)**2 + (ylast - y)**2)**0.5
		xlast, ylast = x, y
		if v > 0:
			#print 'yielding mouse velocity', v
			yield (time.time(), v)

def writedb(logfile, sleeptime):
	import sqlite3, os
	import time
	exists = os.path.exists(logfile)
	conn = sqlite3.connect(logfile)
	c = conn.cursor()
	if not exists:
		c.execute('''CREATE TABLE mouse (time real, d real)''')
	i = 0
	for t, v in mouse_velocity_feed(sleeptime):
		c.execute("INSERT INTO mouse VALUES (?, ?)", (t, v))
		
		i = i + 1
		if i > 60:
			i = 0
			conn.commit()
	out.close()

if __name__ == "__main__":
	import sys
	logfile = sys.argv[1]
	sleeptime = float(sys.argv[2])
	#writelog(logfile, sleeptime)
	
	writedb(logfile, sleeptime)
	
