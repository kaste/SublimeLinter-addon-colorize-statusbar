
import sublime
import sublime_plugin

from SublimeLinter.lint import highlight, persist

from . import settings


Settings = settings.Settings('DynamicUI')


class ColorizeStatusbarSublimeLinterCommand(sublime_plugin.EventListener):
    def __init__(self):
        self._last_flag = None

    def on_activated_async(self, view):
        self.evaluate_linter_output(view)

    def on_selection_modified_async(self, view):
        sublime.set_timeout(lambda: self.evaluate_linter_output(view), 1000)

    def evaluate_linter_output(self, view):
        if not Settings.get('colorize-statusbar', False):
            return
        if not view.file_name():
            return

        # Filter out panels;
        # Also, since we used set_timeout above, ensure the user did not change
        # the active view
        if sublime.active_window().active_view().id() != view.id():
            return

        if view.get_regions(
                highlight.MARK_KEY_FORMAT.format(highlight.ERROR)):
            self.set_settings('errors')

        elif view.get_regions(
                highlight.MARK_KEY_FORMAT.format(highlight.WARNING)):
            self.set_settings('warnings')
        else:
            self.set_settings()

    def set_settings(self, flag=None):
        if flag == self._last_flag:
            return
        self._last_flag = flag

        on_errors = Settings.get('set_on_errors')
        on_warnings = Settings.get('set_on_warnings')

        settings = sublime.load_settings('Preferences.sublime-settings')
        if flag == 'errors':
            settings.set(on_errors, True)
            settings.erase(on_warnings)
        elif flag == 'warnings':
            settings.set(on_warnings, True)
            settings.erase(on_errors)
        else:
            settings.erase(on_errors)
            settings.erase(on_warnings)


