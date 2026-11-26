// Synthetic graph preference prediction and history intervention.
function benchmark(){
 function rng(seed){let s=seed>>>0;return ()=>{s=(Math.imul(s,1664525)+1013904223)>>>0;return s/4294967296}}
 function shortest(edges,start,goal){
  const nodes=[...new Set(edges.flatMap(e=>[e[0],e[1]]).concat([start,goal]))],d=new Map(nodes.map(v=>[v,Infinity])),prev=new Map(),todo=new Set(nodes);d.set(start,0);
  while(todo.size){const a=[...todo].reduce((u,v)=>d.get(u)<=d.get(v)?u:v);todo.delete(a);if(!Number.isFinite(d.get(a)))break;if(a===goal)break;
   for(const [u,v,c,open] of edges){if(!open||u!==a||!todo.has(v))continue;if(d.get(a)+c<d.get(v)){d.set(v,d.get(a)+c);prev.set(v,a)}}
  }
  if(!Number.isFinite(d.get(goal)))return {cost:Infinity,path:[]};const path=[goal];while(path[0]!==start)path.unshift(prev.get(path[0]));return {cost:d.get(goal),path}
 }
 function generate(seed,N,regime){
  const U=rng(seed),rows=[];
  for(let k=0;k<N;k++){
   const latent=.1+.8*U(),I=.6+.4*U(),tau=1+3*U(),histN=12;let pos=0;
   for(let j=0;j<histN;j++)pos+=U()<latent?1:0;
   const D=(1+pos)/(2+histN),premium=.1+3.4*U(),extra=.2+U(),u=U(),status=u<.08?"cancelled":u<.16?"unknown":u<.27?"open":"detour";
   const edges=[["x","g",1,status==="open"],["x","a",.5,status==="detour"],["a","g",.5+premium,status==="detour"],["x","b",.5,status==="detour"],["b","g",.5+premium+extra,status==="detour"],["x","r",1,true]];
   const goal=shortest(edges,"x","g"),ref=shortest(edges,"x","r"),delta=goal.cost-ref.cost,budget=4;
   // Latent cost tolerance is independent of observed history counts. Two declared generators:
   // stationary time-independent; age-sensitive saturating, not the tested linear product.
   const tol=4*latent*I*(regime==="age"?1-Math.exp(-tau/1.8):1)+.4*(U()-.5);
   const feasible=Number.isFinite(goal.cost)&&goal.cost<=budget;
   rows.push({I,tau,D,W:I*tau,status,delta,feasible,label:feasible&&delta<=Math.max(0,tol),goalPath:goal.path,refPath:ref.path});
  }return rows
 }
 const names=["current","historyD","willOnly","willD","shuffledD","boundedWillD"];
 function score(r,name,shuf){
  switch(name){case"current":return r.I*.5;case"historyD":return r.I*r.D;case"willOnly":return r.W*.5;case"willD":return r.W*r.D;case"shuffledD":return r.W*shuf;case"boundedWillD":return r.I*(1-Math.exp(-r.tau/1.8))*r.D;}
 }
 function permute(rows,seed){const a=rows.map(r=>r.D),U=rng(seed);for(let i=a.length-1;i>0;i--){const j=Math.floor(U()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
 function evaluate(rows,name,k,seed){const sh=permute(rows,seed);let n=0,tp=0,tn=0,fp=0,fn=0,hold=0,rev=0,cost=0,violations=0;
  rows.forEach((r,i)=>{
   if(r.status==="cancelled"){rev++;return}if(r.status==="unknown"){hold++;return}
   if(!r.feasible){hold++;return}if(r.status!=="detour")return;
   n++;const take=r.delta<=k*score(r,name,sh[i]);if(take){cost+=r.delta;if(r.label)tp++;else fp++;if(r.goalPath.length<2)violations++}else if(r.label)fn++;else tn++;
  });return {n,tp,tn,fp,fn,accuracy:(tp+tn)/n,paidPremium:cost,hold,rev,violations}
 }
 function fit(rows,name){let best={k:0,accuracy:-1};for(let i=0;i<=160;i++){const k=i*.05;const e=evaluate(rows,name,k,381);if(e.accuracy>best.accuracy)best={k,accuracy:e.accuracy}}return best}
 const results={};
 for(const regime of ["stationary","age"]){const train=generate(421,1200,regime),test=generate(917,2400,regime);results[regime]={};for(const name of names){const f=fit(train,name);results[regime][name]={...f,test:evaluate(test,name,f.k,781)}}}
 const shift=generate(1217,2400,"stationary");results.shift={};for(const name of names)results.shift[name]=evaluate(shift,name,results.age[name].k,782);
 // independent matched state counterfactual with explicit graph path
 const a=shortest([["x","g",1,false],["x","a",.5,true],["a","g",1.5,true],["x","r",1,true]],"x","g");
 const m={I:1,tau:2,W:2,D:3/14};const n={...m,D:11/14};const k=1;
 const intervention={path:a.path,cost:a.cost,premium:a.cost-1,Dlow:m.D,Dhigh:n.D,lowAccepted:a.cost-1<=k*score(m,"willD"),highAccepted:a.cost-1<=k*score(n,"willD")};
 if(intervention.lowAccepted||!intervention.highAccepted)throw Error("intervention failed");
 for(const r of Object.values(results))for(const v of Object.values(r))if((v.test??v).violations)throw Error("invalid path");
 return {scope:"Synthetic offline graph decision prediction; held-out preference labels generated from independent latent tolerance, not human measurements; no native runtime.",trainPerRegime:1200,testPerRegime:2400,shiftTest:2400,calibration:"maximize accuracy on feasible detours; k grid 0..8 step .05; first tie",results,intervention,limitations:"Bounded model uses known generating saturation timescale 1.8 and is oracle-form baseline; not fair evidence of discovered saturation. All policies revise verified cancellation and HOLD unknown/unaffordable; only feasible detours scored. D from 12 synthetic prior Bernoulli observations; true determination not measured. No full temporal learning or graph discovery."}
}
export { benchmark };
