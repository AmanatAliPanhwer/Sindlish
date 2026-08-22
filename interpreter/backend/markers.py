from ..objects.strings import SdString


class KwargMarker(SdString):
    """Marks the start of a keyword-argument pair on the call stack.

    Subclasses SdString so the name rides in .value, but a distinct type
    means runtime string arguments can never be mistaken for markers.
    """
    __slots__ = ()

    def __repr__(self):
        return f"KwargMarker({self.value!r})"


class StarArgsMarker:
    """Follows an expression whose list value expands into positionals."""
    __slots__ = ()


class KwargsDictMarker:
    """Follows an expression whose dict value merges into kwargs."""
    __slots__ = ()
