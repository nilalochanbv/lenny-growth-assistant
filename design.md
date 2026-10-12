# Design System & UX Specification
## Project: The Lenny Growth Assistant
**Design Personality:** Editorial Clarity, Calm Focus, Intelligent Workspace

---

## 1. Design Philosophy
The Lenny Growth Assistant avoids the superficial aesthetic of generic AI chat wrappers (oversized cards, garish gradients, neon halos, decorative blobs). Instead, it adopts the focused, high-density clarity of modern engineering and product tools like **Linear** and **Claude Workspace**.

### Core Tenets:
1. **Editorial Seriousness**: Crisp typography, restrained palette, and high legibility suitable for strategic reading.
2. **Predictable Spatial Hierarchy**: Strict distinction between the Navigation Column, Conversation Stream, Evidence Citations, and the Side-by-Side Artifact Canvas.
3. **Evidence Visibility**: Citations are not hidden behind vague tooltips; they are explicit, numbered interactive chips that reveal context on demand.
4. **Sandboxed Canvas**: Generated deliverables live in an independent, resizable canvas rather than being trapped in the chat scroll.

---

## 2. Design Tokens

### Color Palette (Dark-First Theme)
| Token | Value | Purpose |
| :--- | :--- | :--- |
| `--bg-base` | `#090d16` | Main viewport foundation |
| `--bg-surface` | `#0f1728` | Sidebar and active panels |
| `--bg-elevated` | `#162035` | Cards, active items, inputs |
| `--bg-hover` | `#1d2a45` | Hover state background |
| `--border-subtle` | `rgba(255, 255, 255, 0.07)` | Dividers, subtle lines |
| `--border-default`| `rgba(255, 255, 255, 0.12)` | Component borders |
| `--border-active` | `#6366f1` | Focus outlines & active indicators |
| `--text-main` | `#f8fafc` | Primary headings and text |
| `--text-secondary`| `#94a3b8` | Subtext, timestamps, labels |
| `--text-muted` | `#64748b` | Placeholders, inactive icons |
| `--accent-primary`| `#6366f1` | Primary action button, active session |
| `--accent-amber` | `#f59e0b` | Deliverables and editorial highlights |
| `--status-success`| `#10b981` | Online indicators, active checks |

### Typography Scale
- **Display Heading**: 28px / Semi-bold (700) / Tracking: -0.5px
- **Section Heading**: 16px / Medium (600) / Tracking: -0.2px
- **Body Text**: 14.5px / Regular (400) / Line-height: 1.65
- **Metadata & Badges**: 11px–12px / Medium (500)
- **Monospace**: `JetBrains Mono`, `ui-monospace`, 13px / Line-height: 1.6

---

## 3. Layout & Information Architecture

```
+---------------------------------------------------------------------------------------+
|  TOP HEADER: [Toggle Sidebar] | Current Session Title           [Provider Pill: Local] |
+------------------+---------------------------------------+----------------------------+
|  SIDEBAR (280px) |  CONVERSATION STREAM                  |  ARTIFACT VIEWER (520px)   |
|                  |                                       |                            |
|  [Logo & Pro]    |  [Assistant Message]                  |  [Header: Title + Format]  |
|  [+ New Chat]    |  - Grounded answer paragraphs         |  [Tabs: Preview | Source]  |
|  [Search Filter] |  - Inline citations [1], [2]          |  [Actions: Copy, Download] |
|                  |                                       |                            |
|  Saved Sessions  |  Verified Sources Chips:              |  +----------------------+  |
|  - Active PMF    |  [#1 Molly Graham] [#2 Elena Verna]   |  | Sandboxed Preview    |  |
|  - Retention Q&A |                                       |  | (Markdown / Isolated |  |
|  - Leadership    |  +---------------------------------+  |  |  iframe HTML/CSS)    |  |
|                  |  | COMPOSER: [Ask a question...]    |  |  |                      |  |
|  [Status Badge]  |  | [Model Select]            [Send] |  |  +----------------------+  |
|  [Settings Cog]  |  +---------------------------------+  |                            |
+------------------+---------------------------------------+----------------------------+
```

### 1. Left Sidebar
- Collapsible on desktop (smooth 0.2s slide), hidden via overlay drawer on small screens.
- Search input with real-time substring filtering across conversation titles.
- Message counts and timestamps displayed for each saved session.
- Live database chunk count badge and settings trigger in footer.

### 2. Main Conversation Stream
- Centered container constrained to 820px max-width to maintain comfortable reading eye-span.
- Differentiated avatars: Minimal charcoal ring for User, subtle indigo gradient for Assistant.
- Inline citation chips rendered as discrete pill badges with guest names and index numbers.
- One-click copy action with temporary green check confirmation.

### 3. Split-Pane Artifact Viewer
- Slides in smoothly from the right whenever an artifact is generated or clicked in conversation.
- Tabs for "Preview" and "Source Code".
- Supports safe Markdown styling (with clean tables, headers, and code blocks) and isolated HTML/CSS tools.
- Export button downloads standalone `.html` or `.md` files directly to the user's disk.

---

## 4. Interaction States & Transitions
- **Hover**: Subtle brightness shifts on buttons and cards (`translateY(-1px)`).
- **Focus**: Distinct indigo focus ring (`box-shadow: 0 0 0 1px var(--accent-primary)`).
- **Loading**: Spinner icon inside the send button; composer text retained to prevent loss on failure.
- **Empty State**: Editorial introduction accompanied by 4 high-signal starter cards that execute real backend queries upon click.

---

## 5. Accessibility & Security
- **Accessible Contrast**: All text tokens exceed WCAG AA 4.5:1 contrast requirements against their respective backgrounds.
- **Keyboard Navigation**: Enter submits messages, Shift+Enter inserts line breaks, Esc closes modals.
- **Sandboxed HTML Preview**: Iframe configured with `sandbox="allow-scripts"` and isolated `srcDoc`, preventing child scripts from accessing parent cookies, tokens, or localStorage.
