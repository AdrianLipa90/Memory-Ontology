"""Selective CLX2 episode intake into the existing MAHAL journal, not a new store."""
import json, math, sys
from operation_memory import store_path, MemoryStore
ADDRESS='DYNAMIC_STATE_SPACE/AFFECTIVE_MEMORY'
PREFIX='MAHAL affective episode '
POLICY='NOEMA_AFFECTIVE_AUTOSAVE_V1'
AKEYS=('valence','arousal','urgency','threat_relevance','attachment_relevance','reward_relevance')
FIELDS={'event_id':140,'source_ref':512,'session_id':160,'title':180,'summary':800}

def read_affective_memory(limit=20):
    if type(limit)!=int or not 1<=limit<=100: raise ValueError('limit')
    path=store_path()
    if not path.is_file():return {'address':ADDRESS,'status':'EMPTY','events':[],'scope':'LOCAL_RUNTIME_STORE'}
    with MemoryStore(path) as mem: events=mem.recall(PREFIX,limit=limit)
    return {'address':ADDRESS,'status':'READ','events':events,'scope':'LOCAL_RUNTIME_STORE'}

def remember(event):
    allowed=set(FIELDS)|{'subject','confidence','intensity','distinct_lexical_cues','labels','affect'}
    if not isinstance(event,dict) or set(event)!=allowed:raise ValueError('bounded episode schema')
    for k,n in FIELDS.items():
        v=event[k]
        if not isinstance(v,str) or not v.strip() or len(v)>n:raise ValueError(k)
    if event['subject'] not in ('MODEL_OUTPUT','SIMULATED_EVENT'):raise ValueError('subject')
    for k in ('confidence','intensity'):
        if type(event[k]) not in (int,float) or not math.isfinite(event[k]) or not 0<=event[k]<=1:raise ValueError(k)
    c=event['distinct_lexical_cues']
    if type(c)!=int or c<0:raise ValueError('cue count')
    if not isinstance(event['labels'],list) or len(event['labels'])>8 or any(not isinstance(x,str) or not 1<=len(x)<=64 or any(y not in 'abcdefghijklmnopqrstuvwxyz-' for y in x) for x in event['labels']):raise ValueError('labels')
    a=event['affect']
    if not isinstance(a,dict) or set(a)!=set(AKEYS): raise ValueError('affect keys')
    for k,v in a.items():
        if type(v) not in (int,float) or not math.isfinite(v) or not (-1 if k=='valence' else 0)<=v<=1:raise ValueError('affect scalar')
    if abs(event['intensity']-max(abs(v) for v in a.values()))>1e-9:raise ValueError('inconsistent intensity')
    if event['confidence']<.45 or event['intensity']<.60:return {'status':'IGNORED_EPHEMERAL','persistent_write':False}
    desc={k:event[k] for k in ('subject','confidence','intensity','distinct_lexical_cues','labels','affect')}
    desc.update(policy=POLICY,method='CLX2 lexical interpretation',phenomenal_affect_measured=False)
    value={'event_id':'affective:'+event['event_id'],'kind':'operation','title':PREFIX+event['title'],
           'summary':event['summary']+'; reader interpretation: '+json.dumps(desc,sort_keys=True,ensure_ascii=False),
           'importance':event['intensity'],'source_ref':event['source_ref'],'pin':False,
           'tags':['NOEMA_MAHAL','M10','AFFECTIVE_EPISODE','INTERPRETATION_NOT_MEASUREMENT'],
           'context':{'session_id':event['session_id'],'topic':'MAHAL affective memory'}}
    with MemoryStore(store_path()) as mem:
        receipt=mem.remember(value,threshold=.60)
        saved=mem.get_event(receipt['event_id'])
        if saved is None or saved['cid']!=receipt['cid']:raise RuntimeError('event readback mismatch')
    return {'address':ADDRESS,**receipt,'readback':'VERIFIED','scope':'LOCAL_RUNTIME_STORE','dynamic_aux_archived':False}

def dispatch(value):
    if value.get('op')=='remember':return remember(value['event'])
    if value.get('op')=='recall':return read_affective_memory(value.get('limit',20))
    raise ValueError('unknown operation')

if __name__=='__main__':
    try:print(json.dumps(dispatch(json.load(sys.stdin)),ensure_ascii=False,allow_nan=False))
    except Exception as exc:
        print(json.dumps({'status':'UNVERIFIED','error_type':type(exc).__name__}));sys.exit(1)
