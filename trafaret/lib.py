import sys
import inspect


py3 = sys.version_info[0] == 3
py36 = sys.version_info >= (3, 6, 0)


if py3:
    getargspec = inspect.getfullargspec
    STR_TYPES = (str, bytes)
else:
    getargspec = inspect.getargspec
    STR_TYPES = (basestring,)  # noqa


_empty = object()


def py3metafix(cls):
    if not py3:
        return cls
    else:
        newcls = cls.__metaclass__(cls.__name__, (cls,), {})
        newcls.__doc__ = cls.__doc__
        return newcls


class WithContextCaller(object):
    def __init__(self, func):
        self.func = func
        if hasattr(self.func, 'async_call'):
            self.async_call = self.func.async_call

    def __call__(self, value, context=None):
        return self.func(value, context=context)


class WithoutContextCaller(WithContextCaller):
    def __call__(self, value, context=None):
        return self.func(value)


def with_context_caller(callble):
    if isinstance(callble, WithContextCaller):
        return callble
    if not inspect.isfunction(callble) and hasattr(callble, '__call__'):
        args = getargspec(callble.__call__).args
    else:
        args = getargspec(callble).args
    if 'context' in args:
        return WithContextCaller(callble)
    else:
        return WithoutContextCaller(callble)


def get_callable_args(fn):
    if inspect.isfunction(fn) or inspect.ismethod(fn):
        inspectable = fn
    elif inspect.isclass(fn):
        inspectable = fn.__init__
    elif hasattr(fn, '__call__'):
        inspectable = fn.__call__
    else:
        inspectable = fn
    try:
        spec = getargspec(inspectable)
    except TypeError:
        return ()
    # check if callble is bound method
    if hasattr(fn, '__self__'):
        spec.args.pop(0)  # remove `self` from args
    return spec.args
