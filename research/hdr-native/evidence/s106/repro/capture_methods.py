"""Use the same calibrated parser on capture owners and selected camera control."""
from pathlib import Path
C=Path(__file__).resolve().parent
source=(C/'objc_locate.py').read_text()
changes=[
    ("images=json.loads((C/'locators.json').read_text())['images']", "images=[x for x in json.loads((C/'locators.json').read_text())['images']if x['framework']=='CameraColorProcessing']+json.loads((C/'capture-locators.json').read_text())['images']"),
    ("'linearthumbnail'in name.lower()or", "('linearthumbnail'in name.lower()or'faceboost'in name.lower())or"),
    ("C/'objc-locators.json'", "C/'capture-objc-locators.json'")
]
for a,b in changes:
    assert source.count(a)==1
    source=source.replace(a,b)
exec(compile(source,'same-calibrated-parser-capture-modules','exec'))
