import sublime
import sublime_plugin
from .monkeypatch_sublimelinter import CatchSublimeLinterRuns
from SublimeLinter.lint import persist

from . import settings


Settings = settings.Settings('SublimeLinter-DynamicUI')


class ColorizeStatusbarSublimeLinterCommand(sublime_plugin.EventListener,
                                            CatchSublimeLinterRuns):

    def on_activated_async(self, view):
        self.evaluate_linter_output(view)

    def on_linter_finished_async(self, view):
        self.evaluate_linter_output(view)

    def evaluate_linter_output(self, view):
        if not Settings.get('colorize-statusbar', False):
            return
        if not view.file_name():
            return

        try:
            current_errors = persist.errors[view.id()]['we_count_view']
        except KeyError:
            return

        if current_errors['error'] > 0:
            self.set_settings('errors')
        elif current_errors['warning'] > 0:
            self.set_settings('warnings')
        else:
            self.set_settings()

    def set_settings(self, flag=None):
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
