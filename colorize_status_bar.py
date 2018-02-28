import sublime
import sublime_plugin
from SublimeLinter.lint import persist, events, queue, WARNING, ERROR

from . import settings


Settings = settings.Settings('SublimeLinter-DynamicUI')
State = {}


def plugin_loaded():
    State.update({
        'active_view': sublime.active_window().active_view()
    })

    events.subscribe(events.LINT_RESULT, on_lint_result)


def plugin_unloaded():
    events.unsubscribe(events.LINT_RESULT, on_lint_result)


def on_lint_result(buffer_id, **kwargs):
    active_view = State['active_view']
    if active_view.buffer_id() == buffer_id:
        draw(buffer_id)


class ColorizeStatusbarSublimeLinterCommand(sublime_plugin.EventListener):
    def on_activated_async(self, active_view):
        bid = active_view.buffer_id()
        State.update({
            'active_view': active_view
        })

        draw(bid, immediate=True)


def draw(bid, immediate=False):
    if not Settings.get('colorize-statusbar', False):
        return

    current_errors = persist.errors[bid]
    flag = get_flag(current_errors)

    delay = CHILL_TIME if flag or not immediate else 0
    key = 'SL-ui-colorize-status-bar'
    queue.debounce(lambda: set_flag(flag), delay=delay, key=key)


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


CHILL_TIME = 10


def set_flag(flag):
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
