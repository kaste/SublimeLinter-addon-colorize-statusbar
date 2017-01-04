import sublime
import sublime_plugin
from SublimeLinter.lint import persist

from . import settings


Settings = settings.Settings('DynamicUI')

STYLESHEET = '''
    <style>
        div.error {
            background-color: #af3912;
            color: #fff;
            padding: 0 4px;
        }
    </style>
'''

class ShowTooltipsSublimeLinterCommand(sublime_plugin.EventListener):
    def __init__(self):
        self._last_row = -1
        self._last_html = ''


    def on_selection_modified_async(self, view):
        if not view.file_name():
            return

        sublime.set_timeout(lambda: self.maybe_show_tooltip(view), 1)
        sublime.set_timeout(lambda: self.maybe_show_tooltip(view), 1000)


    def maybe_show_tooltip(self, view, force=False):
        # Get the line number of the first line of the first selection.
        row, col = current_pos(view)

        # on any vertical movement we force to see the tip
        if row != self._last_row:
            force = True
        self._last_row = row

        errors = get_errors_on_line(view, row)

        # if we're really on the error force displaying
        if any(c == col for c, m in errors):
            force = True

        html = get_html(m for c, m in errors) if errors else ''
        if force or html != self._last_html:
            display_popup(view, html)
        self._last_html = html


def display_popup(view, html):
    # The tooltips disappear automatically, no need to do anything here
    if not html:
        return

    if view.is_popup_visible():
        view.update_popup(html)
    else:
        view.show_popup(html, sublime.COOPERATE_WITH_AUTO_COMPLETE,
                        max_width=600, location=-1)


def get_errors_on_line(view, row):
    try:
        errors_by_view = persist.errors[view.id()]
        return errors_by_view[row]
    except (KeyError, IndexError):
        return []

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
