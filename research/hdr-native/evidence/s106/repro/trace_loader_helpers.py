"""Static helper windows for dynamic bundle binding and output attachment roles."""
from pathlib import Path
C=Path(__file__).resolve().parent
source=(C/'trace_follow.py').read_text()
start=source.index('selected=[q for q in methods')
end=source.index('\ndef annotate(raw):',start)
queries=[
    ('loadSmartStyleBundle helper','0x1b05e1038'),
    ('attach output sample buffer helper','0x1b079494c'),
    ('CMSampleBuffer attachment lookup helper','0x1b06072d8'),
]
selected=[{'framework':'CMCapture','class':'capture-helper','selector':name,'IMP':address}for name,address in queries]
source=source[:start]+'selected='+repr(selected)+'\n'+source[end:]
source=source.replace("C/'follow'","C/'loader-helpers'").replace("C/'follow-manifest.json'","C/'loader-helpers-manifest.json'")
exec(compile(source,'same-selected-cache-window-reader-loader-helpers','exec'))
