import sys
f = sys.argv[1]
with open(f, 'r') as fh:
    lines = fh.readlines()
lines = ['edit ' + l[5:] if l.startswith('pick 4708528') else l for l in lines]
with open(f, 'w') as fh:
    fh.writelines(lines)
