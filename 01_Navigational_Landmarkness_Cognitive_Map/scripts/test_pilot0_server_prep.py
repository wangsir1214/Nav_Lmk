"""CPU checks for identity, headings, provenance/resume and VLAD numerical behavior."""
import argparse
import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from zipfile import ZipFile
import numpy as np
from PIL import Image
from pilot0_prepare_weights import VLAD_RELEASE_BYTES, VLAD_RELEASE_SHA256, validate_release_asset
from pilot0_resize_views import check_rows, resize_image, run, sha
from pilot0_vlad import aggregate
from pilot0_score import evaluate, run as run_score


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'raw'; self.source.mkdir()
        self.rows = []
        for i in range(4):
            name = f'pano_with_under_score_panorama_{i}.jpg'
            yy, xx = np.mgrid[:640, :640]
            arr = np.stack(((xx+i*9)%256, yy%256, (xx+yy)%256), axis=-1).astype('uint8')
            Image.fromarray(arr).save(self.source/name, quality=93)
            self.rows.append({'pano_id':'pano_with_under_score','view_index':str(i),
                              'view_id':f'pano_with_under_score__v{i}',
                              'image_relative_path':name,'heading_from_api':'350.5',
                              'absolute_heading':str((350.5+90*i)%360),
                              'experiment_split':'dev','retrieval_role':'unused'})
        self.manifest = self.root/'views.csv'
        with self.manifest.open('w', newline='', encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(self.rows[0]));w.writeheader();w.writerows(self.rows)
        self.args=argparse.Namespace(source_dir=self.source,output_dir=self.root/'resized',
                                     manifest=self.manifest,task_dir=None,expected_count=4)

    def tearDown(self):
        self.temp.cleanup()

    def execute(self):
        with contextlib.redirect_stdout(io.StringIO()):
            run(self.args)

    def test_filename_and_heading_guards(self):
        check_rows(self.rows)
        broken=[dict(r) for r in self.rows];broken[1]['image_relative_path']='pano__v1.jpg'
        with self.assertRaises(ValueError):check_rows(broken)
        broken=[dict(r) for r in self.rows];broken[0]['absolute_heading']='0'
        with self.assertRaises(ValueError):check_rows(broken)

    def test_resize_resume_preserves_sources(self):
        hashes={p.name:sha(p.read_bytes()) for p in self.source.iterdir()}
        self.execute();self.execute()
        result=json.loads((self.args.output_dir/'_provenance/resize_summary.json').read_text())
        self.assertEqual(result['reused'],4);self.assertEqual(result['created'],0)
        self.assertEqual(hashes,{p.name:sha(p.read_bytes()) for p in self.source.iterdir()})
        for r in self.rows:
            png=self.args.output_dir/Path(r['image_relative_path']).with_suffix('.png')
            with Image.open(png) as im:
                self.assertEqual(im.size,(448,448));self.assertEqual(im.mode,'RGB')
                self.assertEqual(im.tobytes(),resize_image((self.source/r['image_relative_path']).read_bytes()).tobytes())

    def test_source_drift_rejected(self):
        self.execute()
        Image.new('RGB',(640,640),'red').save(self.source/self.rows[0]['image_relative_path'])
        with self.assertRaises(ValueError):self.execute()

    def test_output_drift_rejected(self):
        self.execute()
        dest=self.args.output_dir/Path(self.rows[0]['image_relative_path']).with_suffix('.png')
        Image.new('RGB',(448,448),'blue').save(dest)
        with self.assertRaises(ValueError):self.execute()

    def test_wrong_dimensions_rejected(self):
        data=io.BytesIO();Image.new('RGB',(639,640)).save(data,format='PNG')
        with self.assertRaises(ValueError):resize_image(data.getvalue())

    def test_pinned_official_vlad_release_asset(self):
        asset=Path(__file__).resolve().parents[1]/'outputs/pilot0/vlad_recovery_20260924/dinov2_vitg14_l31_value_c32_urban_c_centers.pt'
        if asset.exists():
            raw=asset.read_bytes()
            result=validate_release_asset(raw)
            self.assertEqual(len(raw),VLAD_RELEASE_BYTES)
            self.assertEqual(result['sha256'],VLAD_RELEASE_SHA256)
            with ZipFile(io.BytesIO(raw)) as archive:
                centers=np.frombuffer(archive.read('c_centers/data/0'),dtype='<f4').reshape(32,1536)
            self.assertTrue(np.isfinite(centers).all())
            self.assertTrue(np.all(np.linalg.norm(centers,axis=1)>0))
        with self.assertRaises(ValueError):validate_release_asset(b'not the release asset')

    def test_vlad_hand_computed_and_scaling(self):
        centers=np.array([[1.,0.],[0.,1.]],dtype=np.float32)
        # Assign first vector to center 0, second to center 1.
        patches=np.array([[.8,.6],[.6,.8]],dtype=np.float32)
        residual=np.array([[-.2,.6],[.6,-.2]],dtype=np.float32)
        expected=(residual/np.sqrt(.4)/np.sqrt(2)).reshape(-1)
        actual=aggregate(patches,centers)
        np.testing.assert_allclose(actual,expected,atol=1e-6)
        np.testing.assert_allclose(actual,aggregate(patches*7,centers),atol=1e-6)
        self.assertAlmostEqual(float(np.linalg.norm(actual)),1,places=6)

    def test_cosine_assignment_uses_raw_center_residuals(self):
        # Euclidean would choose center 1, cosine must choose center 0.
        out=aggregate([[1.,0.]],[[100.,0.],[.5,.5]])
        np.testing.assert_allclose(out,[-1.,0.,0.,0.],atol=1e-7)

    def test_invalid_vlad_input_rejected(self):
        for patches in ([[0.,0.]],[[float('nan'),1.]]):
                with self.assertRaises(ValueError):aggregate(patches,[[1.,0.]])

    def test_frozen_scoring_masks_ignore_and_uses_best_positive(self):
        q=[{'view_id':'q__v0','pano_id':'q','dev_group_id':'D01','area_id':'A'}]
        refs=[{'view_id':f'{x}__v0','pano_id':x,'dev_group_id':'D02','area_id':'B'} for x in ['p','p2','n','n2','i']]
        relations=[]
        for rid,rel,case in [('p__v0','positive',''),('p2__v0','positive','R125'),
                             ('n__v0','negative',''),('n2__v0','negative',''),('i__v0','ignore','')]:
            relations.append({'query_view_id':'q__v0','reference_view_id':rid,'relation':rel,
                              'scoring_allowed':str(rel!='ignore'),'review_case_id':case,
                              'distance_m':'12','heading_diff_deg':'5','reference_dev_group_id':'D02'})
        f={'q__v0':np.array([1,0],np.float32),'p__v0':np.array([.8,.6],np.float32),
           'p2__v0':np.array([.7,np.sqrt(.51)],np.float32),'n__v0':np.array([.9,np.sqrt(.19)],np.float32),
           'n2__v0':np.array([0,1],np.float32),'i__v0':np.array([1,0],np.float32)}
        main=evaluate(q,refs,relations,f)
        row=main[0][0]
        self.assertEqual(row['best_positive_rank'],2)
        self.assertEqual(row['recall_at_1'],0);self.assertEqual(row['recall_at_5'],1)
        self.assertAlmostEqual(float(row['margin']),-.1,places=6)
        self.assertNotIn('i__v0',[x['reference_view_id'] for x in main[2][0]['ranked_scoring_gallery']])
        conservative=evaluate(q,refs,relations,f,exclude_exceptions=True)
        self.assertEqual(conservative[0][0]['positive_count'],1)

    def test_scoring_run_validates_hashes_and_writes_baseline(self):
        task=self.root/'task'; feature=self.root/'features'; out=self.root/'results'
        (task/'data').mkdir(parents=True); feature.mkdir()
        task_id='paris_local_v1_20260923'
        request_id='full_image_g14_l31_value_c32_urban_448png_fp32_v2'
        (task/'task_manifest.json').write_text(json.dumps({'task_id':task_id}),encoding='utf-8')
        (feature/'run_config.json').write_text(json.dumps({'request':{'task_id':task_id,'request_id':request_id}}),encoding='utf-8')
        queries=[{'view_id':'q__v0','pano_id':'q','dev_group_id':'D01','area_id':'A'}]
        refs=[{'view_id':'p__v0','pano_id':'p','dev_group_id':'D02','area_id':'B'},
              {'view_id':'n__v0','pano_id':'n','dev_group_id':'D03','area_id':'C'}]
        pairs=[{'query_view_id':'q__v0','reference_view_id':'p__v0','relation':'positive','review_case_id':''},
               {'query_view_id':'q__v0','reference_view_id':'n__v0','relation':'negative','review_case_id':''}]
        for name,rows in [('queries.csv',queries),('references.csv',refs),('retrieval_pairs.csv',pairs)]:
            with (task/'data'/name).open('w',encoding='utf-8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        vectors={'q__v0':np.eye(1,49152,0,dtype=np.float32)[0],
                 'p__v0':np.eye(1,49152,0,dtype=np.float32)[0],
                 'n__v0':np.eye(1,49152,1,dtype=np.float32)[0]}
        rows=[]
        for view_id,vec in vectors.items():
            path=feature/f'{view_id}.npy';np.save(path,vec,allow_pickle=False)
            rows.append({'view_id':view_id,'vlad_path':str(path),'vlad_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        with (feature/'feature_index.csv').open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        (feature/'run_config.json').write_text(json.dumps({'request':{'task_id':task_id,'request_id':request_id},
            'feature_index_sha256':hashlib.sha256((feature/'feature_index.csv').read_bytes()).hexdigest()}),encoding='utf-8')
        run_score(SimpleNamespace(task_dir=task,feature_dir=feature,output=out))
        summary=json.loads((out/'baseline_summary.json').read_text(encoding='utf-8'))
        self.assertEqual(summary['n_queries'],1)
        self.assertEqual(summary['success_count']['recall_at_1'],1)
        self.assertTrue((out/'result_manifest.json').is_file())


if __name__=='__main__':
    unittest.main(verbosity=2)
