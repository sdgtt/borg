import pickledb

DBNAME='borg.db'

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class DB:
    """
        Class handling data model and DB access
        The following is the data structure for the borg application
        {
            "devices" : {
                "deviceserial1" : "<status>[True/False]",
                ...
            }
            "images" : {
                "image name: " "<status>[True/False]",
                ...
            }
        }    
        
    """
    def __init__(self):
        self.db = pickledb.load(DBNAME, False, False)
        keys = self.db.getall()
        if not "devices" in keys:
            if not self.db.dcreate('devices'):
                raise Exception("Error creating \"devices\ entry")
        if not "images" in keys:
            if not self.db.dcreate('images'):
                raise Exception("Error creating \"images\" entry")
        self.db.dump()

    def get_db(self):
        """Return db object"""
        return self.db

    def get(self, dct):
        """Get all key-value pair in a given dictionary from db"""
        return self.db.dgetall(dct)


    def add(self, dct, key, val):
        """Add a key-value pair to a given dictionary """
        _data = (key, val)
        if self.db.dexists(dct,key):
            raise ValueError("{} is already present".format(key))
        if self.db.dadd(dct,_data):
            self.db.dump()
            return _data

    def remove(self, dct, key):
        """Remove a key-value pair to a given dictionary """
        if not self.db.dexists(dct,key):
            raise KeyError("{} is not found".format(key))
        val = self.db.dpop(dct,key)
        self.db.dump()
        return {key, val}

    def set(self, dct, key, val):
        """Set/update and existing value to a key on a given dictionary"""
        if not self.db.dexists(dct,key):
            raise KeyError("{} is not found".format(key))
        if self.db.dpop(dct,key):
            _data = self.add(dct, key, val)
            self.db.dump()
            return _data
