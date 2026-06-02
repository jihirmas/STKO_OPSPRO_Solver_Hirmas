from PySide2 import QtCore, QtWidgets


_open_windows = {}


def show_floating_editor(component, parent=None):
    key = (component.className(), int(component.id))
    window = _open_windows.get(key)
    if window is None:
        window = component.dialog_class()(component=component, parent=parent)
        _open_windows[key] = window
        window.destroyed.connect(lambda *_: _open_windows.pop(key, None))
    else:
        setter = getattr(window, 'set_component', None)
        if callable(setter):
            setter(component)

    window.show()
    window.raise_()
    window.activateWindow()
    return window


def configure_floating_dialog(dialog: QtWidgets.QDialog):
    dialog.setWindowFlag(QtCore.Qt.Window, True)
    dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
    dialog.setModal(False)


def horizontal_line():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


def label(text):
    w = QtWidgets.QLabel(text)
    w.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    return w


def muted_label(text=''):
    w = QtWidgets.QLabel(text)
    w.setStyleSheet('color: gray; font-style: italic;')
    return w


def header(text):
    return QtWidgets.QLabel(f'<b>{text}</b>')

