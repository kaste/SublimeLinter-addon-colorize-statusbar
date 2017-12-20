from itertools import chain

import sublime
import sublime_plugin
from SublimeLinter.lint import persist

from . import settings
from .monkeypatch_sublimelinter import CatchSublimeLinterRuns


Settings = settings.Settings('SublimeLinter-DynamicUI')

STYLESHEET = '''
    <style>
        div.error {
            background-color: #af3912;
            background-color: transparent;
            font-size: .9em;

            color: #fff;
            padding: 0 1px;
            margin-left: 8px;
        }
    </style>
'''


class ShowTooltipsSublimeLinterCommand(sublime_plugin.EventListener,
                                       CatchSublimeLinterRuns):
    def __init__(self):
        self._last_row = -1
        self._last_html = ''

    def on_linter_finished_async(self, view):
        self.maybe_show_tooltip(view)

    def on_selection_modified_async(self, view):
        if not view.file_name():
            return

        sublime.set_timeout(lambda: self.maybe_show_tooltip(view), 1)

    def maybe_show_tooltip(self, view, force=False):
        # Get the line number of the first line of the first selection.
        row, col = current_pos(view)

        # on any vertical movement we force to see the tip
        if row != self._last_row:
            force = True
        self._last_row = row

        errors = get_errors_on_line(view, row)

        # if we're really on the error force displaying
        # if any(c == col for c, m in errors):
        #     force = True

        if errors:
            html = get_html(err['msg'] for err
                            in chain(errors['error'], errors['warning']))
        else:
            html = ''

        if force or html != self._last_html:
            display_popup(view, html)
        self._last_html = html


def display_popup(view, html):
    if not html:
        view.hide_popup()
        return

    if view.is_popup_visible():
        view.update_popup(html)
    else:
        row, _ = current_pos(view)
        last_char = last_char_of_row(view, row)
        view.show_popup(html, sublime.COOPERATE_WITH_AUTO_COMPLETE,
                        max_width=600, location=last_char)


def get_errors_on_line(view, row):
    try:
        return persist.errors[view.id()]['line_dicts'][row]
    except (KeyError, IndexError):
        return {}


def get_html(messages):
    return (
        STYLESHEET +
        '<div class="error">' +
        ''.join('<div>' + m + '</div>' for m in messages) +
        '</div>'
    )


def current_pos(view):
    # Get the line number of the first line of the first selection.
    return view.rowcol(view.sel()[0].begin())


def last_char_of_row(view, row):
    return (view.text_point(row + 1, 0) - 1)
