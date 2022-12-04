from um.settings.base import *

debug = os.environ.get('DEBUG', 'false').lower() == 'true'
if debug:
    from um.settings.dev import *
else:
    from um.settings.production import *
