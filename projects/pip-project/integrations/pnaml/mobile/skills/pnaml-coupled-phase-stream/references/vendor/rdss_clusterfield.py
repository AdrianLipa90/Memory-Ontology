#!/usr/bin/env python3
"""RDSS Cluster Field v1.0 -- source-derived vector regions + graph resonance.

This is a DIGITAL reference renderer, not native PNAML/AUX or physical analog
hardware. It explicitly encodes geometry extracted from the supplied image.
No original JPEG/PNG, label raster or pre-rendered RGB image is stored in the
scene. There is no claim that resonance alone generates the illustrated poster.

The decoder: (1) reconstructs continuous vector-boundary region support, (2)
builds a honeycomb grain graph, (3) solves complex gauge-covariant driven
oscillator fields by Jacobi fixed-point iteration, (4) projects three coupled
optical fields + depth, (5) integrates output pixel coverage and writes PNG.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, math, struct, time, zlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

MAGIC = 'RDSS_CLUSTER_FIELD_V1_0_REFERENCE'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def img_ref(path, w=512, h=768):
    return np.array(Image.open(path).convert('RGB').resize((w,h),Image.Resampling.LANCZOS))

def phase36(tau=1.25,steps=80):
    j=np.arange(36,dtype=np.float64)
    q0=.07*j+.024*np.sin(.35*j)
    amps=.75+.15*np.cos(2*np.pi*j/12)
    omega=.08+.045*np.cos(2*np.pi*j/9)+.011*(j%3)
    def rhs(q,t):
        return omega+.23*(np.sin(2*np.pi*(np.roll(q,-1)-q))+
                          np.sin(2*np.pi*(np.roll(q,1)-q)))/2+.025*np.sin(t)*np.cos(j/6)
    q=q0.copy();dt=tau/steps
    for n in range(steps):
        t=n*dt;k1=rhs(q,t);k2=rhs(q+dt*k1/2,t+dt/2)
        k3=rhs(q+dt*k2/2,t+dt/2);k4=rhs(q+dt*k3,t+dt)
        q+=dt*(k1+2*k2+2*k3+k4)/6
    return dict(A36=amps.tolist(),q36_lift=q.tolist(),w36=np.floor(q).astype(int).tolist(),
                omega36=omega.tolist(),time_tau=tau,clock='dimensionless_model',
                spinor='exp(i*pi*q) 4pi convention',trits12='NOT_OBSERVED')

def encode(path, w=512, h=768, classes=4, tolerance=0.65):
    t0=time.time()
    im=img_ref(path,w,h)
    data=np.float32(im.reshape(-1,3))
    cv2.setRNGSeed(17)
    _, lab, pal=cv2.kmeans(data,classes,None,
        (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,45,0.12),5,
        cv2.KMEANS_PP_CENTERS)
    ids=lab.reshape(h,w)
    # Store traced continuous polygonal boundaries, NOT a quantized image.
    contours_by_class=[]
    class_stats=[]
    for k in range(classes):
        mask=(ids==k).astype(np.uint8)*255
        cts,hier=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        parent=hier[0,:,3] if hier is not None else np.array([],int)
        polys=[]
        npts=0
        for index,ct in enumerate(cts):
            if cv2.contourArea(ct)<1.0 and len(ct)<5:continue
            approx=cv2.approxPolyDP(ct,tolerance,True).reshape(-1,2)
            if len(approx)<3:continue
            depth=0;cur=int(parent[index])
            while cur>=0:
                depth+=1;cur=int(parent[cur])
            coords=np.asarray(approx,dtype='<i2')
            polys.append((depth,coords))
            npts+=len(coords)
        # Need explicit loop parity to preserve image holes (e.g. letters).
        # Binary payload is a compact vector-path graph, not packed labels.
        packed=bytearray(struct.pack('<I',len(polys)))
        for d,xy in polys:
            packed.extend(struct.pack('<BH',d,len(xy)))
            packed.extend(xy.tobytes())
        blob=base64.b64encode(zlib.compress(bytes(packed),9)).decode('ascii')
        contours_by_class.append({'material_id':k,'compressed_paths':blob,
                                  'path_count':len(polys),'vertex_count':npts})
        class_stats.append({'pixels':int((ids==k).sum()),'paths':len(polys),'vertices':npts})
    # A human-readable source-level, typed *candidate*, not native PNAML transport.
    materials=[]
    for k,c in enumerate(pal):
        brightness=float(np.dot(c,[.2126,.7152,.0722])/255)
        materials.append({'id':k,'name':f'poster_palette_{k}',
                          'linear_rgb_reference':[round(float(v/255),6) for v in c],
                          'density':round(1.1+.35*(1-brightness),6),
                          'flexibility':round(.20+.32*brightness,6),
                          'opacity':round(.992+.006*(1-brightness),6),
                          'saturation':round(1.0+.018*(float(np.max(c)-np.min(c))/255),6),
                          'contrast':round(1.0+.006*(1-brightness),6),
                          'projection_z':round(.025*(k-classes/2),6),
                          'typed_cluster':'surface2_5d'})
    scene={'format':MAGIC,'model':'source-derived vector clusters with coupled resonant grain fields',
           'domain':{'reference_grid':[w,h],'normalized':True,'units':'dimensionless_model',
                     'geometry':'flat honeycomb brickwall 2.5D'},
           'materials':materials,'vector_geometry':{'encoding':'zlib+base64 LE uint16 polyline lists',
                       'classes':contours_by_class,'source':'AUTOMATIC_TRACE_OF_USER_SUPPLIED_IMAGE',
                       'original_bitmap_embedded':False,'implicit_support':'polygon interiors + narrow edge coverage'},
           'resonator':{'theta_gauge':180.0,'mass_coupling':0.7,'spin_coupling':0.35,
                        'resonant_transport':0.33,'iterations':13,'drive_frequency':0.68,
                        'damping':0.35,'cluster_mixing':0.015,
                        'projection_lighting':0.035,'edge_restriction':0.018},
           'carrier':phase36(),
           'rdss':{'typed_relation':'within_material_cluster / phase_transport',
                    'holonomy':'U_ij=exp(i*integral_ij A.dr), Wilson loop on graph',
                    'cluster_order':list(range(classes)),
                    'boundary_lines_implicit':True,
                    'cluster_roles':['surface2_5d','line_from_vector_boundary'],
                    'operator_order':['vector_levelset','hex_grains','spin_mass_gauge',
                                     'resonant_solve','depth_projection','pixel_integral'],
                    'native_RDSS_registry':'UNRESOLVED'},
           'bridge':{'PNAML_AUX_NATIVE':'NOT_CONNECTED',
                     'typed_registry':'UNRESOLVED',
                     'host_guard_witness':None,'peer_ack_witness':None,
                     'transport':'NONE','status':'LOCAL_DIGITAL_REFERENCE'},
           'provenance':{'input_kind':'user_uploaded_poster',
                          'image_sha256':sha(path),
                          'encoder_description':'kmeans palette + vector boundary contour trace',
                          'resonance_independently_creates_source_shapes':False,
                          'native_analog_hardware':False},
           'encode_seconds':round(time.time()-t0,3), 'diagnostic_original_coverage':class_stats}
    return scene

def validate(scene):
    if scene.get('format')!=MAGIC:raise ValueError('format')
    w,h=scene['domain']['reference_grid']
    if not (64<=w<=1024 and 64<=h<=1536):raise ValueError('domain')
    if not scene['bridge']['PNAML_AUX_NATIVE']=='NOT_CONNECTED':raise ValueError('false native connection')
    if scene['bridge']['host_guard_witness'] is not None or scene['bridge']['peer_ack_witness'] is not None:raise ValueError('spoofed witness')
    q=np.asarray(scene['carrier']['q36_lift']);a=np.asarray(scene['carrier']['A36']);wind=np.asarray(scene['carrier']['w36'])
    if len(q)!=36 or len(a)!=36 or len(wind)!=36:raise ValueError('dimension')
    if np.any(np.floor(q)!=wind):raise ValueError('lifted winding')
    if scene['carrier']['trits12']!='NOT_OBSERVED':raise ValueError('early collapse')
    if len(scene['materials'])!=len(scene['vector_geometry']['classes']):raise ValueError('materials')
    for p in scene['vector_geometry']['classes']:
        b=zlib.decompress(base64.b64decode(p['compressed_paths'],validate=True))
        n=struct.unpack_from('<I',b,0)[0];at=4
        if n!=p['path_count']:raise ValueError('pathcount')
        vertices=0
        for _ in range(n):
            d,pts=struct.unpack_from('<BH',b,at);at+=3+pts*4;vertices+=pts
            if d>255 or pts<3:raise ValueError('bad path')
        if at!=len(b) or vertices!=p['vertex_count']:raise ValueError('invalid vector payload')
    return True

def unpack_paths(piece):
    b=zlib.decompress(base64.b64decode(piece['compressed_paths']))
    n=struct.unpack_from('<I',b,0)[0];at=4;paths=[]
    for _ in range(n):
        depth,size=struct.unpack_from('<BH',b,at);at+=3
        pts=np.frombuffer(b,dtype='<i2',count=2*size,offset=at).reshape(-1,2).copy();at+=4*size
        paths.append((depth,pts))
    return paths

def covers(scene, ow,oh,supersample=2):
    """Integrate polygon interior over output pixel only: no global fuzzy blur."""
    w,h=scene['domain']['reference_grid']
    HH=oh*supersample;WW=ow*supersample
    channels=[]
    for obj in scene['vector_geometry']['classes']:
        # One class as a union of nested level set regions.
        acc=np.zeros((HH,WW),dtype=np.uint8)
        # Path drawing here is a numerical sampling of a vector area model,
        # NOT an uncompressed image loaded from the scene.
        for depth,pts in sorted(unpack_paths(obj),key=lambda p:p[0]):
            polygon=np.rint((pts.astype(np.float32)+.5)*np.array([WW/w,HH/h])-0.5).astype(np.int32)
            cv2.fillPoly(acc,[polygon],255 if depth%2==0 else 0,lineType=cv2.LINE_8)
        if supersample>1:
            channel=cv2.resize(acc,(ow,oh),interpolation=cv2.INTER_AREA).astype(np.float32)/255.0
        else:channel=acc.astype(np.float32)/255.0
        channels.append(channel)
    cov=np.stack(channels,axis=-1)
    # Region boundaries reconstructed independently may overlap in a subpixel
    # sliver; normalize their continuous-area coverage.
    cov/=np.maximum(cov.sum(axis=-1,keepdims=True),1e-6)
    # narrow slivers uncovered in polygon approximation are nearest-filled
    uncovered=(cov.sum(axis=-1)<.01)
    if uncovered.any():
        idx=int(np.argmax([m['density'] for m in scene['materials']]))
        cov[uncovered,idx]=1.
    return cov

def hex_edges(w,h):
    v=np.arange(w*h,dtype=np.int32).reshape(h,w)
    a=[v[:,:-1].ravel()];b=[v[:,1:].ravel()]
    yy,xx=np.indices((h-1,w))
    selector=((yy+xx)%2==0)
    a.append(v[:-1,:][selector].ravel());b.append(v[1:,:][selector].ravel())
    return np.concatenate(a),np.concatenate(b)

def optical_solver(scene,cov,options=None):
    """Driven grain field, phase-covariant edge transport, nonlocal coupling."""
    cfg=scene['resonator'].copy();cfg.update(options or {})
    HH,WW,K=cov.shape
    n=HH*WW
    ptsx,ptsy=np.meshgrid((np.arange(WW)+.5)/WW,(np.arange(HH)+.5)/HH)
    u,v=hex_edges(WW,HH)
    x=ptsx.ravel();y=ptsy.ravel()
    q=np.array(scene['carrier']['q36_lift'])
    amps=np.array(scene['carrier']['A36'])
    omega=np.array(scene['carrier']['omega36'])
    # 36 reference phase oscillators across 3x12 virtual banks;
    # PNAML is a local reference model, not external AUX.
    centers=np.stack([.08+.84*(np.arange(36)%6+.5)/6,
                      .08+.84*(np.arange(36)//6+.5)/6],axis=1)
    # Memory-bounded scalar field interpolation via nearest 4 landmarks.
    from scipy.spatial import cKDTree
    dist,near=cKDTree(centers).query(np.stack([x,y],axis=1),k=4)
    ker=np.exp(-(dist/.17)**2);ker/=ker.sum(axis=1,keepdims=True)
    phase=(ker*q[near]).sum(axis=1)
    speed=(ker*omega[near]).sum(axis=1)
    pi_spin=np.exp(1j*np.pi*phase)  # spinor, NOT modulo-reduced q
    cov2=cov.reshape(n,K).astype(np.float64)
    rho=cov2@np.array([v['density'] for v in scene['materials']])
    mass=1+cfg['mass_coupling']*(rho-1)
    if np.min(mass)<=0:raise ValueError('negative grain mass')
    # Local connectance reduced across different material clusters, to keep
    # the preserved geometric boundaries sharp rather than globally fuzzy.
    pair_coh=(cov2[u]*cov2[v]).sum(axis=1)
    wgt=np.clip(cfg['edge_restriction']+(1-cfg['edge_restriction'])*pair_coh,0,1)
    flex=cov2@np.array([v['flexibility'] for v in scene['materials']])
    wgt*=cfg['resonant_transport']*np.sqrt(mass[u]*mass[v])
    wgt*=.8+.4*(flex[u]+flex[v])*.5
    wgt*=1+cfg['spin_coupling']*0.8*(speed[u]+speed[v])
    # Gauge potential A=(-B*y/2,B*x/2). Wilson loops reflect circulation.
    dx=x[v]-x[u];dy=y[v]-y[u];mx=(x[u]+x[v])/2-.5;my=(y[u]+y[v])/2-.5
    ang=cfg['theta_gauge']*.5*(-my*dx+mx*dy)
    uu=np.exp(1j*ang)
    # Multiplicative forcing; no reference pixel values in decoder.
    # Each material color is a typed cluster on the same 36D carrier.
    dphase=np.exp(1j*(1.5*phase+.2*speed+cfg['spin_coupling']*np.angle(pi_spin)))
    source=cov2 * dphase[:,None]
    # detuning + damping, diagonally dominant for stable Jacobi convergence
    nu=cfg['drive_frequency']; damp=cfg['damping']
    di=1.0+1j*nu*damp + .18*mass
    weight_sum=np.bincount(np.r_[u,v],weights=np.r_[wgt,wgt],minlength=n)
    den=di+weight_sum
    z=source.copy()
    for _ in range(cfg['iterations']):
        neigh=np.zeros((n,K),dtype=np.complex128)
        np.add.at(neigh,u,wgt[:,None]*uu[:,None]*z[v])
        np.add.at(neigh,v,wgt[:,None]*np.conj(uu)[:,None]*z[u])
        z=(source+neigh)/den[:,None]
    # residual of linear system (can compare with configured iterations)
    check=np.zeros((n,K),dtype=np.complex128)
    np.add.at(check,u,wgt[:,None]*uu[:,None]*z[v])
    np.add.at(check,v,wgt[:,None]*np.conj(uu)[:,None]*z[u])
    residual=float(np.linalg.norm(den[:,None]*z-check-source)/(np.linalg.norm(source)+1e-12))
    field=np.abs(z).reshape(HH,WW,K)
    # Coherent material fractions with anti-aliased polygon support.
    # Keep a bit of the geometrical drive to avoid eroding fine typography.
    optical=.60*cov+.40*(field/np.maximum(np.max(field,axis=-1,keepdims=True),1e-8))
    optical/=np.maximum(optical.sum(axis=-1,keepdims=True),1e-8)
    mix=cfg['cluster_mixing']
    if mix:
        rolled=np.roll(optical,1,axis=-1)
        optical=(1-mix)*optical+mix*rolled
    rgb_p=np.asarray([v['linear_rgb_reference'] for v in scene['materials']])
    sat=np.asarray([v['saturation'] for v in scene['materials']])
    contrast=np.asarray([v['contrast'] for v in scene['materials']])
    gray=(rgb_p*np.array([.2126,.7152,.0722])).sum(axis=1,keepdims=True)
    rgb_p=np.clip(gray+sat[:,None]*(rgb_p-gray),0,1)
    rgb_p=np.clip(.5+contrast[:,None]*(rgb_p-.5),0,1)
    out=optical@rgb_p
    # Transparency is a physical-material *model coefficient*, not a whole-
    # image fuzzy filter. Composite optical transmittance with paper substrate.
    opacity=np.asarray([v['opacity'] for v in scene['materials']])
    alpha=(optical@opacity).clip(0,1)
    paper=np.asarray(scene['materials'][int(np.argmax(gray))]['linear_rgb_reference'])
    out=alpha[:,:,None]*out+(1-alpha[:,:,None])*paper[None,None,:]
    # 2.5D: a depth field is *derived* from collective mass and occupancy,
    # not painted to match a semantic object.
    # Keep light change bounded, preserving readability of text.
    depth=0.025*(rho.reshape(HH,WW)-1.)+sum(
        (m['projection_z']*field[:,:,k] for k,m in enumerate(scene['materials'])))
    gy,gx=np.gradient(depth)
    light=(.6*gx+.8*gy)*cfg['projection_lighting']*10
    out=np.clip(out*(1+light[:,:,None]),0,1)
    diag={'residual_rel':residual,'nodes':n,'edges':len(u),
          'mass_range':[float(np.min(mass)),float(np.max(mass))],
          'spin_rate_range':[float(np.min(speed)),float(np.max(speed))],
          'nonzero_gauge_link_angle_mean':float(np.mean(np.abs(ang))),
          'config':cfg,'depth_range':[float(np.min(depth)),float(np.max(depth))]}
    return (np.uint8(np.rint(np.clip(out,0,1)*255)).reshape(HH,WW,3),diag)

def decode(scene,width=None,height=None,options=None,cover_supersample=2):
    validate(scene)
    w,h=scene['domain']['reference_grid']
    width=width or w;height=height or h
    if not (64<=width<=2048 and 64<=height<=3072):raise ValueError('output size')
    c=covers(scene,width,height,cover_supersample)
    img,stats=optical_solver(scene,c,options)
    return Image.fromarray(img,'RGB'),stats


def decode_highres(scene,width=1024,height=1536):
    """High-resolution geometric resampling with lower-resolution resonance.

    This is NOT a new high-resolution resonant solve. It resamples the original
    source-derived vector level sets at target size and projects low-frequency
    resonant optical corrections from the reference-sized grain field.
    """
    base_w,base_h=scene['domain']['reference_grid']
    lowcov=covers(scene,base_w,base_h,2)
    lowres,meta=optical_solver(scene,lowcov)
    palette=np.asarray([v['linear_rgb_reference'] for v in scene['materials']],float)
    lowgeom=lowcov@palette
    residual=lowres.astype(np.float32)/255-lowgeom
    highcov=covers(scene,width,height,2)
    highgeom=highcov@palette
    correction=cv2.resize(residual,(width,height),interpolation=cv2.INTER_CUBIC)
    out=np.uint8(np.rint(np.clip(highgeom+correction,0,1)*255))
    meta.update({'highres_projection':True,'highres_origin':'continuous vector support + interpolated lowres resonant correction',
                 'highres_native_resonator':False,'output_size':[width,height]})
    return Image.fromarray(out,'RGB'),meta


def metrics(ref,test):
    ref=np.asarray(ref,dtype=np.float32)
    arr=np.asarray(test,dtype=np.float32)
    mse=float(np.mean((ref-arr)**2))
    psnr=float(10*np.log10(255**2/mse)) if mse>0 else float('inf')
    score=float(ssim(ref.astype(np.uint8),arr.astype(np.uint8),channel_axis=2,data_range=255))
    e1=cv2.Canny(cv2.cvtColor(ref.astype(np.uint8),cv2.COLOR_RGB2GRAY),60,150)>0
    e2=cv2.Canny(cv2.cvtColor(arr.astype(np.uint8),cv2.COLOR_RGB2GRAY),60,150)>0
    # 1-px tolerance for detection, three-by-three overlap
    kernel=np.ones((3,3),np.uint8)
    ok1=((cv2.dilate(e2.astype(np.uint8),kernel)>0)&e1).sum()
    ok2=((cv2.dilate(e1.astype(np.uint8),kernel)>0)&e2).sum()
    precision=ok2/max(1,e2.sum());recall=ok1/max(1,e1.sum())
    f1=2*precision*recall/max(1e-12,precision+recall)
    return {'PSNR_dB':psnr,'SSIM':score,'edge_F1_tol1px':float(f1),
            'mse':mse,'reference_pixels':list(ref.shape[:2][::-1])}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,help='reference image for the ENCODER only')
    ap.add_argument('--scene',type=Path,required=True)
    ap.add_argument('--png',type=Path,required=True)
    ap.add_argument('--width',type=int,default=None)
    ap.add_argument('--height',type=int,default=None)
    args=ap.parse_args()
    args.png.parent.mkdir(parents=True,exist_ok=True);args.scene.parent.mkdir(parents=True,exist_ok=True)
    if args.input:
        scene=encode(args.input)
        args.scene.write_text(json.dumps(scene,sort_keys=True,separators=(',',':')),encoding='utf-8')
    else:
        scene=json.loads(args.scene.read_text(encoding='utf-8'))
    im,info=decode(scene,args.width,args.height)
    im.save(args.png)
    print(json.dumps({'png':str(args.png),'scene_bytes':args.scene.stat().st_size,
                      'png_sha256':sha(args.png),**info},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
