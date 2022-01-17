import os
from loguru import logger
from PyQt5 import QtWidgets as qtw


def openSound(window):
    path, _ = qtw.QFileDialog.getOpenFileName(window, 'Open File', "sample.wav", "Sounds(*.wav)")
    return loadSound(path)


def parsePath(path):
    file_name = path.split(os.path.sep)[-1]
    dot_splits = file_name.split(".")
    extension = dot_splits[-1] if len(dot_splits) > 1 else ""
    name = "".join(dot_splits[0:-1])
    return name, extension


def loadSound(path):
    name, extension = parsePath(path)
    logger.info(name, extension)
    if extension == "wav":
        return True, name, path
    else:
        return False, None, None
