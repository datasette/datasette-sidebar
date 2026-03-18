<script lang="ts">
  import type { StarItem } from "./types.ts";
  import Icons from "./Icons.svelte";

  let {
    stars,
    isInstanceLevel,
    onunstar,
  }: {
    stars: StarItem[];
    isInstanceLevel: boolean;
    onunstar: (id: string) => void;
  } = $props();

  const starredDatabases = $derived(
    stars.filter((s) => s.star_type === "database"),
  );
  const starredTables = $derived(
    stars.filter((s) => s.star_type === "table"),
  );
  const starredRows = $derived(
    stars.filter((s) => s.star_type === "row"),
  );

  const allStars = $derived([...starredDatabases, ...starredTables, ...starredRows]);

  function starUrl(star: StarItem): string {
    if (star.star_type === "database") return `/${star.database_name}`;
    if (star.star_type === "table") return `/${star.database_name}/${star.table_name}`;
    if (star.star_type === "row" && star.row_pks)
      return `/${star.database_name}/${star.table_name}/${star.row_pks}`;
    return "/";
  }

  function starLabel(star: StarItem): string {
    if (star.star_type === "database") return star.database_name;
    if (star.star_type === "table")
      return `${star.database_name}/${star.table_name}`;
    if (star.star_type === "row") {
      return `${star.database_name}/${star.table_name}/${star.row_pks}`;
    }
    return "";
  }
</script>

{#if allStars.length > 0}
  <section class="sidebar-section">
    <h3 class="sidebar-section-title">Starred</h3>
    <ul class="sidebar-list">
      {#each allStars as star (star.id)}
        <li class="sidebar-item">
          <a href={starUrl(star)} class="sidebar-item-link">
            <span class="sidebar-item-icon"><Icons kind={star.star_type} /></span>
            {starLabel(star)}
          </a>
          <button
            class="sidebar-item-unstar"
            onclick={() => onunstar(star.id)}
            title="Unstar"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M3.5 3.5L10.5 10.5M10.5 3.5L3.5 10.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
            </svg>
          </button>
        </li>
      {/each}
    </ul>
  </section>
{/if}

<style>
  .sidebar-section {
    margin-bottom: 4px;
  }

  .sidebar-section-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #999;
    padding: 8px 16px 4px;
    margin: 0;
  }

  .sidebar-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .sidebar-item {
    display: flex;
    align-items: center;
    padding: 0 8px;
  }

  .sidebar-item-link {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    font-weight: 500;
    color: #333;
    text-decoration: none;
    border-radius: 4px;
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .sidebar-item-link:hover {
    background: #e8e8e8;
  }

  .sidebar-item-icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    color: #999;
  }

  .sidebar-item-unstar {
    background: none;
    border: none;
    cursor: pointer;
    color: #ccc;
    padding: 4px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    flex-shrink: 0;
    opacity: 0;
    transition: opacity 0.15s;
  }

  .sidebar-item:hover .sidebar-item-unstar {
    opacity: 1;
  }

  .sidebar-item-unstar:hover {
    color: #e44;
    background: #fee;
  }
</style>
