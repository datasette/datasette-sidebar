<script lang="ts">
  import StarredSection from "./StarredSection.svelte";
  import DataTree from "./DataTree.svelte";
  import type { StarItem, DatabaseInfo, TableInfo } from "./types.ts";

  let visible = $state(
    localStorage.getItem("datasette-sidebar-visible") !== "false",
  );
  let stars = $state<StarItem[]>([]);
  let loading = $state(true);
  let databases = $state<DatabaseInfo[]>([]);
  let loadingData = $state(true);

  // Determine current context from URL
  const pathParts = window.location.pathname.split("/").filter(Boolean);
  const currentDatabase = $derived(
    pathParts.length > 0 && !pathParts[0]!.startsWith("-")
      ? pathParts[0]!
      : null,
  );
  const isInstanceLevel = $derived(currentDatabase === null);

  const filteredStars = $derived(
    isInstanceLevel
      ? stars
      : stars.filter((s) => s.database_name === currentDatabase),
  );

  let hasToggled = false;

  function enableTransitions() {
    if (!hasToggled) {
      hasToggled = true;
      document.body.style.transition = "margin-left 0.2s ease";
    }
  }

  function toggle() {
    enableTransitions();
    visible = !visible;
    localStorage.setItem("datasette-sidebar-visible", String(visible));
  }

  async function loadStars() {
    loading = true;
    try {
      const params = currentDatabase
        ? `?database_name=${currentDatabase}`
        : "";
      const resp = await fetch(`/-/sidebar/api/stars${params}`);
      if (resp.ok) {
        const data = await resp.json();
        stars = data.stars;
      }
    } finally {
      loading = false;
    }
  }

  async function loadDatabases() {
    loadingData = true;
    try {
      const resp = await fetch("/.json");
      if (!resp.ok) return;
      const data = await resp.json();
      const dbs: DatabaseInfo[] = [];
      for (const [, db] of Object.entries(data.databases) as [
        string,
        any,
      ][]) {
        if (db.name === "_internal") continue;
        const tables: TableInfo[] = (db.tables_and_views_truncated || [])
          .filter((t: any) => !t.hidden)
          .map((t: any) => ({
            name: t.name,
            columns: t.columns || [],
            count: t.count ?? 0,
            hidden: t.hidden,
          }));
        dbs.push({ name: db.name, path: db.path, tables });
      }
      databases = dbs;
    } finally {
      loadingData = false;
    }
  }

  async function unstar(starId: string) {
    const resp = await fetch(`/-/sidebar/api/stars/${starId}/remove`, {
      method: "POST",
    });
    if (resp.ok) {
      stars = stars.filter((s) => s.id !== starId);
    }
  }

  async function toggleStar(starType: string, databaseName: string, tableName?: string) {
    const resp = await fetch("/-/sidebar/api/toggle-star", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        star_type: starType,
        database_name: databaseName,
        table_name: tableName,
      }),
    });
    if (resp.ok) {
      await loadStars();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if ((e.metaKey || e.ctrlKey) && e.key === "b") {
      e.preventDefault();
      toggle();
    }
  }

  function handleStarsChanged() {
    loadStars();
  }

  $effect(() => {
    loadStars();
    loadDatabases();
    window.addEventListener("keydown", handleKeydown);
    window.addEventListener("sidebar-stars-changed", handleStarsChanged);
    return () => {
      window.removeEventListener("keydown", handleKeydown);
      window.removeEventListener("sidebar-stars-changed", handleStarsChanged);
    };
  });
</script>

{#if !visible}
  <button
    class="sidebar-toggle-hint"
    onclick={toggle}
    title="Open sidebar (Cmd+B)"
  >
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
      <path
        d="M7 1L3 5L7 9"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  </button>
{/if}

<nav
  class="sidebar-panel"
  class:sidebar-panel-hidden={!visible}
  aria-label="Sidebar"
>
  <div class="sidebar-header">
    <button class="sidebar-close" onclick={toggle} title="Close sidebar (Cmd+B)">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path
          d="M4 4L12 12M12 4L4 12"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
        />
      </svg>
    </button>
  </div>

  <div class="sidebar-content">
    {#if !loading}
      <StarredSection
        stars={filteredStars}
        {isInstanceLevel}
        onunstar={unstar}
      />
    {/if}

    <DataTree {databases} loading={loadingData} onstar={toggleStar} stars={stars} />
  </div>
</nav>

<style>
  :global(#datasette-sidebar-root) {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 10000;
    height: 100vh;
    pointer-events: none;
  }

  :global(#datasette-sidebar-root *) {
    pointer-events: auto;
  }

  .sidebar-toggle-hint {
    position: fixed;
    top: 50%;
    left: 6px;
    z-index: 10001;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    background: transparent;
    border: 1px solid rgba(0, 0, 0, 0.15);
    border-radius: 50%;
    cursor: pointer;
    color: rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    transition:
      width 0.2s ease,
      height 0.2s ease,
      background 0.2s ease,
      color 0.2s ease,
      left 0.2s ease;
  }

  .sidebar-toggle-hint:hover {
    width: 32px;
    height: 32px;
    left: 6px;
    background: rgba(255, 255, 255, 0.9);
    border-color: rgba(0, 0, 0, 0.3);
    color: rgba(0, 0, 0, 0.7);
  }

  .sidebar-panel {
    position: fixed;
    top: 0;
    left: 0;
    width: 260px;
    height: 100vh;
    background: #fafafa;
    border-right: 1px solid #ddd;
    display: flex;
    flex-direction: column;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
      sans-serif;
    font-size: 14px;
    transform: translateX(0);
    transition: transform 0.2s ease;
  }

  .sidebar-panel-hidden {
    transform: translateX(-100%);
    pointer-events: none;
  }

  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    height: 2.6rem;
    padding: 0 8px;
    border-bottom: 1px solid #e0e0e0;
    background: #fff;
    flex-shrink: 0;
  }

  .sidebar-close {
    background: none;
    border: none;
    cursor: pointer;
    color: #888;
    padding: 4px;
    border-radius: 4px;
    display: flex;
    align-items: center;
  }

  .sidebar-close:hover {
    background: #eee;
    color: #333;
  }

  .sidebar-content {
    flex: 1;
    overflow-y: auto;
    padding: 8px 0;
  }

  /* Push page content right when sidebar is visible */
  :global(body:has(.sidebar-panel:not(.sidebar-panel-hidden))) {
    margin-left: 260px;
  }
</style>
