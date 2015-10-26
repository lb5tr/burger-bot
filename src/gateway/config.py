import json

class Config(object):
    def __init__(self, base_dir, env):
        d = self._load_config(base_dir, env)

        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b) if isinstance(b, dict) else b)

    def _load_config(self, base_dir, env):
        with open('%s%s.json'% (base_dir, env)) as f:
            data = f.read()
            return json.loads(data)
