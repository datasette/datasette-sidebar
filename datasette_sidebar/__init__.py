import json
import os
from pathlib import Path, PurePosixPath

from datasette import hookimpl
from datasette.permissions import Action
from sqlite_utils import Database as SqliteUtilsDatabase

from .router import router, SIDEBAR_ACCESS_ACTION
from .internal_migrations import internal_migrations

# Import route modules to trigger registration on the shared router
from .routes import api

_ = (api,)

VITE_DEV_PATH = os.environ.get("DATASETTE_SIDEBAR_VITE_PATH")
SIDEBAR_ENTRYPOINT = "src/sidebar/index.ts"

# Load Vite manifest once at import time (production only)
_manifest = {}
_manifest_path = Path(__file__).parent / "manifest.json"
if _manifest_path.exists():
    _manifest = json.loads(_manifest_path.read_text())


def _collect_css_from_manifest(entrypoint):
    """Recursively collect all CSS files from a manifest entry and its imports."""
    css_files = []
    seen = set()

    def collect(key):
        if key in seen:
            return
        seen.add(key)
        chunk = _manifest.get(key, {})
        for css in chunk.get("css", []):
            css_files.append(css)
        for imp in chunk.get("imports", []):
            collect(imp)

    collect(entrypoint)
    return css_files


async def _has_access(datasette, request):
    actor = request.actor if request else None
    print(actor)
    print(await datasette.allowed(action=SIDEBAR_ACCESS_ACTION, actor=actor))
    return await datasette.allowed(action=SIDEBAR_ACCESS_ACTION, actor=actor)


@hookimpl
def register_routes():
    return router.routes()


@hookimpl
def extra_js_urls(datasette, request):
    async def inner():
        if await _has_access(datasette, request):
            return []
        if VITE_DEV_PATH:
            return [
                {"url": f"{VITE_DEV_PATH}@vite/client", "module": True},
                {"url": f"{VITE_DEV_PATH}{SIDEBAR_ENTRYPOINT}", "module": True},
            ]
        chunk = _manifest.get(SIDEBAR_ENTRYPOINT, {})
        file = chunk.get("file", "")
        if file:
            return [
                {
                    "url": datasette.urls.static_plugins(
                        "datasette_sidebar",
                        str(PurePosixPath(file).relative_to("static")),
                    ),
                    "module": True,
                }
            ]
        return []

    return inner


@hookimpl
def extra_css_urls(datasette, request):
    async def inner():
        if not await _has_access(datasette, request):
            return []
        if VITE_DEV_PATH:
            return []
        return [
            datasette.urls.static_plugins(
                "datasette_sidebar",
                str(PurePosixPath(css).relative_to("static")),
            )
            for css in _collect_css_from_manifest(SIDEBAR_ENTRYPOINT)
        ]

    return inner


@hookimpl
def register_actions(datasette):
    return [
        Action(
            name=SIDEBAR_ACCESS_ACTION,
            description="Can access the sidebar",
        ),
    ]


@hookimpl
async def startup(datasette):
    def migrate(connection):
        db = SqliteUtilsDatabase(connection)
        internal_migrations.apply(db)

    await datasette.get_internal_database().execute_write_fn(migrate)


@hookimpl
def database_actions(datasette, actor, database):
    async def inner():
        if actor and await datasette.allowed(
            action=SIDEBAR_ACCESS_ACTION, actor=actor
        ):
            return [
                {
                    "href": datasette.urls.path(
                        f"/-/sidebar/api/toggle-star?star_type=database&database_name={database}"
                    ),
                    "label": "Star this database",
                    "description": "Add this database to your sidebar favorites",
                }
            ]
        return []

    return inner


@hookimpl
def table_actions(datasette, actor, database, table):
    async def inner():
        if actor and await datasette.allowed(
            action=SIDEBAR_ACCESS_ACTION, actor=actor
        ):
            return [
                {
                    "href": datasette.urls.path(
                        f"/-/sidebar/api/toggle-star?star_type=table&database_name={database}&table_name={table}"
                    ),
                    "label": "Star this table",
                    "description": "Add this table to your sidebar favorites",
                }
            ]
        return []

    return inner
