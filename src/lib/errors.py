class ReplayError(Exception):
    ...


class NotSupportedExtentionError(ReplayError):
    MESSAGE = "Files with this extension is not supported"

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class CorruptedReplayError(ReplayError):
    MESSAGE = "Error occured while trying to load replay. \nPossibly, replay is corrupted"

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class EmptyReplayError(ReplayError):
    MESSAGE = "Replay is empty"

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class EmptyPathError(ReplayError):
    MESSAGE = "Path is empty"

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)
