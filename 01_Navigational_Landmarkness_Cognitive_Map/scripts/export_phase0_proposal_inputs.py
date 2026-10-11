"""Export only query ID, source filename and hash from frozen selection."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'outputs/pilot0/phase0_intervention_prep_20261011'
selection=json.loads((PACKAGE/'selection_manifest.json').read_text(encoding='utf-8'))
expected={'query_view_id','image_relative_path','image_sha256'}
entries=[{k:q[k] for k in ('query_view_id','image_relative_path','image_sha256')}
         for q in selection['queries']]
assert len(entries)==20 and len({q['query_view_id'] for q in entries})==20
assert all(set(q)==expected for q in entries)
path=PACKAGE/'proposal_input_only.json'
payload={'package_id':selection['package_id'],'query_count':len(entries),'queries':entries}
if path.exists() and json.loads(path.read_text(encoding='utf-8'))!=payload:
    raise FileExistsError('Existing proposal-only inputs differ')
path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(path)
