from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared limiter instance. Imported by both main.py (to register the
# exception handler/middleware) and individual routers (to decorate routes),
# so it lives in its own module to avoid a main.py <-> routers circular import.
limiter = Limiter(key_func=get_remote_address)
