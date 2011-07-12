import webob.dec

MODES = {
    "RAW": 1,
    "SIMPLE": 2,
    "ADVANCED": 3,
    }

class Compile(object):

    def __init__(self, paths, mode = MODES["RAW"], *args, **kwargs):
        self.paths = paths
        self.mode = mode

    @webob.dec.wsgify
    def __call__(self, request):
        import pdb
        pdb.set_trace()
        return webob.Response(
            body = output, content_type = "application/javascript")
