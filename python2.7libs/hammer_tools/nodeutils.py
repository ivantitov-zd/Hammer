from __future__ import print_function

import os
import tempfile

import hou

from .settings import SettingsManager

settings = SettingsManager.instance()


def playChopAudio(node):
    if settings.value('hammer.audio.play.use_external_player'):
        if node.type().name() == 'chopnet':
            nodes = node.glob('*')
            for node in nodes:
                if node.isAudioFlagSet():
                    break
        if node.type().name() == 'file':
            path = node.parm('file').eval()
            if os.path.exists(path) and path.endswith(('.wav', '.mp3')):
                os.startfile(path)
        else:
            _, path = tempfile.mkstemp('.wav', node.name() + '_', hou.getenv('TEMP'))
            node.saveClip(path)
            os.startfile(path)
    else:
        hou.audio.useTestMode()
        hou.audio.useChops()
        hou.audio.setChopPath(node.path())
        hou.audio.play()


def setSceneChopAudio(node):
    hou.audio.useTimeLineMode()
    hou.audio.useChops()
    hou.audio.setChopPath(node.path())
