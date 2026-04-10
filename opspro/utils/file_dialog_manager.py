"""
file_dialog_manager.py
-----------------------
Python equivalent of the C++ ``AsFileDialogManager`` class (AsWidgets library).

Provides a set of static helpers around :class:`QFileDialog` that
automatically remember the last-used directory (persisted via
:class:`QSettings`) and restore it each time a dialog is opened.

The *context* mechanism lets callers tag a dialog call with a logical name
(e.g. ``"ImportModel"``, ``"ExportReport"``) so that each context
independently tracks its own last-used directory.  After every successful
dialog call the context is automatically reset to ``"General"``.

Typical usage
-------------
::

    # optional: set a context before opening the dialog
    FileDialogManager.set_context('ImportModel')
    path = FileDialogManager.get_open_file_name(
        parent, 'Open model', 'Model files (*.mpco *.json)'
    )

    # save dialog – extension is appended automatically when omitted
    out = FileDialogManager.get_save_file_name(
        parent, 'Save report', 'Excel (*.xlsx);;CSV (*.csv)'
    )
"""

from PySide2 import QtCore, QtWidgets


class FileDialogManager(QtCore.QObject):
    """
    Static helper providing :class:`QFileDialog` wrappers that remember
    the last-used directory per named context (persisted in
    :class:`QSettings`).

    All public methods are *static* and mirror the C++ ``AsFileDialogManager``
    API.  The class also exposes a small set of *instance* methods
    (``run_*``) intended for cross-thread use via signal/slot connections –
    the result is stored in :attr:`file_name` for later retrieval.
    """

    # ------------------------------------------------------------------
    # Internal class-level state  (equivalent to the C++ static variable)
    # ------------------------------------------------------------------
    _current_context: str = 'General'

    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self._filename: str = ''
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to initialize FileDialogManager:\n{e}')

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_last_dir() -> str:
        """Read the last-used directory for the current context from QSettings."""
        try:
            settings = QtCore.QSettings()
            settings.beginGroup('FileDialogManager')
            settings.beginGroup(FileDialogManager._current_context)
            retval = settings.value('LastDirectory', '')
            settings.endGroup()
            settings.endGroup()
            return retval or ''
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to get last directory:\n{e}')
            return ''

    @staticmethod
    def _save_current_dir(filename: str):
        """
        Persist the parent directory of *filename* for the current context,
        then reset the context to ``"General"``.
        """
        try:
            if not filename:
                return
            directory = QtCore.QFileInfo(filename).absoluteDir()
            if not directory.exists():
                return
            settings = QtCore.QSettings()
            settings.beginGroup('FileDialogManager')
            settings.beginGroup(FileDialogManager._current_context)
            settings.setValue('LastDirectory', directory.absolutePath())
            settings.endGroup()
            settings.endGroup()
            FileDialogManager.set_context('')  # reset to General
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to save current directory:\n{e}')

    # ------------------------------------------------------------------
    # Public static API
    # ------------------------------------------------------------------

    @staticmethod
    def set_context(context: str):
        """
        Set the named context used to look up / store the last-used
        directory.  Pass an empty string to reset to the default
        ``"General"`` context.
        """
        try:
            FileDialogManager._current_context = context if context else 'General'
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to set context:\n{e}')

    @staticmethod
    def get_open_file_name(
        parent: QtWidgets.QWidget = None,
        caption: str = '',
        filter: str = '',
        selected_filter: list = None,
        options: QtWidgets.QFileDialog.Options = QtWidgets.QFileDialog.Options(),
    ) -> str:
        """
        Wrap :func:`QFileDialog.getOpenFileName`, starting in the
        remembered last-used directory.

        Parameters
        ----------
        selected_filter : list, optional
            A one-element list.  On entry its first element (if any) is
            used as the initially selected filter; on return it is
            overwritten with the filter the user actually selected.
            Mirrors the ``QString *selectedFilter`` C++ parameter.

        Returns
        -------
        str
            The chosen filename, or an empty string if cancelled.
        """
        try:
            sf_in = selected_filter[0] if selected_filter else ''
            retval, sf_out = QtWidgets.QFileDialog.getOpenFileName(
                parent, caption,
                FileDialogManager._get_last_dir(),
                filter, sf_in, options,
            )
            if selected_filter is not None:
                selected_filter[0] = sf_out
            FileDialogManager._save_current_dir(retval)
            return retval
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to open file dialog:\n{e}')
            return ''

    @staticmethod
    def get_save_file_name(
        parent: QtWidgets.QWidget = None,
        caption: str = '',
        filter: str = '',
        selected_filter: list = None,
        options: QtWidgets.QFileDialog.Options = QtWidgets.QFileDialog.Options(),
        suggested_dir: str = None,
    ) -> str:
        """
        Wrap :func:`QFileDialog.getSaveFileName`, starting in the
        remembered last-used directory.

        .. note::
            On some platforms (notably Linux) the chosen filter extension is
            *not* appended automatically to the filename.  This method
            replicates the C++ fix: when the user did not type any extension,
            the first valid extension from the selected filter (or the first
            valid entry in *filter*) is appended automatically.

        Parameters
        ----------
        selected_filter : list, optional
            Same semantics as in :meth:`get_open_file_name`.
        suggested_dir : str, optional
            When given, overrides the remembered last-used directory for
            this single call only.

        Returns
        -------
        str
            The chosen filename (with extension guaranteed), or an empty
            string if cancelled.
        """
        try:
            sf_in = selected_filter[0] if selected_filter else ''
            the_dir = suggested_dir if suggested_dir else FileDialogManager._get_last_dir()

            retval, sf_out = QtWidgets.QFileDialog.getSaveFileName(
                parent, caption, the_dir, filter, sf_in, options
            )

            if selected_filter is not None:
                selected_filter[0] = sf_out

            # ---- auto-append missing extension ---------------------------
            if retval:
                if not QtCore.QFileInfo(retval).completeSuffix():
                    def _first_ext_from(the_filter: str) -> str:
                        """
                        Extract the first non-wildcard extension from a single
                        filter string like ``"Excel workbook (*.xlsx *.xls)"``.
                        Returns an empty string when no valid extension is found
                        (e.g. ``"All files (*.*)"`` or ``"All files (*)"``).
                        """
                        parts = the_filter.split('(', 1)
                        if len(parts) == 2:
                            inner = parts[1].replace(')', '').replace('*', '').replace('.', '')
                            exts = [e for e in inner.split() if e]
                            if exts:
                                return exts[0]
                        return ''

                    # start with the filter the user actually selected
                    ext = _first_ext_from(sf_out)
                    if not ext:
                        # fall back to the first valid filter in the full list
                        for token in (t for t in filter.split(';;') if t):
                            ext = _first_ext_from(token)
                            if ext:
                                break
                    if ext:
                        retval = f'{retval}.{ext}'

            FileDialogManager._save_current_dir(retval)
            return retval
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to save file dialog:\n{e}')
            return ''

    @staticmethod
    def get_existing_directory(
        parent: QtWidgets.QWidget = None,
        caption: str = '',
        options: QtWidgets.QFileDialog.Options = QtWidgets.QFileDialog.ShowDirsOnly,
    ) -> str:
        """
        Wrap :func:`QFileDialog.getExistingDirectory`, starting in the
        remembered last-used directory.

        Returns
        -------
        str
            The chosen directory path, or an empty string if cancelled.
        """
        try:
            retval = QtWidgets.QFileDialog.getExistingDirectory(
                parent, caption,
                FileDialogManager._get_last_dir(),
                options,
            )
            FileDialogManager._save_current_dir(retval)
            return retval
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to open directory dialog:\n{e}')
            return ''

    @staticmethod
    def get_open_file_names(
        parent: QtWidgets.QWidget = None,
        caption: str = '',
        filter: str = '',
        selected_filter: list = None,
        options: QtWidgets.QFileDialog.Options = QtWidgets.QFileDialog.Options(),
    ) -> list:
        """
        Wrap :func:`QFileDialog.getOpenFileNames`, starting in the
        remembered last-used directory.

        Parameters
        ----------
        selected_filter : list, optional
            Same semantics as in :meth:`get_open_file_name`.

        Returns
        -------
        list[str]
            The chosen filenames, or an empty list if cancelled.
        """
        try:
            sf_in = selected_filter[0] if selected_filter else ''
            retval, sf_out = QtWidgets.QFileDialog.getOpenFileNames(
                parent, caption,
                FileDialogManager._get_last_dir(),
                filter, sf_in, options,
            )
            if selected_filter is not None:
                selected_filter[0] = sf_out
            if retval:
                FileDialogManager._save_current_dir(retval[0])
            return retval
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to open files dialog:\n{e}')
            return []

    # ------------------------------------------------------------------
    # Instance methods  (equivalent to the C++ Qt slots)
    #
    # Intended for cross-thread use: connect a worker-thread signal to
    # one of these slots so the dialog is shown on the GUI thread.
    # The result is stored in ``self._filename`` and accessible via the
    # ``file_name`` property.
    # ------------------------------------------------------------------

    def run_open_file_name(
        self,
        parent: QtWidgets.QWidget = None,
        caption: str = '',
        filter: str = '',
    ):
        """Open a file dialog and store the result in :attr:`file_name`."""
        try:
            self._filename = FileDialogManager.get_open_file_name(parent, caption, filter)
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to run open file dialog:\n{e}')

    def run_msg_box_info(
        self,
        parent: QtWidgets.QWidget = None,
        caption: str = '',
        msg: str = '',
    ):
        """Show a :func:`QMessageBox.information` dialog."""
        try:
            QtWidgets.QMessageBox.information(parent, caption, msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to show info message box:\n{e}')

    def run_msg_box_warning(
        self,
        parent: QtWidgets.QWidget = None,
        caption: str = '',
        msg: str = '',
    ):
        """Show a :func:`QMessageBox.warning` dialog."""
        try:
            QtWidgets.QMessageBox.warning(parent, caption, msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to show warning message box:\n{e}')

    @property
    def file_name(self) -> str:
        """Filename stored by the last :meth:`run_open_file_name` call."""
        try:
            return self._filename
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'Error', f'Failed to get file name:\n{e}')
            return ''
