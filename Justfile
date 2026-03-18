# === Type Generation ===

# Generate TypeScript types from router's OpenAPI spec
types-routes:
  uv run python -c 'from datasette_sidebar.router import router; import json; print(json.dumps(router.openapi_document_json()))' \
    | npx --prefix frontend openapi-typescript > frontend/api.d.ts

# Generate TypeScript types from Pydantic page data models
types-pagedata:
  uv run scripts/typegen-pagedata.py
  for f in frontend/src/page_data/*_schema.json; do \
    npx --prefix frontend json2ts "$f" > "${f%_schema.json}.types.ts"; \
  done

# Generate all types
types:
  just types-routes
  just types-pagedata

# Watch Python files and regenerate types on change
types-watch:
  watchexec -e py --clear -- just types

# === Frontend ===

# Build frontend for production
frontend *flags:
    npm run build --prefix frontend {{flags}}

HMR_PORT := "5182"
# Start Vite dev server (HMR)
frontend-dev *flags:
    npm run dev --prefix frontend -- --port {{HMR_PORT}} {{flags}}

# === Formatting ===

format-backend *flags:
    uv run ruff format {{flags}}

format-backend-check *flags:
    uv run ruff format --check {{flags}}

format-frontend *flags:
    npm run format --prefix frontend {{flags}}

format-frontend-check *flags:
    npm run format:check --prefix frontend {{flags}}

format:
    just format-backend
    just format-frontend

format-check:
    just format-backend-check
    just format-frontend-check

# === Type Checking ===

check-backend:
    uvx ty check

check-frontend:
    npm run check --prefix frontend

check:
    just check-backend
    just check-frontend

# === Development ===

# Run Datasette dev server
dev *flags:
    DATASETTE_SECRET=abc123 uv run \
    --with datasette-debug-gotham \
    datasette \
    -s permissions.datasette-sidebar-access.id "*" \
    {{flags}}

# Run Datasette with Vite HMR (auto-restarts on Python/HTML changes)
dev-with-hmr *flags:
    DATASETTE_SIDEBAR_VITE_PATH=http://localhost:{{HMR_PORT}}/ \
    watchexec \
      --stop-signal SIGKILL \
      -e py,html \
      --ignore '*.db' \
      --restart \
      --clear -- \
      just dev {{flags}}
