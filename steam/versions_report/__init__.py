
import sys
from importlib.metadata import PackageNotFoundError, version as _pkg_version


def versions_report():
    """Print a report of al dependacy versions, and environment"""

    from steam import __version__
    print("steam: {}".format(__version__))

    # dependecy versions
    print("\nDependencies:")

    # Uses ``importlib.metadata.version`` — stdlib since py3.8, the
    # official replacement for the (now-deprecated) ``pkg_resources``
    # API which required setuptools at runtime and no longer ships
    # with modern Python installs.  ``version(name)`` raises
    # ``PackageNotFoundError`` when the distribution isn't installed;
    # we catch that to preserve the legacy "Not Installed" fallback.
    #
    # Dropped from the query list vs. the upstream fork:
    #   * ``enum34``       — py<3.4 stdlib backport, not needed on py3.13
    #   * ``win-inet-pton`` — py2.7 Windows shim, not needed on py3
    # Both were removed from ``pyproject.toml`` when this package was
    # ported from setuptools; querying them here would always miss.
    for dep in (
        "vdf",
        "protobuf",
        "requests",
        "cachetools",
        "gevent",
        "gevent-eventemitter",
        "pycryptodomex",
    ):
        try:
            dep_version = _pkg_version(dep)
        except PackageNotFoundError:
            dep_version = "Not Installed"
        print("{:>20}: {}".format(dep, dep_version))

    # python runtime
    print("\nPython runtime:")
    print("          executable: %s" % sys.executable)
    print("             version: %s" % sys.version.replace('\n', ''))
    print("            platform: %s" % sys.platform)

    # system info
    import platform

    print("\nSystem info:")
    print("              system: %s" % platform.system())
    print("             machine: %s" % platform.machine())
    print("             release: %s" % platform.release())
    print("             version: %s" % platform.version())
