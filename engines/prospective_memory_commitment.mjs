// Synthetic prospective-memory and state-space routing contract.
function run(){
 const I=1, dur=[1,2,4], det=[.25,.5,1], premiums=[.5,1,2,4], conditions=["open","detour","blocked_unknown","unavailable_verified"], budget=4;
 const stats=Object.fromEntries(["local","rigid","replan","will"].map(p=>[p,{arrived:0,alternative:0,hold:0,revised:0,failed:0,paidPremium:0}]));
 const rows=[];const choose=(policy,condition,W,D,premium)=>{
   const open=condition==="open",detour=condition==="detour",unavailable=condition==="unavailable_verified";
   const targetCost=open?1:detour?1+premium:Infinity;
   if(unavailable)return {status:"revised",paid:0,reason:"verified unavailability"};
   if(policy==="local")return {status:"alternative",paid:0,reason:"cheapest immediate alternative; ties favor alternative"};
   if(policy==="rigid")return {status:open?"arrived":"hold",paid:0,reason:"original route only"};
   if(!Number.isFinite(targetCost))return {status:"hold",paid:0,reason:"no observed admissible route"};
   if(targetCost>budget)return {status:"hold",paid:0,reason:"hard resource limit"};
   if(policy==="will"&&targetCost-1>W*D)return {status:"hold",paid:0,reason:"premium exceeds willingness"};
   return {status:"arrived",paid:targetCost-1,reason:"goal route"};
 };
 for(const c of conditions)for(const t of dur)for(const D of det)for(const premium of premiums){
   const W=I*t,P=W*D;
   const outcome={};for(const p of Object.keys(stats)){const r=choose(p,c,W,D,premium);outcome[p]=r.status;stats[p][r.status]++;stats[p].paidPremium+=r.paid}
   rows.push({c,t,D,premium,W,P,...outcome});
 }
 const assert=(cond,msg)=>{if(!cond)throw Error(msg)};
 for(const r of rows){
   if(r.c==="unavailable_verified")assert(r.will==="revised","evidence");
   if(r.c==="blocked_unknown")assert(r.will==="hold","unknown");
   if(r.c==="detour")assert((r.will==="arrived")===(r.premium<=r.P&&1+r.premium<=budget),"will");
 }
 const byDuration=dur.map(t=>({t,eligible:rows.filter(r=>r.c==="detour"&&r.t===t).length,arrived:rows.filter(r=>r.c==="detour"&&r.t===t&&r.will==="arrived").length}));
 const byDetermination=det.map(D=>({D,eligible:rows.filter(r=>r.c==="detour"&&r.D===D).length,arrived:rows.filter(r=>r.c==="detour"&&r.D===D&&r.will==="arrived").length}));
 // Same current intention, state and environment; histories differ in time accrued.
 const causal=[1,4].map(t=>({t,W:t,P:t*.5,...choose("will","detour",t,.5,1)}));
 assert(causal[0].status==="hold"&&causal[1].status==="arrived","matched state intervention");
 // Same physical vector expressed in independent frames; transport to anchor.
 const rot=(v,a)=>[Math.cos(a)*v[0]-Math.sin(a)*v[1],Math.sin(a)*v[0]+Math.cos(a)*v[1]];
 const add=(a,b)=>a.map((x,j)=>x+b[j]); const mul=(a,t)=>a.map(x=>x*t);
 const terms=[{i:[1,0],angle:.3,dt:1},{i:[0,1],angle:-.6,dt:2},{i:[1,-1],angle:1.1,dt:.5}];
 const original=terms.reduce((s,r)=>add(s,mul(rot(r.i,r.angle),r.dt)),[0,0]);
 const alpha=.73, betas=[.8,-1.3,.4];
 const changed=terms.reduce((s,r,k)=>add(s,mul(rot(rot(r.i,betas[k]),r.angle+alpha-betas[k]),r.dt)),[0,0]);
 const transported=rot(original,alpha), err=Math.hypot(...changed.map((v,j)=>v-transported[j]));assert(err<1e-12,"frame covariance");
 // IDT quadrature: split constant density and intention intervals without changing integral.
 const clock=[{wp:.7,wm:.3,dl:2,i:1},{wp:1.2,wm:.8,dl:1.5,i:.5}];
 const integrate=rs=>rs.reduce((s,r)=>s+r.i*(r.wp+r.wm)*r.dl,0);
 const w=integrate(clock), split=integrate(clock.flatMap(r=>[{...r,dl:r.dl/2},{...r,dl:r.dl/2}]));assert(w===split,"split");
 // Positive activity but no directional intention.
 assert(integrate([{wp:1,wm:1,dl:3,i:0}])===0,"no intention");
 return {scope:"deterministic factorial policy fixture, not independent stochastic trials or native runtime",factors:{dur,det,premiums,conditions,budget},n:rows.length,stats,byDuration,byDetermination,causal,frameCovarianceError:err,clockIntegral:w,clockSplitIntegral:split,tests:["verified unavailability revision","unresolved blockage HOLD","cost threshold and hard limit","matched-state history intervention","transport covariance","clock subdivision invariance","zero intention zero accumulation"],notes:"Costs synthetic; readiness scale and policy chosen, not derived; all policies share hard cost budget and evidence handling. No empirical behavioral claim."};
}
export { run };
