from SublimeLinter.lint import persist
from SublimeLinter.highlight_view import (
    extract_uid_from_key,
    get_regions_keys,
    HIDDEN_STYLE_MARKER,
    DEMOTE_WHILE_BUSY_MARKER,
    State as MarkerState,
)


def get_visible_error_ids(view):
    if view.id() in MarkerState['quiet_views']:
        return set()

    idle = view.id() in MarkerState['idle_views']
    return {
        extract_uid_from_key(key)
        for key in get_regions_keys(view)
        if (
            '.Highlights.' in key
            and HIDDEN_STYLE_MARKER not in key
            # Select visible highlights; when `idle` all regions
            # are visible, otherwise all *not* demoted regions.
            and (idle or DEMOTE_WHILE_BUSY_MARKER not in key)
        )
        for region in view.get_regions(key)
    }


def get_visible_errors(view):
    visible_error_ids = get_visible_error_ids(view)
    return [
        error
        for error in persist.errors[view.buffer_id()]
        if error['uid'] in visible_error_ids
    ]
