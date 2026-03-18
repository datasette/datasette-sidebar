import { mount } from "svelte";
import Sidebar from "./Sidebar.svelte";

// Create sidebar container and mount
const container = document.createElement("div");
container.id = "datasette-sidebar-root";
document.body.appendChild(container);

mount(Sidebar, { target: container });

// Intercept sidebar toggle-star links from database_actions/table_actions
document.addEventListener("click", (e) => {
  const link = (e.target as HTMLElement).closest<HTMLAnchorElement>(
    'a[href*="/-/sidebar/api/toggle-star"]',
  );
  if (!link) return;

  e.preventDefault();
  const url = new URL(link.href, window.location.origin);
  const starType = url.searchParams.get("star_type") || "";
  const databaseName = url.searchParams.get("database_name") || "";
  const tableName = url.searchParams.get("table_name") || undefined;
  const rowPks = url.searchParams.get("row_pks") || undefined;

  fetch("/-/sidebar/api/toggle-star", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      star_type: starType,
      database_name: databaseName,
      table_name: tableName,
      row_pks: rowPks,
    }),
  })
    .then((r) => r.json())
    .then((data) => {
      // Dispatch event so sidebar can refresh
      window.dispatchEvent(
        new CustomEvent("sidebar-stars-changed", { detail: data }),
      );
    });
});
