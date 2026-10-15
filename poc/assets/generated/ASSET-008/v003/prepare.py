#!/usr/bin/env python3
"""ASSET-008 revision2: replace Fighting/Ground only; run from repository root."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path('poc/assets/generated/_tools').resolve()))
from prepare_samples import source_cell,fit,fixed_palette,report_image,GREYS
OUT=Path(__file__).parent
cfg=json.loads((OUT/'processing.json').read_text());ops=[]
base=Image.open(cfg['base']).convert('RGBA');before=np.asarray(base).copy()
for item in cfg['replacements']:
 im=source_cell({'input':str(OUT/'raw/symbols.png'),'crop':item['crop'],'trim_alpha':True},{'minimum_component_pixels':64,'alpha_threshold':128},ops)
 im=fit(im,(32,32),ops,margin=2);im,_=fixed_palette(im,GREYS)
 base.paste(im,(item['index']*40,0));im.save(OUT/(item['name']+'.png'))
base.save(OUT/'type_symbols.png');base.resize((base.width*4,128),Image.Resampling.NEAREST).save(OUT/'type_symbols_review_4x.png');base.resize((base.width//2,16),Image.Resampling.NEAREST).save(OUT/'type_symbols_review_half.png')
a=np.asarray(base);checks={}
for n in range(17):
 equal=bool(np.array_equal(before[:,n*40:n*40+32],a[:,n*40:n*40+32]));checks[str(n)]={'unchanged_from_v002':equal,'expected_unchanged':n not in (1,4)}
r=report_image(OUT/'type_symbols.png',(672,32),max_colors=5,palette=GREYS,cells=(32,17))
validation={'sheet':r,'base_sha256':hashlib.sha256(Path(cfg['base']).read_bytes()).hexdigest(),'per_cell_checks':checks,'only_requested_cells_changed':all(x['unchanged_from_v002']==x['expected_unchanged'] for x in checks.values()),'unchanged_gaps':all(np.array_equal(before[:,n*40+32:(n+1)*40],a[:,n*40+32:(n+1)*40]) for n in range(16)),'operations':ops,'runtime_checked':False}
validation['all_passed']=r['passed'] and validation['only_requested_cells_changed'] and validation['unchanged_gaps']
(OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n');assert validation['all_passed'];print('Validated: exactly2 requested cells changed; other15 cells/gaps preserved.')
