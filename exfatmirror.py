#!/usr/bin/env python3

# Recursively copy from src to dst, sanitising subpaths for ExFAT compatibility.
# Skip existing destination dirs/files.

# Unoptimised wrt Path calculations but who cares because severely io-bound.

import sys, os, os.path, shutil
from pathlib import Path

changes = dict()

def sanitise(name):
    """Drop characters not allowed in ExFAT filenames and limit to 255 chars including extension.
    Can be used for filenames or dirnames, but not paths.
    See https://en.wikipedia.org/wiki/ExFAT ."""
    # remove disallowed characters
    characters = ''.join(l for l in name if (ord(l) >= 32) and (l not in '/\\:*?"<>|'))
    path = Path(characters)
    # number of characters available for stem
    available = 255 - len(path.suffix)
    ret = path.stem[:available] + path.suffix
    if name != ret: changes[name] = ret
    return ret

def destination(src, dst, path):
    """Calculate destination path under `dst` from absolute `path` with respect to `src`,
    sanitising parts deep to `src`."""
    s = Path(src)
    sp = s.parts
    d = Path(dst)
    p = Path(path)
    pp = p.parts
    assert pp[:len(sp)] == sp
    sanitise_parts = pp[len(sp):]
    rp = [d] + [sanitise(p) for p in sanitise_parts]
    return Path(*rp)

def step(src, dst, walkstep): # TODO return data from which report can be constructed
    root, dirs, files = walkstep
    dst_root = destination(src, dst, root)
    for d in dirs:
        if d.startswith('.'): continue 
        dst_d = destination(src, dst, Path(root, d))
        if os.path.exists(dst_d):
            print('skipping: ' + d + ' -> ' + str(dst_d))
            continue
        print('creating: ' + d + ' -> ' + str(dst_d))
        os.mkdir(dst_d)
    for f in files:
        if f.startswith('.'): continue
        dst_f = destination(src, dst, Path(root, f))
        if os.path.exists(dst_f):
            continue
        print('copying: ' + f + ' -> ' + str(dst_f))
        shutil.copy(Path(root,f), dst_f)

if __name__ == "__main__":
    src, dst = sys.argv[:2]
    assert(os.path.exists(src))
    assert(os.path.exists(dst))
    for w in os.walk(src):
        step(src, dst, w)
