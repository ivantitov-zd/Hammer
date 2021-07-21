import hou

major_version, minor_version, build_version = hou.applicationVersion()

if major_version < 16:
    _icon_backend = hou.ui.createQtIcon
elif major_version < 17:
    _icon_backend = hou.qt.createIcon
else:
    _icon_backend = hou.qt.Icon


def icon(name, size=32, fallback_name='NETVIEW_debug'):
    """Create and return a new icon for the specified Houdini icon name."""
    try:
        return _icon_backend(name, size, size)
    except hou.OperationFailed:
        pass
    try:
        return _icon_backend(fallback_name, size, size)
    except hou.OperationFailed:
        return _icon_backend('NETVIEW_debug', size, size)


if major_version == 16 and minor_version == 5 or major_version > 16:
    _scale_backend = hou.ui.scaledSize
    scale_factor_backend = hou.ui.globalScaleFactor
else:
    _scale_backend = None
    scale_factor_backend = None


def scaled(size):
    """Scale the specified size by the global UI scale factor and return the scaled size."""
    if not _scale_backend:
        return size

    return _scale_backend(size)


def scale():
    """Return the scale factor that is set by Houdini`s Global UI Size preference."""
    if not _scale_backend:
        return 1.0

    return scale_factor_backend()
