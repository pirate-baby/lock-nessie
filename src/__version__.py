import os

release_version = os.getenv("RELEASE_VERSION")
assert release_version, "RELEASE_VERSION envar is not set, unable to determine version"

__version__ = release_version