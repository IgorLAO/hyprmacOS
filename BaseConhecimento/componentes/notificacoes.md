# Notification Banners and Notification Center

> Sources: macOS 27 UI Kit *Notifications* outline (`referencias/kit/contornos/Notifications.txt`), style `Liquid Glass/*/Notification`, Apple HIG [notifications](../hig/notifications.md), [managing-notifications](../hig/managing-notifications.md).

---

## Notification Banner Specifications (Kit Reference)
* **Dimensions:** **344 × 78 pt**, continuous **radius 20 pt**, styled with Liquid Glass Notification recipe.
* **Padding:** **12 pt (top) / 14 pt (right) / 12 pt (bottom) / 10 pt (left)**, 8 pt column gap:
  1. Leading 40 pt column: **32×32 pt app icon** (radius 6 pt).
  2. Center 232 pt content column: **Title: Bold 13 pt** + **Body: Regular 13 pt**, colored `#363636` (Light) / `#FFFFFFFA` 96% (Dark).
  3. Trailing 32 pt column: **Timestamp: Regular 11 pt** (`#8A8A8A`), optional **32×32 pt attachment thumbnail** below.
* **Stacked Banners:** Subsequent background notifications peek 6–8 pt below, inset 16 pt on each side (312 pt width).
* **Screen Placement:** 16 pt margin from right display edge, 15 pt below menu bar; 16 pt vertical spacing between notification groups.

---

## Behavioral Standards (Apple HIG)
* Keep body text concise and informative; omit the application name from the body (the icon already identifies the app).
* Support up to 4 inline action buttons with concise Title Case labels.
* Notification Center opens when clicking the clock in the top-right corner; items are grouped chronologically and by application.
