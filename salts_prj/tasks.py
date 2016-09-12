# -*- coding: utf-8 -*-

import atexit
import Queue
import threading
from tank_api_client import TankClientError


errors = {'TankClient': []}


def _worker():
    while True:
        func, args, kwargs = _queue.get()
        try:
            func(*args, **kwargs)
        except TankClientError, err:
            errors['TankClient'].append({'host': err.host,
                                         'port': err.port,
                                         'message': str(err)})
        except Exception, exc:
            import traceback
            details = traceback.format_exc()
        finally:
            _queue.task_done()


def postpone(func):
    def decorator(*args, **kwargs):
        _queue.put((func, args, kwargs))
    return decorator


_queue = Queue.Queue()
_thread = threading.Thread(target=_worker)
_thread.daemon = True
_thread.start()


def _cleanup():
    _queue.join()


atexit.register(_cleanup)
