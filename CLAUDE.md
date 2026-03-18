# datasette-sidebar

A Datasette plugin that adds a left sidebar to every page for starring databases, tables, and rows. Supports per-database filtering and plugin extensibility.

## Architecture

- **Backend:** Python, Datasette >=1.0a23, datasette-plugin-router, Pydantic
- **Frontend:** Svelte 5 (runes), TypeScript, Vite, openapi-fetch
- **Database:** sqlite-migrate for internal.db schema management
- **Build:** Just (Justfile), uv (Python), npm (frontend)
- **Injection:** Uses `extra_js_urls` / `extra_css_urls` hooks to inject sidebar on every Datasette page

## Commands

| Command | What it does |
|---------|-------------|
| `just dev` | Run Datasette dev server on port 8006 |
| `just dev-with-hmr` | Datasette + Vite HMR (restarts on .py/.html changes) |
| `just frontend-dev` | Start Vite dev server on port 5180 |
| `just frontend` | Build frontend for production |
| `just types` | Regenerate all TypeScript types from Python |
| `just types-watch` | Watch .py files, auto-regenerate types |
| `just format` | Format backend (ruff) + frontend (prettier) |
| `just check` | Type-check backend (ty) + frontend (svelte-check) |
| `uv run pytest` | Run Python tests |

## Project Structure

```
datasette_sidebar/
├── __init__.py              # Plugin hooks (extra_js_urls, register_routes, etc.)
├── router.py                # Shared Router + permission decorator
├── page_data.py             # Pydantic models (API contracts)
├── internal_db.py           # Star operations wrapper
├── internal_migrations.py   # sqlite-migrate schema
└── routes/
    └── api.py               # Star/unstar API endpoints

frontend/src/
├── sidebar/index.ts         # Entry point (mounts to every page)
├── sidebar/Sidebar.svelte   # Main sidebar component
└── page_data/load.ts        # loadPageData<T>() helper
```

## How the Sidebar Works

Unlike typical fullstack plugins with their own pages, the sidebar injects JS/CSS on **every** Datasette page via `extra_js_urls` / `extra_css_urls` hooks. The Svelte component creates its own container div and mounts to it.

- **Instance level (`/`)**: Shows all starred items across all databases
- **Database level (`/db`)**: Shows only starred items for that database
- **Toggle**: Cmd+B / Ctrl+B, state persisted in localStorage
- **Hidden state**: Shows hamburger menu button in upper left

## API Endpoints

- `GET /-/sidebar/api/stars` — List starred items (optional `?database_name=` filter)
- `POST /-/sidebar/api/toggle-star` — Toggle star on/off
- `DELETE /-/sidebar/api/stars/{id}` — Remove a specific star

## Database

**Tables (in internal.db):**
- `datasette_sidebar_stars` — Starred items per actor

**Migrations:** `internal_migrations.py` — applied on startup hook.

## Hooks Used

- `extra_js_urls()` — injects sidebar JS bundle on every page (permission-gated)
- `extra_css_urls()` — injects sidebar CSS on every page
- `register_routes()` — registers API routes
- `register_actions()` — defines `datasette-sidebar-access` permission
- `database_actions()` — adds "Star this database" to database action menu
- `table_actions()` — adds "Star this table" to table action menu
- `startup()` — applies internal.db migrations

## Permission

- `datasette-sidebar-access` — Controls access to sidebar and starring functionality

## Environment Variables

- `DATASETTE_SIDEBAR_VITE_PATH` — Vite dev server URL for HMR (e.g., `http://localhost:5180/`)
- `DATASETTE_SECRET` — Required for dev server

## Key Conventions

- **Svelte 5 runes**: Use `$state()`, `$derived()`, `$effect()`, `$props()` — NOT Svelte 4 syntax
- **Permissions**: All routes use `@check_permission()` decorator
- **IDs**: Use `python-ulid` for generating record IDs
- **Internal DB reads**: Use `execute_write_fn()` even for reads (transaction safety)
