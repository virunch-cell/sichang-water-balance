"""Runs run_all.py in stages (each below 3 minutes). Usage: python3 run_all_staged.py new A|B|C
A = preamble (Tables 6-8, design catchments) + Table 9 (analytic); B = preamble + Table 10; C = preamble + Table 11 + extras.
The Fig. 8 frontier loop of run_all.py is skipped here: fig8_frontier.py computes it (nine storages)."""
import sys
src=open('run_all.py').read().split('\n')
st=sys.argv.pop(2)
i0=next(i for i,l in enumerate(src) if l.startswith('if not REST: P("Fig8'))
i1=next(i for i,l in enumerate(src) if l.startswith('P("T9 deficit'))
i2=next(i for i,l in enumerate(src) if l.startswith('P("T10 robust'))
i3=next(i for i,l in enumerate(src) if l.startswith('P("T11'))
pre=src[:i0]; sec={'A':src[i1:i2],'B':src[i2:i3],'C':src[i3:]}[st]
if st!='A': pre=[l for l in pre if not l.startswith('P("T8') ]  # same
exec('\n'.join(pre+['QUIET=False']+sec))
