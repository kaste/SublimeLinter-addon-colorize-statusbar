import sublime
import sublime_plugin
from SublimeLinter.lint import persist, events, queue, WARNING, ERROR

from . import settings


CHILL_TIME = 3
DEBOUNCE_KEY = 'SL-ui-colorize-status-bar'


Settings = settings.Settings('SublimeLinter-DynamicUI')
State = {}


def plugin_loaded():
    State.update({'active_view': sublime.active_window().active_view()})

    events.subscribe(events.LINT_RESULT, on_lint_result)


def plugin_unloaded():
    events.unsubscribe(events.LINT_RESULT, on_lint_result)


def on_lint_result(buffer_id, **kwargs):
    active_view = State['active_view']
    if active_view.buffer_id() == buffer_id:
        draw(buffer_id)


class ColorizeStatusbarSublimeLinterCommand(sublime_plugin.EventListener):
    def on_activated_async(self, active_view):
        if active_view.settings().get('is_widget'):
            return

        bid = active_view.buffer_id()
        State.update({'active_view': active_view})

        draw(bid, immediate=True)


def draw(bid, immediate=False):
    if not Settings.get('flags', False):
        return

    current_errors = persist.errors[bid]
    flag = get_flag(current_errors)

    delay = CHILL_TIME if (flag and not immediate) else 0
    queue.debounce(lambda: set_flag(flag), delay=delay, key=DEBOUNCE_KEY)


def get_flag(errors):
    has_warnings = False
    for error in errors:
        if error['error_type'] == ERROR:
            return 'errors'

        if error['error_type'] == WARNING:
            has_warnings = True

    if has_warnings:
        return 'warnings'
    else:
        return None


def set_flag(flag):
    on_errors = Settings.get('flag_on_errors')
    on_warnings = Settings.get('flag_on_warnings')

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
