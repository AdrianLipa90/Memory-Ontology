from __future__ import annotations
import hashlib, math
import numpy as np
DIM=36
TAU=2.0*math.pi
KAPPA=math.log(2.0)/(24.0*math.pi)

def phase36(value)->np.ndarray:
    if isinstance(value,np.ndarray):
        a=np.asarray(value,dtype=np.float64).reshape(-1)
        if a.size!=DIM or not np.isfinite(a).all(): raise ValueError("invalid 36D vector")
        return np.mod(a,TAU)
    raw=hashlib.shake_256(str(value).encode()).digest(DIM*8)
    u=np.frombuffer(raw,dtype='<u8').astype(np.float64)
    return (u/np.float64(2**64-1))*TAU

def batch_phase36(labels)->np.ndarray:
    labels=list(labels)
    if not labels:return np.empty((0,DIM),dtype=np.float64)
    # Fixed-size binary conversion in one dense ndarray after deterministic XOF generation.
    raw=b''.join(hashlib.shake_256(str(x).encode()).digest(DIM*8) for x in labels)
    u=np.frombuffer(raw,dtype='<u8').reshape(len(labels),DIM).astype(np.float64)
    return (u/np.float64(2**64-1))*TAU

def order_parameter(v):
    a=np.asarray(v,dtype=np.float64)
    if a.ndim==1:a=a.reshape(1,-1)
    return np.abs(np.exp(1j*a).mean(axis=1))

def circular_distance_matrix(a,b):
    aa=np.asarray(a,dtype=np.float64)[:,None,:]
    bb=np.asarray(b,dtype=np.float64)[None,:,:]
    d=np.angle(np.exp(1j*(aa-bb)))
    return np.sqrt(np.mean(d*d,axis=2))

def batch_sha256(blobs):
    return [hashlib.sha256(bytes(x)).hexdigest() for x in blobs]
