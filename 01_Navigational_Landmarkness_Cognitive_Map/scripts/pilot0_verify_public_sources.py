"""Download only small public source text; do not execute remote code or fetch weights."""
import argparse, json, urllib.request
from pathlib import Path
from pilot0_local import digest, write_json

def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Pilot0-source-verification','Accept':'application/vnd.github+json' if 'api.github.com' in url else 'text/plain'})
    with urllib.request.urlopen(req,timeout=25) as r:return r.read()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    sources=[]
    for repo,files in [('AnyLoc/AnyLoc',['demo/README.md','demo/anyloc_vlad_generate.py','utilities.py']),('facebookresearch/dinov2',['dinov2/hub/backbones.py','dinov2/models/vision_transformer.py'])]:
        try:
            revision=json.loads(get('https://api.github.com/repos/'+repo+'/commits/main'))['sha']
        except Exception as e:
            sources.append({'repo':repo,'error':str(e)});continue
        for name in files:
            url='https://raw.githubusercontent.com/'+repo+'/'+revision+'/'+name
            try:
                raw=get(url);dest=a.output_dir/(repo.replace('/','_')+'__'+name.replace('/','_'));dest.write_bytes(raw)
                sources.append({'repo':repo,'revision':revision,'url':url,'local_file':dest.name,'sha256':digest(raw),'bytes':len(raw),'executed':False})
            except Exception as e:sources.append({'url':url,'error':str(e)})
    write_json(a.output_dir/'source_manifest.json',sources)
    print(json.dumps(sources,indent=2))
