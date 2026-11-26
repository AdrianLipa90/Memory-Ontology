"""Event-first PNAML memory, AUX input strictly read-only.

No network, no continuous AUX persistence, no writes to NOEMA canonical state.
SQLite WAL+FULL transaction commits for selected memories. Source code and
runtime state may be hosted independently of CIELPC/NOEMA.
"""
from __future__ import annotations

from datetime import date, datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import math
import os
import sqlite3
import stat
from typing import Any

SCHEMA = 'PNAML_CONTINUITY_EVENT_JOURNAL_V1'
IMPORTANT_KINDS = frozenset({
    'discovery', 'decision', 'correction', 'contradiction', 'commitment',
    'identity', 'relationship', 'test_result', 'failure', 'milestone',
    'safety', 'memory_revision'
})
EVENT_KEYS = frozenset({
    'event_id','kind','title','summary','importance','source_ref','tags',
    'relations','context','aux_link','pin','occurred_at'
})
CONTEXT_KEYS = frozenset({'session_id','topic','branch_id','object_id','concept_id'})
AUX_LINK_KEYS = frozenset({'source_id','generation','tick','fingerprint_sha256'})
RELATION_KEYS = frozenset({'source','type','target','status'})
RAW_AUX_KEYS = frozenset({
    'phi','phi36','omega','omega36','aux_raw','aux_state','aux_payload',
    'raw_aux','aux_samples','aux_stream','phase_samples','waveform',
    'iq_samples','trits12','q36_lifted_turns'
})


class MemoryErrorStatus(ValueError):
    """Invalid event, unsupported provenance, or continuity integrity failure."""


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(domain: str, obj: Any) -> str:
    return hashlib.sha256(domain.encode('ascii') + b'\0' + canonical(obj)).hexdigest()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec='microseconds').replace('+00:00','Z')


def require_text(value: Any, label: str, limit: int = 10000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise MemoryErrorStatus(f'{label} must be nonempty text (max {limit})')
    return value.strip()


def forbid_unknown(obj: dict, allowed: frozenset, label: str) -> None:
    disallowed = sorted(set(obj) - allowed)
    if disallowed:
        raise MemoryErrorStatus(f'{label} contains prohibited/unknown fields: {disallowed}')


def normalize_event(event: dict) -> dict:
    """Allowlist serialization boundary; never accept raw AUX state or traces."""
    if not isinstance(event, dict):
        raise MemoryErrorStatus('event must be an object')
    forbid_unknown(event, EVENT_KEYS, 'event')
    event_id = require_text(event.get('event_id'), 'event_id', 160)
    kind = require_text(event.get('kind'), 'kind', 64).lower()
    title = require_text(event.get('title'), 'title', 320)
    summary = require_text(event.get('summary'), 'summary', 12000)
    source_ref = require_text(event.get('source_ref'), 'source_ref', 1024)
    importance = event.get('importance', 0.0)
    if isinstance(importance, bool) or not isinstance(importance, (int,float)) or not math.isfinite(importance) or not 0 <= importance <= 1:
        raise MemoryErrorStatus('importance must be finite in [0,1]')
    pin = event.get('pin', False)
    if not isinstance(pin, bool):
        raise MemoryErrorStatus('pin must be boolean')
    tags = event.get('tags', [])
    if not isinstance(tags,list) or len(tags)>32 or any(not isinstance(t,str) or not t.strip() or len(t)>100 for t in tags):
        raise MemoryErrorStatus('tags must be <=32 nonempty labels')
    context = event.get('context', {})
    if not isinstance(context,dict):
        raise MemoryErrorStatus('context must be an object')
    forbid_unknown(context, CONTEXT_KEYS, 'context')
    for key, val in context.items():
        require_text(val, 'context.'+key, 300)
    relations = event.get('relations', [])
    if not isinstance(relations,list) or len(relations)>64:
        raise MemoryErrorStatus('relations must contain <=64 typed edges')
    validated_relations=[]
    for i, rel in enumerate(relations):
        if not isinstance(rel,dict):
            raise MemoryErrorStatus(f'relations[{i}] must be an object')
        forbid_unknown(rel, RELATION_KEYS, f'relations[{i}]')
        validated_relations.append({key:require_text(rel.get(key),f'relations[{i}].{key}',512)
                                    for key in ('source','type','target','status')})
    aux_link = event.get('aux_link', None)
    if aux_link is not None:
        if not isinstance(aux_link,dict):
            raise MemoryErrorStatus('aux_link must be an object')
        forbid_unknown(aux_link, AUX_LINK_KEYS, 'aux_link')
        if not {'source_id','fingerprint_sha256'} <= set(aux_link):
            raise MemoryErrorStatus('aux_link requires source_id and fingerprint_sha256')
        fp = require_text(aux_link['fingerprint_sha256'],'fingerprint_sha256',64)
        if len(fp)!=64 or any(c not in '0123456789abcdef' for c in fp):
            raise MemoryErrorStatus('fingerprint_sha256 must be lowercase SHA-256 hex')
        fixed = {'source_id':require_text(aux_link['source_id'],'aux_link.source_id',240),
                 'fingerprint_sha256':fp}
        for field in ('generation','tick'):
            if field in aux_link:
                v = aux_link[field]
                if field=='tick' and (not isinstance(v,int) or isinstance(v,bool) or v<0):
                    raise MemoryErrorStatus('tick must be nonnegative integer')
                if field=='generation': v=require_text(v,'generation',160)
                fixed[field]=v
        aux_link=fixed
    occurred_at = event.get('occurred_at', None)
    if occurred_at is not None:
        t=require_text(occurred_at,'occurred_at',50)
        try:
            parsed=datetime.fromisoformat(t.replace('Z','+00:00'))
            if parsed.tzinfo is None: raise ValueError('missing UTC offset')
            occurred_at=iso_utc(parsed)
        except ValueError as exc:
            raise MemoryErrorStatus('occurred_at must be offset-aware ISO8601') from exc
    return {
        'event_id':event_id,'kind':kind,'title':title,'summary':summary,
        'importance':float(importance),'source_ref':source_ref,
        'tags':sorted(set(t.strip() for t in tags)),
        'relations':validated_relations,'context':{k:context[k].strip() for k in sorted(context)},
        'aux_link':aux_link,'pin':pin,'occurred_at':occurred_at
    }


def shard_specs(event: dict, committed_at: str) -> list[tuple[str,dict]]:
    result = [
        ('semantic', {'title':event['title'],'summary':event['summary'],'tags':event['tags']}),
        ('temporal', {'committed_at':committed_at,'occurred_at':event['occurred_at'],
                      'session_id':event['context'].get('session_id')}),
        ('provenance', {'source_ref':event['source_ref']}),
        ('salience', {'importance':event['importance'],'kind':event['kind']})
    ]
    if event['context']:
        result.append(('context',event['context']))
    if event['aux_link']:
        result.append(('aux_reference',event['aux_link']))
    result.extend(('typed_relation',rel) for rel in event['relations'])
    return result


def validate_metrics_snapshot(metrics: dict) -> dict:
    """Strict daily aggregate schema: reject arbitrary sample arrays/telemetry."""
    if not isinstance(metrics,dict):
        raise MemoryErrorStatus('daily metrics must be a JSON object')
    allowed={'status','sample_count','aux_raw_persisted','metrics'}
    if set(metrics)-allowed:
        raise MemoryErrorStatus('daily metrics contain unsupported fields; only aggregates allowed')
    status=metrics.get('status')
    if status not in ('OBSERVED_AGGREGATES','NOT_MEASURED'):
        raise MemoryErrorStatus('invalid daily metrics status')
    count=metrics.get('sample_count')
    if isinstance(count,bool) or not isinstance(count,int) or count<0:
        raise MemoryErrorStatus('sample_count must be nonnegative integer')
    if 'aux_raw_persisted' in metrics and metrics['aux_raw_persisted'] is not False:
        raise MemoryErrorStatus('raw AUX storage is prohibited')
    if status=='NOT_MEASURED' and count!=0:
        raise MemoryErrorStatus('NOT_MEASURED cannot have samples')
    if status=='OBSERVED_AGGREGATES' and count<=0:
        raise MemoryErrorStatus('OBSERVED_AGGREGATES requires samples')
    stats=metrics.get('metrics',{})
    if not isinstance(stats,dict) or set(stats)-{'r36','phase_dispersion','omega_mean','omega_abs_max'}:
        raise MemoryErrorStatus('invalid metric names; no raw AUX fields permitted')
    if count>0 and not stats:
        raise MemoryErrorStatus('observed metrics need aggregates')
    fixed={}
    for name,summary in stats.items():
        if not isinstance(summary,dict) or set(summary)!={'samples','min','max','mean','stddev'}:
            raise MemoryErrorStatus('metric aggregate fields invalid')
        n=summary['samples']
        if isinstance(n,bool) or not isinstance(n,int) or n<0 or n>count:
            raise MemoryErrorStatus('metric sample count invalid')
        clean={'samples':n}
        for key in ('min','max','mean','stddev'):
            val=summary[key]
            if val is None:
                if n:raise MemoryErrorStatus('missing numeric metric aggregate')
            elif isinstance(val,bool) or not isinstance(val,(int,float)) or not math.isfinite(val):
                raise MemoryErrorStatus('nonfinite or invalid metric aggregate')
            elif n==0:
                raise MemoryErrorStatus('unexpected metric for zero samples')
            clean[key]=float(val) if val is not None else None
        if n and (clean['min']>clean['max'] or clean['stddev']<0 or
                  not clean['min']-1e-8 <=clean['mean']<=clean['max']+1e-8):
            raise MemoryErrorStatus('inconsistent metric summary')
        fixed[name]=clean
    return {'status':status,'sample_count':count,'aux_raw_persisted':False,'metrics':fixed}


class MemoryStore:
    """One writer per SQLite transaction; concurrent clients are safe via IMMEDIATE."""
    def __init__(self, path: str | Path):
        self.path=Path(path).expanduser()
        live_root=Path('/dev/shm/ciel_noema').resolve()
        resolved=self.path.resolve()
        if os.path.commonpath([str(live_root),str(resolved)])==str(live_root):
            raise MemoryErrorStatus('persistent memory DB must not be written into volatile NOEMA/AUX source')
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(str(self.path), timeout=15, isolation_level=None)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS shards(
            cid TEXT PRIMARY KEY, kind TEXT NOT NULL,
            payload_json TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events(
            seq INTEGER PRIMARY KEY AUTOINCREMENT, cid TEXT UNIQUE NOT NULL,
            event_id TEXT UNIQUE NOT NULL, input_sha TEXT NOT NULL,
            committed_at TEXT NOT NULL, day TEXT NOT NULL,
            kind TEXT NOT NULL, title TEXT NOT NULL, summary TEXT NOT NULL,
            importance REAL NOT NULL, source_ref TEXT NOT NULL,
            prev_cid TEXT, shard_cids_json TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS events_by_day ON events(day,seq);
        CREATE TABLE IF NOT EXISTS event_shards(
            event_cid TEXT NOT NULL REFERENCES events(cid),
            shard_cid TEXT NOT NULL REFERENCES shards(cid),
            ordinal INTEGER NOT NULL,
            PRIMARY KEY(event_cid,ordinal));
        CREATE TABLE IF NOT EXISTS daily(
            day TEXT PRIMARY KEY, cid TEXT UNIQUE NOT NULL, closed_at TEXT NOT NULL,
            previous_daily_cid TEXT,
            journal_text TEXT NOT NULL, journal_sha TEXT NOT NULL,
            metrics_json TEXT NOT NULL, event_cids_json TEXT NOT NULL);
        ''')

    def close(self):
        self.db.close()

    def __enter__(self): return self
    def __exit__(self,*_): self.close()

    def remember(self, value: dict, threshold: float=0.70) -> dict:
        event=normalize_event(value)
        if not 0<=threshold<=1: raise MemoryErrorStatus('threshold must be in [0,1]')
        important=event['pin'] or event['kind'] in IMPORTANT_KINDS or event['importance']>=threshold
        if not important:
            return {'status':'IGNORED_EPHEMERAL','event_id':event['event_id'],
                    'persistent_write':False,'reason':'insufficient_salience'}
        input_sha=digest('pnaml:input:v1',event)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            previous=self.db.execute('SELECT cid,input_sha FROM events WHERE event_id=?',
                                     (event['event_id'],)).fetchone()
            if previous:
                if previous['input_sha']!=input_sha:
                    raise MemoryErrorStatus('event_id reuse with changed payload')
                self.db.execute('COMMIT')
                return {'status':'DUPLICATE','event_id':event['event_id'],
                        'cid':previous['cid'],'persistent_write':False}
            committed=iso_utc(utcnow())
            day=committed[:10]
            if self.db.execute('SELECT 1 FROM daily WHERE day=?',(day,)).fetchone():
                raise MemoryErrorStatus('current day already finalized')
            previous_cid=self.db.execute('SELECT cid FROM events ORDER BY seq DESC LIMIT 1').fetchone()
            previous_cid=previous_cid['cid'] if previous_cid else None
            specs=shard_specs(event,committed)
            shard_cids=[]
            for kind,payload in specs:
                cid=digest('pnaml:shard:v1',{'kind':kind,'payload':payload})
                self.db.execute('INSERT OR IGNORE INTO shards VALUES (?,?,?,?)',
                                (cid,kind,canonical(payload).decode('utf-8'),committed))
                shard_cids.append(cid)
            envelope={'event_id':event['event_id'],'input_sha':input_sha,'committed_at':committed,
                      'day':day,'kind':event['kind'],'title':event['title'],
                      'summary':event['summary'],'importance':event['importance'],
                      'source_ref':event['source_ref'],'prev_cid':previous_cid,
                      'shard_cids':shard_cids}
            event_cid=digest('pnaml:event:v1',envelope)
            self.db.execute('''INSERT INTO events(cid,event_id,input_sha,committed_at,day,kind,title,
                summary,importance,source_ref,prev_cid,shard_cids_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',(
                event_cid,event['event_id'],input_sha,committed,day,event['kind'],event['title'],
                event['summary'],event['importance'],event['source_ref'],previous_cid,
                canonical(shard_cids).decode('utf-8')))
            for i,cid in enumerate(shard_cids):
                self.db.execute('INSERT INTO event_shards VALUES (?,?,?)',(event_cid,cid,i))
            self.db.execute('COMMIT')
            return {'status':'COMMITTED','event_id':event['event_id'],'cid':event_cid,
                    'shard_cids':shard_cids,'committed_at':committed,'persistent_write':True}
        except Exception:
            self.db.execute('ROLLBACK')
            raise

    def get_event(self, identifier: str) -> dict | None:
        row=self.db.execute('SELECT * FROM events WHERE event_id=? OR cid=?',
                            (identifier,identifier)).fetchone()
        if not row:return None
        out={k:row[k] for k in row.keys() if k not in ('shard_cids_json',)}
        refs=self.db.execute('''SELECT s.cid,s.kind,s.payload_json FROM event_shards e
             JOIN shards s ON s.cid=e.shard_cid WHERE e.event_cid=? ORDER BY e.ordinal''',
             (row['cid'],)).fetchall()
        out['shards']=[{'cid':s['cid'],'kind':s['kind'],'payload':json.loads(s['payload_json'])}
                       for s in refs]
        return out

    def recall(self, query: str, limit: int=20) -> list[dict]:
        if not query.strip(): raise MemoryErrorStatus('empty query')
        if not 1<=limit<=100: raise MemoryErrorStatus('limit out of range')
        escaped=query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
        rows=self.db.execute('''SELECT event_id,cid,title,summary,kind,source_ref,committed_at
            FROM events WHERE title LIKE ? ESCAPE '\\' OR summary LIKE ? ESCAPE '\\'
            ORDER BY seq DESC LIMIT ?''',(f'%{escaped}%',f'%{escaped}%',limit)).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def _render_journal(day: str, rows: list[sqlite3.Row]) -> str:
        lines=[f'# Dziennik PNAML — {day} (UTC)','',
               'Automatyczna chronologia zatwierdzonych zdarzeń. Bez rekonstrukcji surowego AUX.','']
        if not rows:lines.append('Brak zatwierdzonych zdarzeń tego dnia.')
        for r in rows:
            lines.append(f"- {r['committed_at']} | {r['kind']} | {r['title']} | CID {r['cid']}")
            lines.append(f"  {r['summary']}")
            lines.append(f"  Źródło: {r['source_ref']}")
        return '\n'.join(lines)+'\n'

    def finalize_day(self, day: str, metrics: dict | None=None, *, allow_today: bool=False) -> dict:
        try: d=date.fromisoformat(day)
        except ValueError as exc:raise MemoryErrorStatus('date must be YYYY-MM-DD') from exc
        current=utcnow().date()
        if d>current or (d==current and not allow_today):
            raise MemoryErrorStatus('only past UTC days can be finalized without allow_today')
        metrics = validate_metrics_snapshot(metrics if metrics is not None else
                                            {'status':'NOT_MEASURED','sample_count':0})
        metric_bytes=canonical(metrics)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            existing=self.db.execute('SELECT cid FROM daily WHERE day=?',(day,)).fetchone()
            if existing:
                self.db.execute('COMMIT')
                return {'status':'ALREADY_FINALIZED','day':day,'cid':existing['cid']}
            last=self.db.execute('SELECT day,cid FROM daily ORDER BY day DESC LIMIT 1').fetchone()
            if last and last['day']>=day:
                raise MemoryErrorStatus('daily snapshots must be finalized chronologically')
            rows=self.db.execute('SELECT * FROM events WHERE day=? ORDER BY seq',(day,)).fetchall()
            journal=self._render_journal(day,rows)
            journal_sha=digest('pnaml:journal:v1',journal)
            event_cids=[r['cid'] for r in rows]
            prev=last['cid'] if last else None
            daily_envelope={'day':day,'previous_daily_cid':prev,'journal_sha':journal_sha,
                            'metrics':metrics,'event_cids':event_cids}
            cid=digest('pnaml:daily:v1',daily_envelope)
            closed=iso_utc(utcnow())
            self.db.execute('INSERT INTO daily VALUES (?,?,?,?,?,?,?,?)',(
                day,cid,closed,prev,journal,journal_sha,metric_bytes.decode('utf-8'),
                canonical(event_cids).decode('utf-8')))
            self.db.execute('COMMIT')
            return {'status':'FINALIZED','day':day,'cid':cid,'journal_sha':journal_sha,
                    'event_count':len(rows),'metrics_sample_count':metrics.get('sample_count',0),
                    'previous_daily_cid':prev}
        except Exception:
            self.db.execute('ROLLBACK')
            raise

    def get_day(self, day: str) -> dict | None:
        r=self.db.execute('SELECT * FROM daily WHERE day=?',(day,)).fetchone()
        if not r:return None
        o=dict(r)
        o['metrics']=json.loads(o.pop('metrics_json'))
        o['event_cids']=json.loads(o.pop('event_cids_json'))
        return o

    def restore(self, recent_limit: int=100, day_limit: int=7) -> dict:
        last=self.db.execute('SELECT * FROM daily ORDER BY day DESC LIMIT 1').fetchone()
        daily=self.db.execute('SELECT day,cid,previous_daily_cid FROM daily ORDER BY day DESC LIMIT ?',
                              (day_limit,)).fetchall()
        if last:
            rows=self.db.execute('SELECT event_id,cid,kind,title,committed_at FROM events WHERE day>? ORDER BY seq ASC LIMIT ?',
                                 (last['day'],recent_limit)).fetchall()
        else:
            rows=self.db.execute('SELECT event_id,cid,kind,title,committed_at FROM events ORDER BY seq DESC LIMIT ?',
                                 (recent_limit,)).fetchall()
        return {'schema':SCHEMA,'last_closed_day':last['day'] if last else None,
                'last_daily_cid':last['cid'] if last else None,
                'recent_events':[dict(r) for r in rows],
                'daily_chain':[dict(d) for d in daily],
                'note':'Old event shards remain available by CID; derived indexes can be rebuilt.'}

    def verify(self) -> dict:
        errors=[]; prev=None; n=0
        for row in self.db.execute('SELECT * FROM events ORDER BY seq'):
            n+=1
            shards=json.loads(row['shard_cids_json'])
            refs=self.db.execute('''SELECT e.ordinal,s.cid,s.kind,s.payload_json FROM event_shards e
                JOIN shards s ON s.cid=e.shard_cid WHERE e.event_cid=? ORDER BY e.ordinal''',
                (row['cid'],)).fetchall()
            if [r['cid'] for r in refs]!=shards or [r['ordinal'] for r in refs]!=list(range(len(refs))):
                errors.append(f'event {row["event_id"]}: shard linkage mismatch')
            for sr in refs:
                try:
                    actual=digest('pnaml:shard:v1',{'kind':sr['kind'],'payload':json.loads(sr['payload_json'])})
                    if actual!=sr['cid']:errors.append(f'shard {sr["cid"]}: payload altered')
                except (ValueError,TypeError):errors.append(f'shard {sr["cid"]}: malformed JSON')
            envelope={k:row[k] for k in ('event_id','input_sha','committed_at','day','kind','title',
                                          'summary','importance','source_ref','prev_cid')}
            envelope['shard_cids']=shards
            if row['prev_cid']!=prev:errors.append(f'event {row["event_id"]}: chain break')
            if digest('pnaml:event:v1',envelope)!=row['cid']:
                errors.append(f'event {row["event_id"]}: CID mismatch')
            prev=row['cid']
        prev_daily=None; d=0
        for row in self.db.execute('SELECT * FROM daily ORDER BY day'):
            d+=1; day=row['day']
            events=self.db.execute('SELECT * FROM events WHERE day=? ORDER BY seq',(day,)).fetchall()
            expected_cids=[r['cid'] for r in events]
            try:stored_cids=json.loads(row['event_cids_json']); metrics=json.loads(row['metrics_json'])
            except ValueError:
                errors.append(f'day {day}: malformed JSON');continue
            journal=self._render_journal(day,events)
            js=digest('pnaml:journal:v1',journal)
            if js!=row['journal_sha'] or journal!=row['journal_text']:
                errors.append(f'day {day}: journal mismatch')
            if stored_cids!=expected_cids:errors.append(f'day {day}: event set changed')
            if row['previous_daily_cid']!=prev_daily:errors.append(f'day {day}: chain break')
            expected=digest('pnaml:daily:v1',{'day':day,'previous_daily_cid':row['previous_daily_cid'],
                'journal_sha':row['journal_sha'],'metrics':metrics,'event_cids':stored_cids})
            if expected!=row['cid']:errors.append(f'day {day}: CID mismatch')
            prev_daily=row['cid']
        return {'status':'PASS' if not errors else 'FAIL','events_checked':n,
                'days_checked':d,'errors':errors,'event_head':prev,'daily_head':prev_daily}


class MetricAccumulator:
    """Welford running aggregates in volatile RAM. No raw sample retention."""
    def __init__(self):
        self.count=0
        self.data={k:{'min':None,'max':None,'mean':0.0,'m2':0.0,'n':0} for k in
                   ('r36','phase_dispersion','omega_mean','omega_abs_max')}
    def add(self, values: dict) -> None:
        for k in self.data:
            v=values.get(k)
            if v is not None and (isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v)):
                raise MemoryErrorStatus(f'nonfinite metric: {k}')
        self.count+=1
        for k,st in self.data.items():
            v=values.get(k)
            if v is None:continue
            if not isinstance(v,(int,float)) or not math.isfinite(v):
                raise MemoryErrorStatus(f'nonfinite metric: {k}')
            st['n']+=1
            st['min']=float(v) if st['min'] is None else min(st['min'],v)
            st['max']=float(v) if st['max'] is None else max(st['max'],v)
            delta=v-st['mean'];st['mean']+=delta/st['n'];st['m2']+=delta*(v-st['mean'])
    def summary(self) -> dict:
        return {'status':'OBSERVED_AGGREGATES' if self.count else 'NOT_MEASURED',
                'sample_count':self.count,'aux_raw_persisted':False,
                'metrics':{k:{'samples':v['n'],'min':v['min'],'max':v['max'],
                              'mean':v['mean'] if v['n'] else None,
                              'stddev':math.sqrt(max(0.0,v['m2']/v['n'])) if v['n'] else None}
                           for k,v in self.data.items()}}


def observe_aux_file(path: str | Path, root: str | Path) -> dict:
    """Stateless observation of one approved JSON snapshot; O_RDONLY, no mutation.

    The input format is a derived observation of the source AUX, not the AUX
    memory object itself. State has to expose phi36 (36 radians), optionally
    omega36 (36 angular frequencies), and optionally tick.
    """
    path=Path(path)
    resolved=path.resolve(strict=True)
    permitted=Path(root).resolve(strict=True)
    if os.path.commonpath([str(permitted),str(resolved)])!=str(permitted):
        raise MemoryErrorStatus('AUX file outside authorized read-only source root')
    flags=os.O_RDONLY | getattr(os,'O_NOFOLLOW',0) | getattr(os,'O_CLOEXEC',0)
    fd=os.open(resolved,flags)
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size>1024*1024:
            raise MemoryErrorStatus('AUX observation must be a regular JSON file <=1 MiB')
        data=os.read(fd,1024*1024+1)
        if len(data)>1024*1024:raise MemoryErrorStatus('AUX input too large')
    finally:os.close(fd)
    payload=json.loads(data)
    if not isinstance(payload,dict):raise MemoryErrorStatus('AUX observation must be an object')
    phases=payload.get('phi36')
    if not isinstance(phases,list) or len(phases)!=36 or any(
        isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in phases):
        raise MemoryErrorStatus('expected exactly 36 finite phi36 radians')
    omegas=payload.get('omega36')
    if omegas is not None and (not isinstance(omegas,list) or len(omegas)!=36 or any(
        isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in omegas)):
        raise MemoryErrorStatus('omega36 must contain 36 finite numbers')
    re=sum(math.cos(p) for p in phases)/36
    im=sum(math.sin(p) for p in phases)/36
    r36=min(1.0,math.hypot(re,im))
    return {'r36':r36,'phase_dispersion':1-r36,
            'omega_mean':sum(omegas)/36 if omegas is not None else None,
            'omega_abs_max':max(abs(o) for o in omegas) if omegas is not None else None}
