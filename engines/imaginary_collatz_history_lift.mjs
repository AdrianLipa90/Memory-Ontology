// Exact finite Collatz parity/rapidity/history lift; no native runtime.
function witness(N=4096,H=32,cap=10000){
 const C=n=>n%2n===0n?n/2n:3n*n+1n;
 const cache=new Map([[1n,[4n,7n]],[2n,[2n,7n]],[4n,[1n,7n]]]);
 function phase(n){
   const path=[];let x=n;
   while(!cache.has(x)&&path.length<cap){path.push(x);x=C(x)}
   if(!cache.has(x))throw Error("unresolved terminal orbit");
   let [a,d]=cache.get(x);
   for(let i=path.length-1;i>=0;i--){const v=path[i];a+=v%2n*d;d*=2n;cache.set(v,[a,d])}
   return cache.get(n);
 }
 const eq=(a,d,b,e)=>a*e===b*d;
 const hist=new Map();let stepChecks=0,reverse=0,radial=0,accelerated=0,maxFirst=0;
 for(let j=1;j<=N;j++){
   const start=BigInt(j);let n=start,[a,d]=phase(n),y=0n,den=1n;const init=a,initD=d;
   let f=n,l=0;while(f!==1n&&l<cap){f=C(f);l++}if(f!==1n)throw Error("cap");maxFirst=Math.max(maxFirst,l);
   for(let k=0;k<H;k++){
     const b=n%2n;if(2n*a/d!==b)throw Error("phase bit");
     const old=n;n=C(n);
     const tnum=2n*old-1n,tden=2n*old+1n,tn=2n*n-1n,td=2n*n+1n;
     if(b===0n){if(!eq(3n*tnum-tden,3n*tden-tnum,tn,td))throw Error("even radial")}
     else{
       if(!eq(tnum+2n*tden,3n*tden,tn,td))throw Error("odd radial");
       const m=n/2n,[qa,qd]=phase(m);
       if(!eq(4n*a%d,d,qa,qd))throw Error("accelerated phase");
       accelerated++;
     }
     radial++;a=2n*a-b*d;y+=b*den;den*=2n;
     const [qa,qd]=phase(n);if(!eq(a,d,qa,qd))throw Error("phase step");stepChecks++;
   }
   hist.set(String(n),(hist.get(String(n))??0)+1);
   for(let k=0;k<H;k++){
      const b=2n*y/den;y-=b*(den/2n);den/=2n;
      a+=b*d;d*=2n;
      if(b===0n)n*=2n;else{
        if((n-1n)%3n!==0n)throw Error("invalid inverse");n=(n-1n)/3n;
        if(n%2n!==1n)throw Error("odd inverse");
      }
   }
   if(n!==start||!eq(a,d,init,initD)||y!==0n||den!==1n)throw Error("reverse");
   reverse++;
 }
 const conditional=[...hist.values()].reduce((s,v)=>s+v/N*Math.log2(v),0);
 return {N,H,stepChecks,radial,accelerated,reverse,terminal_orbit_cap:cap,max_first_hit_1:maxFirst,distinct_endpoints:hist.size,largest_endpoint_fibre:Math.max(...hist.values()),conditional_history_entropy_bits:conditional,endpoint_entropy_bits:Math.log2(N)-conditional,example_collision:{n1:1,n2:8,endpoint:4},scope:"exact BigInt rational phase/rapidity and reversible history lift, uniform finite seed ensemble; no HTRI run"};
}
export { witness };
