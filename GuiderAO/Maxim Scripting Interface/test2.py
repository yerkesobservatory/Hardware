import os
from rich.console import Console
from rich.markdown import Markdown
console = Console()
fpath = r'C:\Users\NUC\OneDrive\Documents\GitHub\Hardware\GuiderAO\Maxim Scripting Interface\camstat_code.md'
with open(fpath) as f:

    md = Markdown(f.read())
    console.print(md)
