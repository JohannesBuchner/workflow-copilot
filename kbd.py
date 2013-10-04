# input from sudo evtest /dev/input/by-path/platform-i8042-serio-0-event-kbd
import sys

def kbd_event_feed(instream = sys.stdin):
	while True:
		line = instream.readline()
		if line is None:
			break
		if not line.startswith("Event:"):
			continue
		if line.endswith("-------------- SYN_REPORT ------------\n"):
			continue
		#print 'key pressed:'
		a = line
		#b = sys.stdin.readline()
	
		#print '', a
		#print '', b
		parts = a.split(",")
		if len(parts) != 4:
			continue
		e, t, c, v = a.split(",")
		if not t.startswith(' type 1 '):
			continue
	
		#e2, t2, c2, v2 = b.split(",")
		#print "parts1: '%s' '%s' '%s' '%s'" % (e, t, c, v)
		#print "parts2: '%s' '%s' '%s' '%s'" % (e2, t2, c2, v2)
		values = (float(e.split(' ')[2]),
			4, 4,
			int(t.split(' ')[2]),
			int(c.split(' ')[2]),
			#int(t2.split(' ')[2]),
			#int(c2.split(' ')[2]),
			)
		#print 'yielding kbd event', values
		yield values

if __name__ == '__main__':
	import sqlite3, os
	logfile = sys.argv[1]
	exists = os.path.exists(logfile)
	conn = sqlite3.connect(logfile)
	curs = conn.cursor()
	if not exists:
		curs.execute('''CREATE TABLE kbd (time real, msctype int, msccode int, keytype int, keycode int)''')
	k = 0
	for event in kbd_event_feed():
		curs.execute("INSERT INTO kbd VALUES (?, ?, ?, ?, ?)", event)
		k = k + 1
		if k > 10:
			conn.commit()
			k = 0
	out.close()

