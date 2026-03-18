<script lang="ts">
  import Section from "./Section.svelte";

  interface AppItem {
    label: string;
    href: string;
    icon: string;
    color: string;
    description: string;
  }

  let { apps }: { apps: AppItem[] } = $props();
</script>

{#if apps.length > 0}
  <Section title="Apps" id="apps">
    <ul class="apps-list">
      {#each apps as app (app.label)}
        <li class="apps-item">
          <a href={app.href} class="apps-item-link" title={app.description || app.label}>
            <span class="apps-item-icon" style="color: {app.color}">
              {@html app.icon}
            </span>
            <span class="apps-item-text">
              <span class="apps-item-label">{app.label}</span>
              {#if app.description}
                <span class="apps-item-desc">{app.description}</span>
              {/if}
            </span>
          </a>
        </li>
      {/each}
    </ul>
  </Section>
{/if}

<style>
  .apps-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .apps-item {
    display: flex;
    align-items: center;
    padding: 0 8px;
  }

  .apps-item-link {
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

  .apps-item-link:hover {
    background: #e8e8e8;
  }

  .apps-item-icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    width: 14px;
    height: 14px;
  }

  .apps-item-icon :global(svg) {
    width: 14px;
    height: 14px;
  }

  .apps-item-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .apps-item-label {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .apps-item-desc {
    font-size: 11px;
    font-weight: 400;
    color: #888;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
