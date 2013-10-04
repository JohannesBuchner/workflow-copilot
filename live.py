from kbd import kbd_event_feed
from mouse import mouse_velocity_feed
from analyse import analyse
import threadpool
from interact import startup, interrupt_user, check_news
import time

# mouse events & kbd events simultaneously

from threadpool import ThreadPool
def logger(v):
	print 'LOG:', v
pool = ThreadPool(max_threads=2, catch_returns=True, logger=logger)
print 'starting mouse pool ...'
pool(mouse_velocity_feed)(0.1)
print 'starting kbd pool ...'
pool(kbd_event_feed)()
print 'reading events...'

def insert_null_events(timeout=60):
	import time
	from Queue import Empty
	while pool.call_queue.unfinished_tasks > 0:
		try:
			yield pool.returns.get(timeout=timeout)
		except Empty:
			yield (time.time(),)

out = file('live.log', 'a')
lastactive = time.time()
lastcheck = time.time()
print 'STARTUP'
startup()
for k, v in analyse(insert_null_events(timeout=10)):
	# store
	out.write("%s: %s\n" % (k, v))
	out.flush()
	print k, v
	
	# put logic here:
	# if currently inactive period -- check emails every 10 minutes
	# so that we are up to date when he comes back
	# also check facebook
	inactive = lastactive - time.time() > 10 * 60 and lastcheck - time.time() > 10 * 60
	
	if (inactive and v) or 'switchtabs' in v:
		# good time to interrupt!
		print 'DECIDING to interrupt user'
		interrupt_user()
	elif inactive:
		print 'DECIDING to check news'
		check_news()
	
	if not v: # nothing happened
		pass
	else:
		lastactive = time.time()
	




