import attrs


@attrs.frozen
class Season:
    # This is the database ID.
    id: int
    year: int
