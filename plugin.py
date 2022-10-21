import sublime
import sublime_plugin
from SublimeLinter.lint import persist, events, util, queue, WARNING, ERROR


MYPY = False
if MYPY:
    from typing import TypedDict

    State_ = TypedDict("State_", {"active_view": sublime.View}, total=False)


CHILL_TIME = 0
DEBOUNCE_KEY = 'SL-ui-colorize-status-bar'


Settings = None  # type: sublime.Settings  # type: ignore[assignment]
State = {}  # type: State_


def plugin_loaded():
    global Settings
    Settings = sublime.load_settings(
        'SublimeLinter-addon-colorize-statusbar.sublime-settings'
    )
    State.update(
        {
            'active_view': (
                sublime.active_window().active_view() or sublime.View(-1)
            )
        }
    )

    events.subscribe(events.LINT_RESULT, on_lint_result)


def plugin_unloaded():
    events.unsubscribe(events.LINT_RESULT, on_lint_result)


def on_lint_result(filename, **kwargs):
    active_view = State['active_view']
    if util.canonical_filename(active_view) == filename:
        draw(filename)


class ColorizeStatusbarSublimeLinterCommand(sublime_plugin.EventListener):
    def on_activated_async(self, active_view: sublime.View) -> None:
        if active_view.settings().get('is_widget'):
            return

        State.update({'active_view': active_view})

        filename = util.canonical_filename(active_view)
        draw(filename, immediate=True)


def draw(filename: str, immediate: bool = False) -> None:
    if not Settings.get('flags', False):
        return

    current_errors = persist.file_errors[filename]
    linters_to_ignore = Settings.get('linters_to_ignore') or []
    only_if_errors_outside_of_visible_region = Settings.get(
        'only_if_errors_outside_of_visible_region', True
    )
    visible_region = State["active_view"].visible_region()
    flag = (
        None
        # The idea is that if an error is within the `visible_region`
        # the user already is notified and disturbed enough and
        # does not need any further visual hint.  So `None` is the
        # correct answer then.
        if (
            only_if_errors_outside_of_visible_region
            and any(
                error
                for error in current_errors
                if visible_region.contains(error["region"])
            )
        )
        else get_flag(
            error
            for error in current_errors
            if error["linter"] not in linters_to_ignore
        )
    )

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
    assert on_errors
    assert on_warnings

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
