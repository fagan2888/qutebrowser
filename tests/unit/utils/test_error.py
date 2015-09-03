# Copyright 2015 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for qutebrowser.utils.error."""

import sys
import collections
import logging

import pytest

from qutebrowser.utils import error

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QMessageBox


Args = collections.namedtuple('Args', 'no_err_windows')


def test_no_err_windows(caplog):
    """Test handle_fatal_exc uwith no_err_windows = True."""
    try:
        raise ValueError("exception")
    except ValueError as e:
        with caplog.atLevel(logging.ERROR):
            error.handle_fatal_exc(e, Args(no_err_windows=True), 'title',
                                   pre_text='pre', post_text='post')
    msgs = [rec.message for rec in caplog.records()]
    assert msgs[0] == 'Handling fatal ValueError with --no-err-windows!'
    assert msgs[1] == 'title: title'
    assert msgs[2] == 'pre_text: pre'
    assert msgs[3] == 'post_text: post'


@pytest.mark.parametrize('pre_text, post_text, expected', [
    ('', '', 'exception'),
    ('foo', '', 'foo: exception'),
    ('foo', 'bar', 'foo: exception\n\nbar'),
    ('', 'bar', 'exception\n\nbar'),
])
def test_err_windows(qtbot, qapp, pre_text, post_text, expected):

    @pyqtSlot()
    def err_window_check():
        w = qapp.activeModalWidget()
        try:
            qtbot.add_widget(w)
            if sys.platform != 'darwin':
                assert w.windowTitle() == 'title'
            assert w.icon() == QMessageBox.Critical
            assert w.standardButtons() == QMessageBox.Ok
            assert w.text() == expected
        finally:
            w.close()

    QTimer.singleShot(0, err_window_check)
    error.handle_fatal_exc(ValueError("exception"), Args(no_err_windows=False),
                           'title', pre_text=pre_text, post_text=post_text)
