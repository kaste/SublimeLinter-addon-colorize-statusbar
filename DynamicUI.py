import sublime
import sublime_plugin
from SublimeLinter.lint import highlight, persist

from . import settings


Settings = settings.Settings('DynamicUI')


class DynamicUICommand(sublime_plugin.EventListener):
    def __init__(self):
        self.views = {}
        self._last_lineno = -1
        self._last_message = ''


    def on_activated_async(self, view):
        if not view.file_name():
            return
        self.evaluate_linter_output(view)

    def on_selection_modified_async(self, view):
        if not view.file_name():
            return

        sublime.set_timeout(lambda: self.evaluate_linter_output(view), 1000)
        sublime.set_timeout(lambda: self.maybe_show_tooltip(view), 1)
        sublime.set_timeout(lambda: self.maybe_show_tooltip(view), 1000)

    def evaluate_linter_output(self, view):
        if not view.file_name():
            return

        # what's the correct way to find out if the view is actually not a
        # panel but a view? HACK
        if sublime.active_window().active_view().id() != view.id():
            return

        errors = view.get_regions(
            highlight.MARK_KEY_FORMAT.format(highlight.ERROR))
        if errors:
            # print(errors, errors[0].contains(view.sel()[0]))
            self.set_settings(True)
            return

        warnings = view.get_regions(
            highlight.MARK_KEY_FORMAT.format(highlight.WARNING))
        if warnings:
            self.set_settings(True)
            return

        self.set_settings(False)

    def set_settings(self, flag):
        settings = sublime.load_settings('Preferences.sublime-settings')
        if flag:
            settings.set('has_lint_errors', flag)
        else:
            settings.erase('has_lint_errors')


    def _compute_tooltip_html(self, view):
        # Get the line number of the first line of the first selection.
        rowcol = view.rowcol(view.sel()[0].begin())
        lineno = rowcol[0]

        # on any vertical movement we force to see the tip
        if lineno != self._last_lineno:
            self._last_message = ''

        self._last_lineno = lineno

        all_errors = persist.errors[view.id()]
        errors = all_errors[lineno]
        cols = [error[0] for error in errors]
        messages = [error[1] for error in errors]

        # if we're really on the error force displaying
        if rowcol[1] in cols:
            self._last_message = ''

        html = ('<div style="'
                # 'background-color: #e62d96; '
                'background-color: #af3912; '
                'color: #fff; '
                'padding: 0 4px">')
        for message in messages:
            html += "<div>{}</div>".format(message)

        html += "</div>"


        if html == self._last_message:
            return
        self._last_message = html

        # print('New message:', html)

        return html

    def maybe_show_tooltip(self, view):
        # print(view.sel()[0])
        try:
            html = self._compute_tooltip_html(view)
        except (KeyError, IndexError):
            self._last_message = ''
            view.hide_popup()
            return

        if not html:
            return

        if view.is_popup_visible():
            view.update_popup(html)
        else:
            view.show_popup(html, sublime.COOPERATE_WITH_AUTO_COMPLETE,
                            max_width=600, location=-1)





