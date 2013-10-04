
def analyse_keyboard_event(d, event, prev):
	time, msctype, msccode, keytype, keycode = event
	if keycode == 56:
		d['alt'] = True
	elif keycode == 15:
		d['tab'] = True
	elif keycode == 29 or keycode == 97:
		d['ctrl'] = True
	elif keycode == 57:
		d['space'] = True
	elif keycode == 54 or keycode == 42:
		d['shift'] = True
	elif keycode == 164 or keycode == 114 or keycode == 115:
		d['music'] = True
	elif keycode == 103 or keycode == 104 or keycode == 105 or keycode == 106 or keycode == 108 or keycode == 109:
		d['scrolling'] = True
	elif keycode < 57:
		d['typing'] = d.get('typing', 0) + 1
	else:
		print 'other unclassified keyboard event', time, keycode
	if prev is not None and (time - prev[0] < 1):
		prevkey = prev[4]
		if (prevkey, keycode) == (29, 46) or (prevkey, keycode) == (44, 46):
			d['jobcontrol'] = True
		#elif (prevkey, keycode) == (29, 46): # Ctrl-C is ambiguous
		#	d['jobcontrol'] = True
		elif (prevkey, keycode) == (56, 105):
			d['browseback'] = True
		elif (prevkey, keycode) == (56, 15):
			d['switchwindows'] = True
		elif (prevkey, keycode) == (29, 15) or (prevkey, keycode) == (29, 20): # Ctrl-Tab or Ctrl-T
			d['switchtabs'] = True
		elif (prevkey == 54 or prevkey == 42) and (keycode == 105) or (keycode == 106):
			d['switchconsoletabs'] = True
		elif (prevkey, keycode) == (29, 45) or (prevkey, keycode) == (29, 47): # (prevkey, keycode) == (29, 46) or 
			d['copypaste'] = True
	return d

def analyse_mouse_event(d, event):
	time, dist = event
	d['mouse'] = d.get('mouse', 0) + dist
	return d

def analyse(inputiter):
	prevkey = None
	lastkey = None
	lastdict = {}
	for event in inputiter:
		time = event[0]
		k = int(time / 5) * 5
		d = lastdict if k == lastkey else {}
		if len(event) == 5: # keyboard
			d = analyse_keyboard_event(d, event, prevkey)
			prevkey = event
		elif len(event) == 2: # mouse
			d = analyse_mouse_event(d, event)
		elif len(event) == 1: # nothing happened
			pass
		else:
			assert False, ('unknown type of event', event)
		if k != lastkey and lastkey != None:
			yield (lastkey, lastdict)
		lastdict = d
		lastkey = k

def plot_analysis(keys, times):
	attributes = ['jobcontrol', 'browseback', 'scrolling', 'typing', 'music', 'switchwindows', 'switchtabs', 'switchconsoletabs', 'copypaste']
	colors = ['r', 'g', 'b', 'o', 'k', 'y', 'm'] * 100
	x = range(len(attributes))
	plot_attributes = dict([(a, dict(color=c, pos=xi)) for a, c, xi in zip(attributes, colors, x)])

	figures = set()
	import matplotlib.pyplot as plt
	import time
	import random
	rng = random.Random()
	from math import log10, ceil, floor

	for k in keys:
		lt = time.localtime(k)
		figname = '%04d-%03d' % (lt.tm_year, lt.tm_yday)
		figures.add(figname)
		plt.figure(figname, figsize=(15,5*4))
		plt.subplot(4, 1, int(lt.tm_hour * 4 / 24) + 1)
	
		r = rng.normalvariate(0, 0.2)
		for attr, val in times[k].iteritems():
			if attr == 'typing':
				plt.plot(lt.tm_hour * 60 + lt.tm_min + lt.tm_sec / 60., -1 + r, '.', ms=4*log10(val), color='k')
			elif attr == 'mouse':
				plt.plot(lt.tm_hour * 60 + lt.tm_min + lt.tm_sec / 60., -2 + r, '.', ms=2*log10(val), color='y')
			elif attr in plot_attributes and val == True:
				plotattr = plot_attributes[attr]
				plt.plot(lt.tm_hour * 60 + lt.tm_min + lt.tm_sec / 60., plotattr['pos'] + r, '.', ms=4, color=plotattr['color'])
		plt.plot(lt.tm_hour * 60 + lt.tm_min + lt.tm_sec / 60., len(attributes), '.', ms=1, color='grey', alpha=0.2)
		#print k, times[k]

	for figname in figures:
		plt.figure(figname)
		for i in range(4):
			plt.subplot(4, 1, i + 1)
			if i == 0:
				plt.title(figname)
			xlo, xhi = plt.xlim()
			#hlo = int(floor(xlo / 15))
			#hhi = int(floor(xhi / 15 + 1))
			hlo, hhi = i * 6 * 60, (i + 1) * 6 * 60
			hticks = range(hlo, hhi + 1, 15)
			plt.xticks(hticks, ['%d.%d' % (int(h / 60), int((h % 60) / 15)) for h in hticks])
			plt.xlim(hlo, hhi)
			plt.yticks([-2, -1] + x, ['mouse', 'typing'] + attributes)
			plt.ylim(-3, len(attributes))
		plt.xlabel('hour of the day')
		plt.savefig(figname + '.pdf', bbox_inches='tight')
		plt.close()

if __name__ == '__main__':
	import sys
	infile = sys.argv[1]
	if infile.endswith('.db'):
		kbdfile = infile
		import sqlite3
		conn = sqlite3.connect(kbdfile)
		curs = conn.cursor()

		curs.execute('select * from kbd')

		table = curs.fetchall()

		ret = analyse(table)
		times = [(k, v) for k, v in ret] # iterate it out
		keys = [k for k, v in times]
		times = dict(times)
		plot_analysis(keys, times)
	else:
		import ast
		keys = []
		times = {}
		for line in open(infile):
			try:
				i = line.index(':')
				k, val = line[:i], line[i+1:].strip()
				time = float(k)
				val = ast.literal_eval(val)
				keys.append(time)
				times[time] = val
			except Exception as e:
				print 'WARNING: could not parse line:'
				print '<<', line[:-1]
				print '::', e
		print 'parsing complete. plotting...'
		plot_analysis(keys, times)
			
				


