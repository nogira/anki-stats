# package version
__version__ = "0.2.3"


from .tables import *
from .plots import *
from .stats import *
from .simulation import *

def db_path(path):
    full_db.path = path