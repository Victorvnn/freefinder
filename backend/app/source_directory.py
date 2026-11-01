"""Discovery links are metadata only: never scan or turn these entries into offers."""
import json
from pathlib import Path

PUBLIC_SOURCE_FIELDS={'id','name','enabled','minimum_hours','policy_url','policy_note','policy_reviewed','url','mode','categories','notes'}
MODES={'automated','manual','invitation','permission_required'}

def merge_directory(sources):
    """Project scanner configurations into a safe directory, preserving real source IDs."""
    directory=json.loads(Path(__file__).with_name('source_directory.json').read_text(encoding='utf-8'))
    result=[]
    seen=set()
    for raw in list(sources)+directory:
        if raw['id'] in seen:continue
        seen.add(raw['id'])
        source={k:v for k,v in raw.items() if k in PUBLIC_SOURCE_FIELDS}
        source.setdefault('url',next(iter(raw.get('seeds',[])),raw.get('policy_url','')))
        source.setdefault('mode','automated' if raw.get('enabled') else 'permission_required')
        source.setdefault('categories',[])
        if source['mode'] not in MODES:raise ValueError('Unknown source access mode')
        # Reuse the catalog's strict credential/query/fragment export rules.
        from .cloud import public_url
        for key in ('url','policy_url'):
            if source.get(key):source[key]=public_url(source[key])
        result.append(source)
    return result
