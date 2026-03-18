from dataclasses import dataclass, field
from typing import Callable, Union

from pluggy import HookspecMarker

hookspec = HookspecMarker("datasette")


@dataclass
class SidebarApp:
    """An app entry registered in the sidebar."""

    label: str
    href: Union[str, Callable[[str | None], str]]
    icon: str = ""
    color: str = "#666"
    description: str = ""

    def resolve_href(self, database_name: str | None = None) -> str:
        if callable(self.href):
            return self.href(database_name)
        return self.href


@hookspec
def datasette_sidebar_apps(datasette):
    """
    Register apps in the sidebar.

    Returns a list of SidebarApp instances.
    """
