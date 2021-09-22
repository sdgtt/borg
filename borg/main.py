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

@app.get("/")
def root():
    return {"msg": "We are the Borg. Resistance is futile."}

@app.get("/imgs")
def get_images():
    """Get available img files"""
    files = glob.glob("/imgs/kuiper/*")
    return {
        "available": files, 
        "help": "To load image, call /imgs/load/<image_name>.img" 
    }

@app.get("/imgs/loaded")
def get_loaded_imgs():
    """Get loaded image information"""
    files = glob.glob("/srv/nfs/img/*.img")
    if len(files) == 0:
        raise HTTPException(status_code=404, detail=f"No image is currently loaded")
    return {
        "loaded": files,
        "help": "To unload image, call /imgs/unload"
    }

@app.get("/imgs/load/{image}")
def load_image(image: str):
    """Load reference image"""
    if len(glob.glob("/srv/nfs/img/*.img")) > 0:
        raise HTTPException(status_code=403, detail=f"An image is currently loaded, please execute /imgs/unload first!")
    o = os.system(
        'mv /imgs/kuiper/{} /srv/nfs/img/'.format(image)
    )
    if o != 0:
        raise HTTPException(status_code=500, detail=f"Failed loading image")
    return {"status": True}

@app.get("/imgs/unload")
def unload_image():
    """Unload reference image"""
    if len(glob.glob("/srv/nfs/img/*.img")) != 1:
        raise HTTPException(status_code=403, detail=f"No image to unload!")
    file = glob.glob("/srv/nfs/img/*.img")[0]
    o = os.system(
        'mv {} /imgs/kuiper/'.format(file)
    )
    if o != 0:
        raise HTTPException(status_code=403, detail=f"Failed to unload image")
    return {"status": True}

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
        raise HTTPException(status_code=500, detail=f"Failed to add device to fstab")
    DB().add('devices', serial, 'False')
    return {"status": True}

@app.get("/remove/{serial}")
def remove_dev(serial: str):
    """Remove serial from database"""
    if not serial in get_devices_list():
        raise HTTPException(status_code=404, detail=f"Device not yet registed. Try to add it first")
    if sbool(DB().get('devices')[serial]):
        raise HTTPException(status_code=403, detail=f"Device is currently active. Deactivate device first")
    o = os.system(
        "sed '/{}/d' -in /etc/fstab".format(serial)
    )
    if o != 0:
        raise HTTPException(status_code=500, detail=f"Failed to remove device from fstab")
    DB().remove('devices', serial)
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
