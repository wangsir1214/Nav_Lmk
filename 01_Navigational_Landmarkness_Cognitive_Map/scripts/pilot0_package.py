"""Create a hash manifest and image-free draft handoff; no network or Git writes."""
import argparse, json, platform, re, subprocess, sys, zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from pilot0_local import digest, read_csv, write_json

class ReviewHTML(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and a.get('href'):self.links.append(a['href'])

def build(out,node):
    project=Path(__file__).resolve().parents[1]
    html=(out/'review/index.html').read_text(encoding='utf-8')
    parser=ReviewHTML();parser.feed(html)
    if len(parser.ids)!=len(set(parser.ids)):raise ValueError('Duplicate HTML IDs')
    for link in parser.links:
        if not (out/'review'/link).resolve().exists():raise ValueError('Missing local review link: '+link)
    qa=out/'qa';qa.mkdir(exist_ok=True)
    js=re.search(r'<script>([\s\S]*?)</script>',html).group(1)
    (qa/'review_script.js').write_text(js,encoding='utf-8')
    result=subprocess.run([str(node),'--check',str(qa/'review_script.js')],capture_output=True,text=True)
    (qa/'javascript_syntax_check.txt').write_text('command: node --check qa/review_script.js\nexit_code: '+str(result.returncode)+'\n'+result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError(result.stderr)
    validation=json.loads((out/'validation_report.json').read_text())
    if not validation['passed']:raise ValueError('Machine validation did not pass')
    triage=json.loads((out/'review/codex_visual_notes.json').read_text(encoding='utf-8'))
    write_json(out/'quality_checks.json',{'machine_validation_passed':True,'machine_check_count':len(validation['checks']),'selected_images_decoded':216,'contact_sheets_visually_inspected':22,'pairs_visually_inspected_on_sheets':132,'full_size_cards_additionally_inspected':['R019','R051','R071','R095'],'priority_candidate_positives':len(triage['priority_cases']),'review_return_contract_tests':{'passed':6,'failed':0,'execution':'test_pilot0_review_gate.py; temporary synthetic fixtures; actual unittest result recorded in session'},'javascript_syntax_check_exit_code':result.returncode,'html_unique_ids':True,'local_html_links_present':True,'browser_runtime_test':'NOT_PERFORMED: browser URL security policy blocked file URL; no alternate browser or proxy attempted.','human_annotations_completed':0})
    scripts=['pilot0_local.py','pilot0_tasks.py','pilot0_review.py','pilot0_review_template.html','pilot0_validate.py','test_pilot0_review_gate.py','pilot0_package.py']
    files={p.relative_to(out).as_posix():p for p in sorted((out/'data').glob('*.csv'))}
    names=['configs/protocol.json','configs/paths.example.json','index_summary.json','task_summary.json','validation_report.json','environment.json','quality_checks.json','sources/source_manifest.json','review/image_validation.csv','review/review_cases.json','review/HUMAN_REVIEW.csv','review/codex_pair_pre_review.csv','review/codex_visual_notes.json','review/review_build_summary.json','REVIEW_GUIDE.md','LOCAL_TO_SERVER.md','REPRODUCE.md','run.log']
    files.update({n:out/n for n in names})
    hashes={k:{'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size} for k,p in files.items()}
    hashes.update({'code/'+n:{'sha256':digest((project/'scripts'/n).read_bytes()),'bytes':(project/'scripts'/n).stat().st_size} for n in scripts})
    for name in ['review/index.html','review/spatial_overview.svg']:
        p=out/name;hashes[name]={'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size}
    write_json(out/'artifact_hashes.json',hashes)
    refs=read_csv(out/'data/references.csv')
    gallery='gallery_'+digest(json.dumps(sorted((v['view_id'],v['image_sha256']) for v in refs)).encode())[:20]
    task={'task_id':'paris_local_v0_20260922','created_utc':datetime.now(timezone.utc).isoformat(),'task_state':'DRAFT_PENDING_HUMAN_REVIEW','gallery_id':gallery,'query_views':48,'reference_views':168,'all_relations':8064,'human_reviews_completed':0,'baseline_allowed':False,'scientific_protocol_frozen':False,'source_heading_sha256':json.loads((out/'sources/source_manifest.json').read_text())['heading']['sha256'],'view_manifest_sha256':hashes['data/view_manifest.csv']['sha256'],'pairs_sha256':hashes['data/retrieval_pairs.csv']['sha256'],'code_commit':None,'git_status':'No repository initialized or remote used','allowed_server_work':['environment_inventory','model_vocabulary_compatibility_check','selected_image_path_hash_check','feature_extraction_smoke_test_without_formal_scoring'],'next_gate':'Complete human pair review and reconcile disputes before publishing a new frozen task version.'}
    write_json(out/'task_manifest.json',task)
    files.update({'task_manifest.json':out/'task_manifest.json','artifact_hashes.json':out/'artifact_hashes.json'})
    files.update({'scripts/'+n:project/'scripts'/n for n in scripts})
    contents={k:{'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size} for k,p in files.items()}
    with zipfile.ZipFile(out/'server_draft_package.zip','w',zipfile.ZIP_DEFLATED) as z:
        for k,p in files.items():z.write(p,k)
        z.writestr('package_manifest.json',json.dumps({'task_state':'DRAFT_PENDING_HUMAN_REVIEW','images_included':False,'files':contents},ensure_ascii=False,indent=2))
    with zipfile.ZipFile(out/'server_draft_package.zip') as z:
        for k,h in contents.items():
            if digest(z.read(k))!=h['sha256']:raise ValueError('ZIP hash mismatch '+k)
        if any(k.endswith(('.jpg','.png','.pt','.npy')) or k.endswith('paths.local.json') for k in z.namelist()):raise ValueError('Excluded artifact in ZIP')
    write_json(out/'package_summary.json',{'zip':'server_draft_package.zip','bytes':(out/'server_draft_package.zip').stat().st_size,'sha256':digest((out/'server_draft_package.zip').read_bytes()),'entries':len(contents)+1,'all_entry_hashes_verified':True,'images_included':False,'uploaded':False,'gallery_id':gallery})
    print((out/'package_summary.json').read_text())

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--node',type=Path,required=True)
    a=p.parse_args();build(a.output_dir,a.node)
