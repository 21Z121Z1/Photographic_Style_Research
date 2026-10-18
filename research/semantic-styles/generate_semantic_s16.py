"""Add a finite-domain semantic inverse audit; frozen consumers are read only."""
from pathlib import Path
import sys, json, hashlib
src = Path('research/semantic-styles/semantic_consumer_s5.m')
out = Path(sys.argv[1]); out.mkdir(exist_ok=True, parents=True)
text = src.read_text(); a = text.index('static void Probe('); b = text.index('static int Process(', a)
text = text[:a] + '#include "semantic_s16.inc"\n' + text[b:]
(out/'semantic_consumer_s16.m').write_text(text)
(out/'generated-sha256.json').write_text(json.dumps({
    'source': str(src), 'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
    'generated_sha256': hashlib.sha256(text.encode()).hexdigest(),
    'change': 'Only Probe replaced. Original PSO, all other textures/buffers/stats retained; theta9/10 alone neutralized. Finite local half boxes, not global certification.'
}, indent=2)+'\n')
