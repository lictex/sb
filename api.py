import requests
from . import preferences


def _api_url():
    return preferences.get().url.strip("/")


def get(url: str):
    return requests.get(f"{_api_url()}/{url.strip('/')}")


def post(url: str, json=None):
    return requests.post(f"{_api_url()}/{url.strip('/')}", json=json)


_enum_caches = {}


def clear_enum_caches():
    _enum_caches.clear()


def _enum_wrapper(s, f):
    def fn(self, context):
        if not _enum_caches.get(s):
            _enum_caches[s] = f()
        return [(x, x, "") for x in _enum_caches[s]]
    return fn


def _samplers_get():
    r = get("/sdapi/v1/samplers")
    return list((x["name"] for x in r.json()))


Samplers = _enum_wrapper("_samplers", _samplers_get)


def _upscalers_get():
    r = get("/sdapi/v1/upscalers")
    return list((x["name"] for x in r.json()))


Upscalers = _enum_wrapper("_upscalers", _upscalers_get)


def _hr_upscalers_get():
    r = get("/sdapi/v1/upscalers")
    return [
        *(
            "Latent",
            "Latent (antialiased)",
            "Latent (bicubic)",
            "Latent (bicubic antialiased)",
            "Latent (nearest)",
            "Latent (nearest-exact)",
        ),
        *(x["name"] for x in r.json())
    ]


HiResUpscalers = _enum_wrapper("_hr_upscalers", _hr_upscalers_get)


def _cnet_modules_get():
    r = get("/controlnet/module_list")
    return list(r.json()["module_list"])


CNetModules = _enum_wrapper("_cnet_modules", _cnet_modules_get)


def _cnet_models_get():
    r = get("/controlnet/model_list")
    return list(r.json()["model_list"])


CNetModels = _enum_wrapper("_cnet_models", _cnet_models_get)
