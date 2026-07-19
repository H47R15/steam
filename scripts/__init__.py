"""Dev-only helpers exposed as poetry console scripts.

See ``pyproject.toml``'s ``[tool.poetry.scripts]`` block for the console
entries (``pb-fetch`` / ``pb-compile`` / ``pb-services`` / ``pb-gen-enums``
/ ``pb-update``).  Each is a thin wrapper around one of this package's
``main()`` functions.
"""
