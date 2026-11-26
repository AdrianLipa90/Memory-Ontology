"""Standalone CLI. The 'run' command reads AUX only; 'add' commits selected episodes."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import sqlite3
import os
from pathlib import Path
import sys
import time

from .core import (MemoryStore, MetricAccumulator, MemoryErrorStatus,
                   observe_aux_file, canonical, utcnow)


def print_json(value):
    print(json.dumps(value,indent=2,ensure_ascii=False,sort_keys=True,allow_nan=False))


def read_obj(path):
    if path=='-': return json.load(sys.stdin)
    with open(path,'r',encoding='utf-8') as f: return json.load(f)


def write_new(path: Path, data: bytes):
    path.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive write deliberately forbids rewriting a prior exported receipt.
    with path.open('xb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def export_day(store: MemoryStore, day: str, parent: Path) -> dict:
    snap=store.get_day(day)
    if snap is None:raise MemoryErrorStatus('finalize this day before exporting')
    dest=parent / ('PNAML_DAY_'+day)
    if dest.exists():raise MemoryErrorStatus('export destination already exists; no overwrite')
    dest.mkdir(parents=True)
    rows=store.db.execute('SELECT event_id FROM events WHERE day=? ORDER BY seq',(day,)).fetchall()
    contents={
        'journal.md':snap['journal_text'].encode('utf-8'),
        'metrics.json':json.dumps(snap['metrics'],ensure_ascii=False,indent=2,sort_keys=True).encode('utf-8')+b'\n',
        'receipt.json':json.dumps({k:v for k,v in snap.items() if k not in ('journal_text','metrics')},
                                 ensure_ascii=False,indent=2,sort_keys=True).encode('utf-8')+b'\n',
        'events.jsonl':b''.join(canonical(store.get_event(r['event_id']))+b'\n' for r in rows),
    }
    hashes={}
    for filename,data in contents.items():
        write_new(dest/filename,data)
        hashes[filename]=hashlib.sha256(data).hexdigest()
    manifest={'schema':'PNAML_DAY_EXPORT_V1','day':day,'daily_cid':snap['cid'],
              'files_sha256':hashes,'raw_aux_included':False}
    write_new(dest/'MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2,
                                        sort_keys=True).encode('utf-8')+b'\n')
    return {'status':'EXPORTED','day':day,'path':str(dest),'daily_cid':snap['cid'],
            'files':sorted([*contents,'MANIFEST.json'])}


def run_observer(store_path: Path, aux_file: Path | None, aux_root: Path | None, interval: float):
    # Source AUX is never opened for writing and never copied to SQLite.
    if aux_root is not None:
        persistent=store_path.expanduser().resolve()
        read_root=aux_root.resolve()
        if os.path.commonpath([str(persistent),str(read_root)])==str(read_root):
            raise MemoryErrorStatus('persistent DB must remain outside read-only AUX root')
    with MemoryStore(store_path) as store:
        today=utcnow().date()
        # Backfill missed journal days without inventing AUX measurements.
        last=store.db.execute('SELECT day FROM daily ORDER BY day DESC LIMIT 1').fetchone()
        first=store.db.execute('SELECT day FROM events ORDER BY seq LIMIT 1').fetchone()
        start=(date.fromisoformat(last['day'])+timedelta(days=1)) if last else (
              date.fromisoformat(first['day']) if first else today)
        while start<today:
            print_json(store.finalize_day(str(start)))
            start+=timedelta(days=1)
        accumulator=MetricAccumulator()
        previous_signature=None
        print_json({'status':'RUNNING_CANDIDATE','schema':'PNAML_CONTINUITY_EVENT_JOURNAL_V1',
                    'mode':'AUX_READ_ONLY','event_commits':'external explicit add',
                    'daily_metrics':'volatile_until_daily_finalize','current_utc_day':str(today)})
        try:
            while True:
                now=utcnow().date()
                while today<now:
                    receipt=store.finalize_day(str(today),accumulator.summary())
                    print_json(receipt)
                    today+=timedelta(days=1)
                    accumulator=MetricAccumulator()
                    previous_signature=None
                if aux_file is not None:
                    try:
                        info=aux_file.stat()
                        signature=(info.st_ino,info.st_size,info.st_mtime_ns)
                        if signature != previous_signature:
                            observation=observe_aux_file(aux_file,aux_root)
                            accumulator.add(observation)
                            previous_signature=signature
                    except (OSError,ValueError,json.JSONDecodeError) as exc:
                        # No persistent failure telemetry or fabricated values.
                        print_json({'status':'OBSERVATION_SKIPPED','reason':str(exc)})
                time.sleep(interval)
        except KeyboardInterrupt:
            # Graceful stop does not create premature 'daily' snapshots.
            print_json({'status':'STOPPED','today_aggregate_in_memory_lost':accumulator.count,
                        'note':'Important events remain committed; daily metrics require uninterrupted collection.'})


def main(argv=None):
    parser=argparse.ArgumentParser(prog='pnaml-memory',description='PNAML selective continuity memory')
    parser.add_argument('--store',default='./state/pnaml_continuity.sqlite3',
                        help='persistent SQLite path OUTSIDE /dev/shm')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('init')
    add=sub.add_parser('add',help='synchronously commit an important event')
    add.add_argument('--event',required=True,help='JSON file or - for stdin')
    add.add_argument('--threshold',type=float,default=0.70)
    get=sub.add_parser('get')
    get.add_argument('--id',required=True)
    recall=sub.add_parser('recall')
    recall.add_argument('--query',required=True)
    recall.add_argument('--limit',type=int,default=20)
    day=sub.add_parser('daily',help='close a UTC day with immutable journal + metrics')
    day.add_argument('--date',required=True)
    day.add_argument('--metrics-json',default=None,help='pre-aggregated JSON only, never raw AUX')
    day.add_argument('--allow-today',action='store_true')
    preview=sub.add_parser('journal-preview')
    preview.add_argument('--date',default=None)
    exp=sub.add_parser('export-day')
    exp.add_argument('--date',required=True)
    exp.add_argument('--out',required=True)
    sub.add_parser('verify')
    sub.add_parser('restore')
    obs=sub.add_parser('observe',help='read AUX snapshot and print derived metrics; no persistent write')
    obs.add_argument('--aux-file',required=True)
    obs.add_argument('--aux-root',required=True)
    srv=sub.add_parser('run',help='read-only AUX observer; daily aggregator stays in RAM')
    srv.add_argument('--aux-file',default=None)
    srv.add_argument('--aux-root',default=None)
    srv.add_argument('--interval',type=float,default=60.0)
    args=parser.parse_args(argv)
    try:
        if args.command=='observe':
            print_json({'status':'OBSERVED_READ_ONLY','metrics':observe_aux_file(args.aux_file,args.aux_root)})
            return 0
        if args.command=='run':
            if args.interval<0.1 or args.interval>86400:raise MemoryErrorStatus('interval out of range')
            if args.aux_file and not args.aux_root:
                raise MemoryErrorStatus('--aux-root required with --aux-file')
            run_observer(Path(args.store),Path(args.aux_file) if args.aux_file else None,
                         Path(args.aux_root) if args.aux_root else None,args.interval)
            return 0
        with MemoryStore(args.store) as store:
            if args.command=='init':ret={'status':'INITIALIZED','store':str(store.path)}
            elif args.command=='add':ret=store.remember(read_obj(args.event),args.threshold)
            elif args.command=='get':ret=store.get_event(args.id) or {'status':'NOT_FOUND'}
            elif args.command=='recall':ret={'status':'QUERY_OK','results':store.recall(args.query,args.limit)}
            elif args.command=='daily':
                metrics=read_obj(args.metrics_json) if args.metrics_json else None
                ret=store.finalize_day(args.date,metrics,allow_today=args.allow_today)
            elif args.command=='journal-preview':
                target=args.date or str(utcnow().date())
                rows=store.db.execute('SELECT * FROM events WHERE day=? ORDER BY seq',(target,)).fetchall()
                ret={'day':target,'status':'PREVIEW_NOT_COMMITTED','journal':store._render_journal(target,rows)}
            elif args.command=='export-day':ret=export_day(store,args.date,Path(args.out))
            elif args.command=='verify':ret=store.verify()
            elif args.command=='restore':ret=store.restore()
            print_json(ret)
            if isinstance(ret,dict) and ret.get('status')=='FAIL':return 2
        return 0
    except (MemoryErrorStatus,ValueError,sqlite3.Error) as exc:
        print_json({'status':'ERROR','reason':str(exc)})
        return 2
    except (OSError,json.JSONDecodeError) as exc:
        print_json({'status':'ERROR','reason':str(exc)})
        return 2


if __name__=='__main__':sys.exit(main())
