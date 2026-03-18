<script lang="ts">
  import type { StarItem } from "./types.ts";
  import Icons from "./Icons.svelte";
  import Section from "./Section.svelte";

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
  <Section title="Starred" id="starred">
    <ul class="starred-list">
      {#each allStars as star (star.id)}
        <li class="starred-item">
          <a href={starUrl(star)} class="starred-item-link">
            <span class="starred-item-icon"><Icons kind={star.star_type} /></span>
            {starLabel(star)}
          </a>
          <button
            class="starred-item-unstar"
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
  </Section>
{/if}

<style>
  .starred-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .starred-item {
    display: flex;
    align-items: center;
    padding: 0 8px;
  }

  .starred-item-link {
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

  .starred-item-link:hover {
    background: #e8e8e8;
  }

  .starred-item-icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    color: #999;
  }

  .starred-item-unstar {
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

  .starred-item:hover .starred-item-unstar {
    opacity: 1;
  }

  .starred-item-unstar:hover {
    color: #e44;
    background: #fee;
  }
</style>
