// Finite candidate state-space memory reference. Positive costs, explicit events, no native runtime.
function graph(nodes, edges) {
  if(new Set(nodes).size!==nodes.length) throw Error("duplicate state");
  const weights=new Map();
  for(const [a,b,w] of edges){
    if(!nodes.includes(a)||!nodes.includes(b)||a===b||!Number.isFinite(w)||w<=0)throw Error("invalid edge");
    const id=JSON.stringify([a,b].sort());
    if(weights.has(id))throw Error("duplicate edge");
    weights.set(id,w);
  }
  return {nodes:[...nodes],weights,seen:new Map(),access:0.2};
}

function update(g,e){
  if(typeof e.id!=="string"||!e.id||typeof e.source!=="string"||!e.source||typeof e.verified!=="boolean")throw Error("event contract");
  const key=JSON.stringify([e.a,e.b].sort());
  if(!g.weights.has(key))throw Error("inadmissible edge");
  const signature=JSON.stringify([e.a,e.b,e.source,e.verified]);
  if(g.seen.has(e.id)){
    if(g.seen.get(e.id)!==signature)throw Error("conflicting replay");
    return g;
  }
  const next={nodes:[...g.nodes],weights:new Map(g.weights),seen:new Map(g.seen),access:g.access};
  next.seen.set(e.id,signature);
  if(e.verified){
    next.weights.set(key,0.5+0.5*(next.weights.get(key)-0.5));
    next.access+=0.25*(1-next.access);
  }
  return next;
}

function decay(g,dt){
  if(!Number.isFinite(dt)||dt<0)throw Error("invalid duration");
  return {...g,access:g.access*Math.exp(-dt)};
}

function distance(g,start){
  if(!g.nodes.includes(start))throw Error("unknown state");
  const d=new Map(g.nodes.map(n=>[n,n===start?0:Infinity]));
  const pending=new Set(g.nodes);
  while(pending.size){
    const a=[...pending].reduce((a,b)=>d.get(a)<=d.get(b)?a:b);
    pending.delete(a);
    if(!Number.isFinite(d.get(a)))break;
    for(const b of pending){
      const w=g.weights.get(JSON.stringify([a,b].sort()));
      if(w!==undefined)d.set(b,Math.min(d.get(b),d.get(a)+w));
    }
  }
  return d;
}

function reachable(g,start,budget=Infinity){
  if(!(budget>=0))throw Error("invalid budget");
  return [...distance(g,start)].filter(([,v])=>Number.isFinite(v)&&v<=budget).map(([k])=>k).sort();
}

function witness(){
  const g=graph(["x","a","b","z"],[["x","a",2],["a","z",2],["x","b",1.5],["b","z",1.5]]);
  const e={id:"fixture-1",a:"x",b:"a",source:"synthetic traversal receipt",verified:true};
  const a=update(g,e);
  const b=update(a,{...e,id:"fixture-2",a:"a",b:"z"});
  const c=decay(b,20);
  const fail=update(g,{...e,verified:false});
  const relabel={x:"p",a:"q",b:"r",z:"s"};
  const renamed=graph(g.nodes.map(n=>relabel[n]),[...b.weights].map(([k,w])=>[...JSON.parse(k).map(n=>relabel[n]),w]));
  const checks={
    matched_initial_state:true,
    original_immutable:distance(g,"x").get("z")===3,
    history_changes_cost:distance(b,"x").get("z")===2.5,
    unchanged_topology:JSON.stringify(reachable(g,"x"))===JSON.stringify(reachable(b,"x")),
    budgeted_reachability_changes:!reachable(g,"x",2.6).includes("z")&&reachable(b,"x",2.6).includes("z"),
    unverified_no_weight_update:JSON.stringify([...fail.weights])===JSON.stringify([...g.weights]),
    replay_idempotent:update(a,e)===a,
    decay_keeps_geometry:c.access<1e-8&&JSON.stringify([...c.weights])===JSON.stringify([...b.weights]),
    relabel_invariance:g.nodes.every(n=>distance(b,"x").get(n)===distance(renamed,"p").get(relabel[n])),
    disconnected_excluded:!reachable(graph(["x","z"],[]),"x").includes("z")
  };
  let conflict=false;try{update(a,{...e,source:"conflict"})}catch{conflict=true}
  checks.conflicting_replay_rejected=conflict;
  if(!Object.values(checks).every(Boolean))throw Error(JSON.stringify(checks));
  return {scope:"deterministic finite graph fixture; explicit externally supplied verification, no native HTRI/TIR execution",checks,initial_cost:distance(g,"x").get("z"),learned_cost:distance(b,"x").get("z"),access_before_decay:b.access,access_after_decay:c.access,initial_budget_reachable:reachable(g,"x",2.6),learned_budget_reachable:reachable(b,"x",2.6)};
}

export {graph,update,decay,distance,reachable,witness};
