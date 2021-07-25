from typing import Optional

from fastapi import BackgroundTasks, FastAPI
from fastapi import HTTPException

import glob
import os

app = FastAPI()

devices = {}
imgs = {}


@app.get("/")
def root():
    return {"msg": "We are the Borg. Resistance is futile."}


@app.get("/imgs")
def get_imgs():
    """Get available img files"""
    files = glob.glob("/srv/nfs/img/*.img")
    return files


@app.get("/add/{serial}")
def add_dev(serial: str):
    """Add device to database"""
    if serial in devices:
        raise HTTPException(status_code=404, detail=f"Device already in database")
    o = os.system(
        'echo "/srv/nfs/rpi4/boot /srv/tftpboot/{serial} none defaults,bind 0 0" >> /etc/fstab'
    )
    if o != 0:
        raise HTTPException(status_code=404, detail=f"Failed to add device to fstab")
    devices[serial] = False
    return {"status": True}


@app.get("/set/{serial}/{mode}")
def set_dev(serial: str, mode: bool):
    """Make boot files availabe or not-available"""
    if serial not in devices:
        raise HTTPException(status_code=404, detail=f"Device {serial} not in database")
    if mode:
        o = os.system("mount /srv/tftpboot/{serial}")
    else:
        o = os.system("unmount /srv/tftpboot/{serial}")
    if o != 0:
        raise HTTPException(status_code=404, detail=f"Failed to mount/umount device")
    devices[serial] = mode
    return {"status": True}


@app.get("/status/{serial}")
def get_status(serial: str):
    if serial not in devices:
        raise HTTPException(
            status_code=404, detail=f"Device with serial {serial} not found"
        )
    return {"serial": serial, "status": device[serial]}
