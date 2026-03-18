<script lang="ts">
  import type { Snippet } from "svelte";

  const STORAGE_PREFIX = "datasette-sidebar-section-";

  let {
    title,
    id,
    children,
  }: {
    title: string;
    id: string;
    children: Snippet;
  } = $props();

  function loadCollapsed(): boolean {
    try {
      return localStorage.getItem(STORAGE_PREFIX + id) === "collapsed";
    } catch {
      return false;
    }
  }

  let collapsed = $state(loadCollapsed());

  function toggle() {
    collapsed = !collapsed;
    try {
      if (collapsed) {
        localStorage.setItem(STORAGE_PREFIX + id, "collapsed");
      } else {
        localStorage.removeItem(STORAGE_PREFIX + id);
      }
    } catch {
      // ignore
    }
  }
</script>

<section class="section">
  <button class="section-header" onclick={toggle}>
    <h3 class="section-title">{title}</h3>
    <svg
      class="section-chevron"
      class:section-chevron-collapsed={collapsed}
      width="10"
      height="10"
      viewBox="0 0 10 10"
      fill="none"
    >
      <path
        d="M1 3L5 7L9 3"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  </button>
  {#if !collapsed}
    <div class="section-body">
      {@render children()}
    </div>
  {/if}
</section>

<style>
  .section {
    margin-bottom: 2px;
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 8px 12px 4px 16px;
    background: none;
    border: none;
    cursor: pointer;
    margin: 0;
  }

  .section-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #999;
    margin: 0;
  }

  .section-chevron {
    color: rgba(0, 0, 0, 0.12);
    transition: color 0.15s, transform 0.15s;
    flex-shrink: 0;
  }

  .section-header:hover .section-chevron {
    color: rgba(0, 0, 0, 0.5);
  }

  .section-chevron-collapsed {
    transform: rotate(-90deg);
  }

  .section-body {
    padding: 0;
  }
</style>
