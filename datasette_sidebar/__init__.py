import os

from datasette import hookimpl
from datasette.permissions import Action
from datasette.plugins import pm
from datasette_vite import vite_js_urls, vite_css_urls
from sqlite_utils import Database as SqliteUtilsDatabase

from . import hookspecs
from .router import router, SIDEBAR_ACCESS_ACTION
from .internal_migrations import internal_migrations

pm.add_hookspecs(hookspecs)

# Import route modules to trigger registration on the shared router
from .routes import api

_ = (api,)

VITE_DEV_PATH = os.environ.get("DATASETTE_SIDEBAR_VITE_PATH")
SIDEBAR_ENTRYPOINT = "src/sidebar/index.ts"


async def _has_access(datasette, request):
    actor = request.actor if request else None
    return await datasette.allowed(action=SIDEBAR_ACCESS_ACTION, actor=actor)


@hookimpl
def register_routes():
    return router.routes()


@hookimpl
def extra_js_urls(datasette, request):
    async def inner():
        if not await _has_access(datasette, request):
            return []
        return vite_js_urls(
            datasette=datasette,
            entrypoint=SIDEBAR_ENTRYPOINT,
            plugin_package="datasette_sidebar",
            vite_dev_path=VITE_DEV_PATH,
        )

    return inner


@hookimpl
def extra_css_urls(datasette, request):
    async def inner():
        if not await _has_access(datasette, request):
            return []
        return vite_css_urls(
            datasette=datasette,
            entrypoint=SIDEBAR_ENTRYPOINT,
            plugin_package="datasette_sidebar",
            vite_dev_path=VITE_DEV_PATH,
        )

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