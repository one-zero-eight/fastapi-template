# API version
VERSION = "0.1.0"

# Info for OpenAPI specification
SUMMARY = "{{ cookiecutter.project_name.title() }} API"

DESCRIPTION = """
### About this project

This is the API for {{ cookiecutter.project_name.title() }} project developed by one-zero-eight community.
"""

CONTACT_INFO = {
    "name": "one-zero-eight (Telegram)",
    "url": "https://t.me/one_zero_eight",
}
LICENSE_INFO = {
    "name": "MIT License",
    "identifier": "MIT",
}

TAGS_INFO: list[dict] = []
'''
On each new tag add description to TAGS_INFO, f.e.

```python
"""
Some description of the module with new tag.
"""
docs.TAGS_INFO.append({"description": __doc__, "name": str(router.tags[0])})
```

'''
