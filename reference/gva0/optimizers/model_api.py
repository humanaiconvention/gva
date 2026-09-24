"""Reserved extension point. Model APIs are excluded from the v0.1 core."""


class ModelAPI:
    def choose(self, *args, **kwargs):
        raise NotImplementedError("Requires a new protocol; no model calls in core v0.1")
