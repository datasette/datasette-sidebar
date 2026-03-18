from typing import Annotated

from datasette import Response
from datasette.plugins import pm
from datasette_plugin_router import Body
from pydantic import BaseModel

from ..router import router, check_permission
from ..internal_db import InternalDB
from ..page_data import StarItem, StarListResponse, ToggleStarResponse


class ToggleStarBody(BaseModel):
    star_type: str
    database_name: str
    table_name: str | None = None
    row_pks: str | None = None


@router.GET("/-/sidebar/api/stars$", output=StarListResponse)
@check_permission()
async def api_get_stars(datasette, request):
    actor_id = request.actor["id"] if request.actor else None
    if not actor_id:
        return Response.json({"stars": []})

    database_name = request.args.get("database_name")
    db = InternalDB(datasette.get_internal_database())
    stars = await db.get_stars(actor_id, database_name=database_name)
    return Response.json({"stars": [s.model_dump() for s in stars]})


@router.POST("/-/sidebar/api/toggle-star$", output=ToggleStarResponse)
@check_permission()
async def api_toggle_star(
    datasette,
    request,
    body: Annotated[ToggleStarBody, Body()],
):
    actor_id = request.actor["id"] if request.actor else None
    if not actor_id:
        return Response.json({"error": "Authentication required"}, status=403)

    starred, star = await InternalDB(datasette.get_internal_database()).toggle_star(
        actor_id=actor_id,
        star_type=body.star_type,
        database_name=body.database_name,
        table_name=body.table_name,
        row_pks=body.row_pks,
    )
    return Response.json(
        {
            "starred": starred,
            "star": star.model_dump() if star else None,
        }
    )


@router.GET("/-/sidebar/api/toggle-star$")
@check_permission()
async def api_toggle_star_get(datasette, request):
    """GET handler for toggle-star, used by database_actions/table_actions links.
    Renders a small form that auto-submits via POST."""
    star_type = request.args.get("star_type", "")
    database_name = request.args.get("database_name", "")
    table_name = request.args.get("table_name", "")
    row_pks = request.args.get("row_pks", "")

    label = database_name
    if table_name:
        label = f"{database_name}/{table_name}"

    html = f"""<!DOCTYPE html>
<html>
<head><title>Star {label}</title></head>
<body>
<h2>Star {label}?</h2>
<form method="POST" action="/-/sidebar/api/toggle-star" id="star-form">
    <input type="hidden" name="star_type" value="{star_type}">
    <input type="hidden" name="database_name" value="{database_name}">
    <input type="hidden" name="table_name" value="{table_name}">
    <input type="hidden" name="row_pks" value="{row_pks}">
    <button type="submit">Toggle Star</button>
</form>
<script>document.getElementById('star-form').submit();</script>
</body>
</html>"""
    return Response.html(html)


@router.POST("/-/sidebar/api/stars/(?P<star_id>[^/]+)/remove$")
@check_permission()
async def api_remove_star(datasette, request, star_id: str):
    actor_id = request.actor["id"] if request.actor else None
    if not actor_id:
        return Response.json({"error": "Authentication required"}, status=403)

    removed = await InternalDB(datasette.get_internal_database()).remove_star(
        actor_id=actor_id,
        star_id=star_id,
    )
    return Response.json({"removed": removed})


@router.GET("/-/sidebar/api/apps$")
@check_permission()
async def api_get_apps(datasette, request):
    database_name = request.args.get("database_name") or None
    apps = []
    for result in pm.hook.datasette_sidebar_apps(datasette=datasette):
        if result:
            for app in result:
                apps.append(
                    {
                        "label": app.label,
                        "href": app.resolve_href(database_name),
                        "icon": app.icon,
                        "color": app.color,
                        "description": app.description,
                    }
                )
    return Response.json({"apps": apps})
