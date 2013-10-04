# FacebookFeedFetch for Notifications
# f4n
import feedparser
import subprocess
import StringIO
import json
import os, sys

jsonfile = 'fff.json'
old = {}
if os.path.exists(jsonfile):
	old = json.load(open(jsonfile))

for url in sys.argv[1:]:
	d = feedparser.parse(url)
	for i in d.entries:
		item = dict([(k, i[k]) for k in 'link,title,summary'.split(',')])
		if i['id'] not in old:
			args = ('notify-send', '-a', 'Facebook', 
				"""<b><a href="%(link)s">%(title)s</a></b><p>%(summary)s</p>""" % item)
			p = subprocess.Popen(args)
			if p.wait() != 0:
				print 'return value of startup script was non-zero'
				continue
		
			old[i['id']] = item
			# send libnotify stuff
			print 'notified about', item

json.dump(old, file(jsonfile, 'w'), indent=4)


