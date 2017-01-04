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


    def maybe_show_tooltip(self, view):
        try:
            html = self._compute_tooltip_html(view)
        except (KeyError, IndexError):
            self._last_html = ''
            view.hide_popup()
            return

        # The tooltips disappear automatically, no need to do anything her
        if not html:
            return

        if view.is_popup_visible():
            view.update_popup(html)
        else:
            view.show_popup(html, sublime.COOPERATE_WITH_AUTO_COMPLETE,
                            max_width=600, location=-1)


    def _compute_tooltip_html(self, view):
        # Get the line number of the first line of the first selection.
        row, col = current_pos(view)

        # on any vertical movement we force to see the tip
        if row != self._last_row:
            force = True

        self._last_row = row

        all_errors = persist.errors[view.id()]
        errors = all_errors[row]

        # if we're really on the error force displaying
        cols = [error[0] for error in errors]
        if col in cols:
            force = True

        messages = [error[1] for error in errors]
        html = get_html(messages)

        if not force and html == self._last_html:
            return
        self._last_html = html

        # print('New message:', html)

        return html


def get_html(messages):
    return (
        STYLESHEET +
        '<div class="error">' +
        ''.join('<span>' + m + '</span>' for m in messages) +
        '</div>'
    )


def current_pos(view):
    # Get the line number of the first line of the first selection.
    return view.rowcol(view.sel()[0].begin())
