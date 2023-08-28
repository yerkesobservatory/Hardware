import os
from rich.console import Console
from rich.markdown import Markdown
console = Console()
fpath = r'C:\Users\NUC\OneDrive\Documents\GitHub\Hardware\GuiderAO\Maxim Scripting Interface\camstat_code.md'
print("BLASSSSSSSSSSSSSSSSSSSA")
print(fpath)
if os.path.exists(fpath):
    print("all good")
else:
    print("file missing")
#md = Markdown(f.read())
#with console.capture() as capture:
#    console.print(md)
lines = [l.strip() for l in open(fpath) if l[0] == '|']
tline = lines[0]
clines = lines[2:]
fstr = "%-15s  %-20s  %-52s"
ts = [t.strip() for t in tline.split('|') if len(t)]
print(ts)
print(fstr % (ts[0],ts[1],ts[2]))
for l in clines:
    cs = [t.strip() for t in l.split('|') if len(t)]
    print(fstr % (cs[0], cs[1], cs[2]) )
    
#print(capture.get())


print(1)