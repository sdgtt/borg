from typing import Optional

from fastapi import BackgroundTasks, FastAPI
from fastapi import HTTPException
from borg.data import DB

import glob
import os

app = FastAPI()

def get_devices_list():
    return [ k for k in DB().get('devices').keys() ]

def sbool(v):
  return v.lower() in ("yes", "true", "t", "1")

@app.get("/imgs")
def get_imgs():
    """Get available img files"""
    files = glob.glob("/srv/nfs/img/*.img")
    return files

@app.get("/")
def root():
    return {"msg": "We are the Borg. Resistance is futile."}

@app.get("/devices")
def list_dev():
    """List registered devices"""
    return {"devices": DB().get('devices')}

@app.get("/add/{serial}")
def add_dev(serial: str):
    """Add device to database"""
    if serial in get_devices_list():
        raise HTTPException(status_code=403, detail=f"Device already in database")
    o = os.system(
        'echo "/srv/nfs/rpi4/boot /srv/tftpboot/{} none defaults,bind 0 0" >> /etc/fstab'.format(serial)
    )
    if o != 0:
        raise HTTPException(status_code=403, detail=f"Failed to add device to fstab")
    DB().add('devices', serial, 'False')
    return {"status": True}


@app.get("/set/{serial}/{mode}")
def set_dev(serial: str, mode: bool):
    """Make boot files availabe or not-available"""
    if serial not in get_devices_list():
        raise HTTPException(status_code=404, detail=f"Device {serial} not in database")
    if mode and not sbool(DB().get('devices')[serial]):
        o = os.system("mkdir -p /srv/tftpboot/{}; mount /srv/tftpboot/{}".format(serial,serial))
    elif not mode and sbool(DB().get('devices')[serial]):
        o = os.system("umount -f /srv/tftpboot/{}; rmdir /srv/tftpboot/{}".format(serial,serial))
    else:
        raise HTTPException(status_code=403, detail=f"Invalid request")
    if o != 0:
        raise HTTPException(status_code=500, detail=f"Failed to mount/umount device")
    DB().set('devices', serial, str(mode))
    return {"status": True}

@app.get("/status/{serial}")
def get_status(serial: str):
    if serial not in get_devices_list():
        raise HTTPException(
            status_code=404, detail=f"Device with serial {serial} not found"
        )
    return {"serial": serial, "status": sbool(DB().get('devices')[serial])}
