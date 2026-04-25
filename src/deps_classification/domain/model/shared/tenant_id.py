from .guards import Guard, ImmutableCheck

__all__ = ["TenantId"]


class TenantId:
    value = Guard[str](str, ImmutableCheck())

    def __init__(self, value: str) -> None:
        self.value = value

    def __call__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"<TenantId: {self.value}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.value == other.value
