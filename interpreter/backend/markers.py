"""Call-stack markers for expanded arguments.

The compiler pushes one of these ahead of every ``*args`` / ``**kwargs`` /
``key=value`` payload so the VM can split a flat stack slot list back into
positionals and keyword arguments (:meth:`.vm.VM._expand_call_args`).
Plain calls carry no markers and skip that expansion entirely.
"""

from __future__ import annotations

from ..objects.strings import SdString


class KwargMarker(SdString):
    """Marks the start of a keyword-argument pair on the call stack.

    Subclasses SdString so the name rides in .value, but a distinct type
    means runtime string arguments can never be mistaken for markers.
    """

    __slots__ = ()

    def __repr__(self) -> str:
        return f"KwargMarker({self.value!r})"


class StarArgsMarker:
    """Follows an expression whose list value expands into positionals."""

    __slots__ = ()


class KwargsDictMarker:
    """Follows an expression whose dict value merges into kwargs."""

    __slots__ = ()
