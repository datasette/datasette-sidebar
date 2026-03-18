<script lang="ts">
  import type { DatabaseInfo, StarItem } from "./types.ts";
  import Icons from "./Icons.svelte";
  import Section from "./Section.svelte";

  const STORAGE_KEY = "datasette-sidebar-tree-expanded";

  let {
    databases,
    loading,
    onstar,
    stars = [],
  }: {
    databases: DatabaseInfo[];
    loading: boolean;
    onstar: (starType: string, databaseName: string, tableName?: string) => void;
    stars?: StarItem[];
  } = $props();

  function isStarred(starType: string, dbName: string, tableName?: string): boolean {
    return stars.some(
      (s) =>
        s.star_type === starType &&
        s.database_name === dbName &&
        (starType === "database" || s.table_name === tableName),
    );
  }

  function loadExpanded(): Set<string> {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? new Set(JSON.parse(stored) as string[]) : new Set();
    } catch {
      return new Set();
    }
  }

  function saveExpanded() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...expanded]));
    } catch {
      // localStorage full or unavailable
    }
  }

  let expanded = $state<Set<string>>(loadExpanded());

  function toggleExpanded(key: string) {
    if (expanded.has(key)) {
      expanded.delete(key);
    } else {
      expanded.add(key);
    }
    expanded = new Set(expanded);
    saveExpanded();
  }
</script>

<Section title="Databases and Tables" id="data-tree">
  {#if loading}
    <p class="sidebar-loading">Loading...</p>
  {:else}
    <ul class="tree-list">
      {#each databases as db (db.name)}
        {@const dbKey = `db:${db.name}`}
        {@const isExpanded = expanded.has(dbKey)}
        <li class="tree-node">
          <div class="tree-row">
            <button
              class="tree-toggle"
              onclick={() => toggleExpanded(dbKey)}
              aria-label="{isExpanded ? 'Collapse' : 'Expand'} {db.name}"
            >
              <svg
                class="tree-chevron"
                class:tree-chevron-open={isExpanded}
                width="10"
                height="10"
                viewBox="0 0 10 10"
                fill="none"
              >
                <path
                  d="M3 1L7 5L3 9"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </button>
            <a href={db.path} class="tree-label tree-label-db">
              <span class="tree-icon"><Icons kind="database" /></span>
              {db.name}
            </a>
            <button
              class="tree-star"
              class:tree-star-active={isStarred('database', db.name)}
              onclick={() => onstar('database', db.name)}
              title="{isStarred('database', db.name) ? 'Unstar' : 'Star'} {db.name}"
            >
              {#if isStarred('database', db.name)}
                <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor"><path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/></svg>
              {:else}
                <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor"><path d="M2.866 14.85c-.078.444.36.791.746.593l4.39-2.256 4.389 2.256c.386.198.824-.149.746-.592l-.83-4.73 3.522-3.356c.33-.314.16-.888-.282-.95l-4.898-.696L8.465.792a.513.513 0 0 0-.927 0L5.354 5.12l-4.898.696c-.441.062-.612.636-.283.95l3.523 3.356-.83 4.73zm4.905-2.767-3.686 1.894.694-3.957a.56.56 0 0 0-.163-.505L1.71 6.745l4.052-.576a.53.53 0 0 0 .393-.288L8 2.223l1.847 3.658a.53.53 0 0 0 .393.288l4.052.575-2.906 2.77a.56.56 0 0 0-.163.506l.694 3.957-3.686-1.894a.5.5 0 0 0-.461 0z"/></svg>
              {/if}
            </button>
          </div>
          {#if isExpanded}
            <ul class="tree-children">
              {#each db.tables as table (table.name)}
                <li class="tree-node">
                  <div class="tree-row tree-row-table">
                    <a
                      href="/{db.name}/{table.name}"
                      class="tree-label tree-label-table"
                    >
                      <span class="tree-icon"><Icons kind="table" /></span>
                      {table.name}
                    </a>
                    <button
                      class="tree-star"
                      class:tree-star-active={isStarred('table', db.name, table.name)}
                      onclick={() => onstar('table', db.name, table.name)}
                      title="{isStarred('table', db.name, table.name) ? 'Unstar' : 'Star'} {table.name}"
                    >
                      {#if isStarred('table', db.name, table.name)}
                        <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor"><path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/></svg>
                      {:else}
                        <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor"><path d="M2.866 14.85c-.078.444.36.791.746.593l4.39-2.256 4.389 2.256c.386.198.824-.149.746-.592l-.83-4.73 3.522-3.356c.33-.314.16-.888-.282-.95l-4.898-.696L8.465.792a.513.513 0 0 0-.927 0L5.354 5.12l-4.898.696c-.441.062-.612.636-.283.95l3.523 3.356-.83 4.73zm4.905-2.767-3.686 1.894.694-3.957a.56.56 0 0 0-.163-.505L1.71 6.745l4.052-.576a.53.53 0 0 0 .393-.288L8 2.223l1.847 3.658a.53.53 0 0 0 .393.288l4.052.575-2.906 2.77a.56.56 0 0 0-.163.506l.694 3.957-3.686-1.894a.5.5 0 0 0-.461 0z"/></svg>
                      {/if}
                    </button>
                    <span class="tree-count">{table.count} {table.count === 1 ? 'row' : 'rows'}</span>
                  </div>
                </li>
              {/each}
            </ul>
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</Section>

<style>
  .sidebar-loading {
    padding: 16px;
    color: #888;
    font-size: 13px;
    line-height: 1.5;
  }

  .tree-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .tree-node {
    list-style: none;
  }

  .tree-row {
    display: flex;
    align-items: center;
    padding: 1px 8px 1px 4px;
    gap: 2px;
    min-height: 24px;
  }

  .tree-row-table {
    padding-left: 22px;
  }

  .tree-icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    color: #888;
  }

  .tree-toggle {
    background: none;
    border: none;
    cursor: pointer;
    padding: 2px;
    margin-left: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    border-radius: 3px;
    flex-shrink: 0;
    width: 18px;
    height: 18px;
  }

  .tree-toggle:hover {
    background: #e8e8e8;
    color: #555;
  }

  .tree-chevron {
    transition: transform 0.15s ease;
  }

  .tree-chevron-open {
    transform: rotate(90deg);
  }

  .tree-label {
    font-size: 13px;
    font-weight: 500;
    color: #333;
    text-decoration: none;
    padding: 4px 6px;
    border-radius: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  a.tree-label:hover {
    background: #e8e8e8;
  }

  .tree-label-db {
    font-weight: 500;
  }

  .tree-star {
    background: none;
    border: none;
    cursor: pointer;
    padding: 2px;
    display: flex;
    align-items: center;
    color: #ccc;
    border-radius: 3px;
    flex-shrink: 0;
    opacity: 0;
    transition: opacity 0.15s, color 0.15s;
  }

  .tree-row:hover .tree-star {
    opacity: 1;
  }

  .tree-star:hover {
    color: #e8a900;
  }

  .tree-star-active {
    opacity: 1;
    color: #e8a900;
  }

  .tree-count {
    color: #aaa;
    font-size: 11px;
    margin-left: auto;
    flex-shrink: 0;
  }

  .tree-children {
    list-style: none;
    margin: 0;
    padding: 0 0 0 16px;
  }
</style>
