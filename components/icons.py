from __future__ import annotations

ICONS: dict[str, str] = {
    "database": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <ellipse cx="12" cy="5" rx="8" ry="3"></ellipse>
  <path d="M4 5v6c0 1.66 3.58 3 8 3s8-1.34 8-3V5"></path>
  <path d="M4 11v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6"></path>
</svg>
""",
    "upload": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M12 16V4"></path>
  <path d="m7 9 5-5 5 5"></path>
  <path d="M4 17v2a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-2"></path>
</svg>
""",
    "schema": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <rect x="3" y="4" width="7" height="16" rx="1.5"></rect>
  <rect x="14" y="4" width="7" height="7" rx="1.5"></rect>
  <rect x="14" y="13" width="7" height="7" rx="1.5"></rect>
</svg>
""",
    "quality": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M12 3l7 3v5c0 4.5-3 8.5-7 10-4-1.5-7-5.5-7-10V6l7-3z"></path>
  <path d="m9 12 2 2 4-4"></path>
</svg>
""",
    "distribution": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M4 20V10"></path>
  <path d="M9 20V4"></path>
  <path d="M14 20v-7"></path>
  <path d="M19 20V8"></path>
</svg>
""",
    "anomaly": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M12 3 2 20h20L12 3z"></path>
  <path d="M12 10v4"></path>
  <path d="M12 17h.01"></path>
</svg>
""",
    "report": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"></path>
  <path d="M14 3v5h5"></path>
  <path d="M9 13h6"></path>
  <path d="M9 17h6"></path>
</svg>
""",
    "warning": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <circle cx="12" cy="12" r="9"></circle>
  <path d="M12 8v5"></path>
  <path d="M12 16h.01"></path>
</svg>
""",
    "info": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <circle cx="12" cy="12" r="9"></circle>
  <path d="M12 11v5"></path>
  <path d="M12 8h.01"></path>
</svg>
""",
    "check": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <circle cx="12" cy="12" r="9"></circle>
  <path d="m8.5 12.5 2.5 2.5 4.5-5"></path>
</svg>
""",
    "arrow_up": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M12 19V5"></path>
  <path d="m5 12 7-7 7 7"></path>
</svg>
""",
    "arrow_down": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M12 5v14"></path>
  <path d="m19 12-7 7-7-7"></path>
</svg>
""",
    "minus": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M5 12h14"></path>
</svg>
""",
    "github": """
<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
  <path d="M12 2C6.48 2 2 6.58 2 12.25c0 4.53 2.87 8.37 6.84 9.73.5.1.68-.22.68-.49 0-.24-.01-.87-.01-1.71-2.78.62-3.37-1.37-3.37-1.37-.45-1.18-1.11-1.5-1.11-1.5-.91-.63.07-.62.07-.62 1 .07 1.53 1.06 1.53 1.06.89 1.56 2.34 1.11 2.91.85.09-.66.35-1.11.63-1.37-2.22-.26-4.56-1.14-4.56-5.07 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.71 0 0 .84-.28 2.75 1.05a9.36 9.36 0 0 1 5 0c1.91-1.33 2.75-1.05 2.75-1.05.55 1.41.2 2.45.1 2.71.64.72 1.03 1.63 1.03 2.75 0 3.94-2.34 4.81-4.57 5.06.36.32.68.94.68 1.9 0 1.37-.01 2.47-.01 2.81 0 .27.18.6.69.49A10.04 10.04 0 0 0 22 12.25C22 6.58 17.52 2 12 2z"></path>
</svg>
""",
}


def icon(name: str, size: int = 20, css_class: str = "") -> str:
    svg = " ".join(ICONS.get(name, ICONS["info"]).split())
    return (
        f'<span class="icon-wrapper {css_class}" '
        f'style="--icon-size:{size}px" aria-hidden="true">'
        f"{svg}</span>"
    )