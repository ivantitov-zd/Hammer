import hou


def setRampParmInterpolation(parm, basis):
    """Sets interpolation for all knots."""
    try:
        source_ramp = parm.evalAsRamp()
        bases = (basis,) * len(source_ramp.basis())
        new_ramp = hou.Ramp(bases, source_ramp.keys(), source_ramp.values())
        parm.set(new_ramp)
    except hou.PermissionError:
        pass
