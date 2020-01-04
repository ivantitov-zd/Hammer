from canvaseventtypes import *
import nodegraphview as view


def createEventHandler(uievent, pending_actions):
    print 123
    if isinstance(uievent, ContextEvent):
        editor = uievent.editor
        oldpath = uievent.oldcontext
        newpath = uievent.context
        view.handleNetworkChange(editor, oldpath, newpath, None, False)
        editor.setFootprints(editor.footprints() + hou.NetworkFootprint('hammer::action::1.0', hou.ui.colorFromName('GraphOutputHighlight'), 1, True))
        print 'Footprint edited'
        return None, True

    return None, False
