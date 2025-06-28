from jinja2 import Environment, StrictUndefined
from jinja2.ext import Extension


class SetStrictUndefined(Extension):
    def __init__(self, env: "Environment"):
        super().__init__(env)
        env.undefined = StrictUndefined
