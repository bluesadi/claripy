from __future__ import annotations

call_depth = 0


def _log(s):
    print("|  " * call_depth + s)


def _debugged(f):
    def debugged(*args, **kwargs):
        global call_depth

        _log(f.__name__ + " " + str(args) + " " + str(kwargs))
        call_depth += 1
        try:
            r = f(*args, **kwargs)
        except Exception as e:  # pylint:disable=broad-except
            r = f"EXCEPTION: {e!s}"
            raise
        finally:
            call_depth -= 1
            if r is not None:
                _log(r"\... " + str(r))

        if hasattr(r, "__iter__") and hasattr(r, "next"):
            return _debug_iterator(r)
        return r

    return debugged


def _debug_iterator(i):
    for v in i:
        _log("NEXT: " + str(v))
        yield v
    _log("FINISHED: " + str(i))


class DebugMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattribute__(self, a):
        o = super().__getattribute__(a)
        if a.startswith("__"):
            return o
        if callable(o):
            return _debugged(o)
        if hasattr(o, "__next__"):
            return _debug_iterator(o)
        return o


def debug_decorator(o):
    if isinstance(o, type):

        class Debugged(DebugMixin, o):
            pass

        Debugged.__name__ = "Debugged" + o.__name__
        return Debugged
    if callable(o):
        return _debugged(o)
    return None
