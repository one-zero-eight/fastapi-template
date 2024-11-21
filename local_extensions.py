"""
Copy-pasted from (under MIT license):
https://github.com/dusktreader/cut-out-cookies/tree/main
"""

import jinja2
import jinja2.ext

STENCIL_PATH_PREFIX = "OBSCURATA_LAMINA_INTERRASILIS--"


class Stencil(jinja2.ext.Extension):
    counter = 0

    def __init__(self, environment, *args, **kwargs):
        @jinja2.pass_context
        def stencil(ctx, value, pattern):
            cookiecutter_config = ctx.get("cookiecutter", {})

            included = cookiecutter_config.get(f"__include_{pattern}", None)
            if isinstance(included, str):
                included = included.lower() == "true"
            return value if included else ""

        @jinja2.pass_context
        def stencil_path(ctx, value, pattern):
            rendered_value = stencil(ctx, value, pattern)
            if rendered_value == "":
                self.counter += 1
                return f"{STENCIL_PATH_PREFIX}{value}"
            return rendered_value

        environment.filters["stencil"] = stencil
        environment.filters["stencil_path"] = stencil_path
        super().__init__(environment)
