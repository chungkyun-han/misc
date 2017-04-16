import os

# extend = '.csv'
extend = '.pkl'

for fn in os.listdir("."):
	if not fn.endswith(extend):
		continue
	_, _, x = fn[:-len(extend)].split('-')
	new_fn = 'roamingTime-influenceGraph-2009-%s%s' % (x, extend)
	os.rename(fn, new_fn)
	print fn
