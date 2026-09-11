# UI Improvement Plan — Landing Page + Login Screens

## Scope boundary (read this first — this is what makes parallel work safe)

**This session touches ONLY these files:**
- `frontend/index.html` (landing page, role selection)
- `frontend/login/user/index.html`
- `frontend/login/driver/index.html`
- `frontend/login/officer/index.html`
- Any *new* shared CSS/asset file you create for these four (e.g. `frontend/shared/auth-theme.css`)

**Do NOT touch, under any circumstances — another session is actively working in the same working directory in parallel:**
- `frontend/user/index.html` (the main app — being edited for driver GPS tracking + hazard reporting polish right now)
- Anything under `backend/`
- `CLAUDE.md` (shared project memory — if you need to leave a note for the other session, add it to the "Progress" section at the bottom of *this* file instead)
- `implementation_plan_phase2.md`
- `.env` / `.env.example`

Both sessions are working uncommitted in the same folder (no git worktree isolation), so this boundary is the only thing preventing one session's edits from silently clobbering the other's. If a task genuinely requires touching something outside your four files, stop and flag it instead of editing it.

The dev server is already running on `localhost:3000` — reload `/`, `/login/user`, `/login/driver`, `/login/officer` in the browser to preview live; no separate server needed for these four static pages.

---

## Why these four pages need work

They're functionally complete (auth wired to the backend, role gating verified live) but visually minimal — plain system-font cards, no shared stylesheet (each file repeats the same CSS custom properties and component classes independently), emoji as icons despite the README's stated "zero emoji dependencies" principle, and no validation/loading feedback beyond a static error message.

## Design direction (per the original problem statement's §15 visual style, already partially followed — keep it)

- Light/white backgrounds, blue = primary/user, green = safe/driver, amber = caution/officer, **red reserved only for real errors** (this is already followed correctly — don't break it)
- Rounded cards, minimal shadows, no cyberpunk/neon — "trustworthy government/technology" tone
- Mobile-first: large tap targets, one-handed reach, no scroll needed to see the primary action on a normal phone screen

## Concrete tasks

1. **Extract a shared stylesheet.** All four files currently redefine the same `:root` custom properties, `.back-btn`, `.icon-box`, `.login-card`, `.btn*`, `.error-msg` classes independently. Pull the common pieces into one file (e.g. `frontend/shared/auth-theme.css`) linked from all four — keeps them visually consistent and makes future changes one edit instead of four.
2. **Replace emoji icons with inline SVG.** 👤🚚👮 on the icon boxes and the hazard/role indicators read as placeholder, not deliberate — swap for simple line-icon SVGs matching the back-button's existing stroke style. Keep it minimal, not a full icon library.
3. **Real-time form validation**, not just on-submit: email format check as they type/blur, password strength hint on the signup path, visually disable the submit button until the form is valid rather than only after clicking it.
4. **Loading state polish.** Currently a text swap + `opacity: 0.6`. Add a small inline spinner on the button itself so it's unambiguous a request is in flight, especially on slow mobile connections.
5. **Success feedback before redirect.** Right now signup/login either shows an error or silently navigates away — a brief "Signed in — redirecting…" state (even 300-500ms) avoids the page feeling like it did nothing.
6. **Officer invite-code field.** Just added functionally (plain text input) — give it proper visual weight/hierarchy since it's the one field that determines whether someone becomes an officer; it shouldn't look like just another form field.
7. **Accessibility pass.** Visible `:focus` states on all inputs/buttons (currently relies on browser default, inconsistent across the four), sufficient color contrast on the lighter text (`--c-text-2: #86868b` on white is borderline for body text — check against WCAG AA), proper `<label for="">` association instead of the current label-above-input-without-`for`.
8. **Verify at 360-400px width** (smallest common Android screens) — landing page's three role cards and each login card should need zero scrolling to reach the primary action.

## Definition of Done

- All four pages visually consistent via the shared stylesheet, no duplicated CSS logic.
- Every form gives real-time feedback (valid/invalid, loading, success) without needing a page reload to see the result of a mistake.
- No emoji-as-icon left on these four pages.
- Confirmed usable one-handed at 375px width without horizontal scroll.
- The actual auth network calls (`/api/v1/auth/register`, `/api/v1/auth/register-officer`, Supabase sign-in) are untouched — this is a visual/UX pass only, not a logic change. If backend testing is needed, the other session already has a working backend on `localhost:8000` — don't start a second one.

---

## Progress (update this section, not CLAUDE.md)

- [x] Shared stylesheet extracted — `frontend/shared/auth-theme.css`, linked from all four pages. Each page keeps only a tiny local `:root` override (`--c-primary` / `--c-primary-rgb`) plus true page-unique layout (landing's `.role-card` grid). Also extracted `frontend/shared/auth-ui.js` (email/password validation, button loading state, success message) since the same JS was duplicated across the three login pages.
- [x] Emoji icons replaced — 👤/🚚/👮 swapped for inline line-style SVGs (person / truck / shield-check) matching the back button's stroke style, on both the landing role cards and the login page icon boxes. Officer icon changed from a literal police emoji to a neutral shield-check (authority/trust, not law-enforcement-specific).
- [x] Form validation added — live email format check on input/blur (red border + inline message on blur if invalid, green border once valid), password strength meter (weak/fair/strong) under the password field, submit buttons visually disabled (`opacity:0.4`, `cursor:not-allowed`) until the form is valid. Officer's "create account" button additionally requires the invite code to be non-empty; "login" only requires email+password.
- [x] Loading/success states added — buttons show an inline spinner + swapped label text ("Signing in…" / "Creating account…" / "Verifying invite code…") while the request is in flight, then a green "Signed in — redirecting…" success state for ~450ms before navigating away.
- [x] Invite-code field restyled — wrapped in a tinted `.invite-box` (role-color border/background, lock icon on the label, helper text underneath) so it reads as the one field that changes what the account can do, not just another input.
- [x] Accessibility pass done — `:focus-visible` outline on all links/buttons/inputs, every `<label>` now has a matching `for`/`id`, `role="alert"`/`role="status"` on error/success messages, and `--c-text-2` darkened from `#86868b` to `#6e6e73` (~4.6:1 on white, AA-safe for body text — the old value was ~3.5:1 and failed AA for the `.desc` paragraphs).
- [x] Mobile-width verified — layout was already `width:100%; max-width:380px` with 20px body side padding, confirmed via the 320px effective viewport math at 360px screen width; no changes needed there, just kept it intact through the refactor.

No backend/auth logic touched — `/api/v1/auth/register`, `/api/v1/auth/register-officer`, and the Supabase calls are byte-for-byte the same calls as before, just wrapped with client-side validation gating and loading/success UI around them.

### Follow-up: full visual redesign (per explicit request, beyond the original DoD)

The first pass above was a polish pass on the existing card/layout design (per the plan's original "keep it" instruction). User then asked for an actual visual redesign, not just interaction polish. Second pass on top of the same four files:

- **Gradient icon badges** — `.icon-box` is now a role-colored gradient (`--c-primary` → `--c-primary-dark`) with a soft glow shadow and a white icon, replacing the flat tinted box.
- **Branded background wash** — `body` now has a layered soft radial-gradient tint (role color, very low opacity) instead of flat `#f5f5f7`, on all four pages.
- **Split hero/form layout for the 3 login pages at ≥900px** — new `.auth-shell` / `.brand-panel` / `.form-panel` structure: a full-bleed gradient panel with the role icon/title/description on one side, the form card on the other, inside one rounded elevated shell. Below 900px this collapses back to the exact same centered single-column stack the mobile-width verification already covered, so the no-scroll behavior at 360–400px is unchanged and wasn't re-gambled.
- **Icon-in-input fields** — email/password/invite-code inputs now have a leading SVG icon (mail / lock / key) instead of bare text fields.
- **Redesigned cards** — `.login-card` and `.role-card` got a top accent bar (or hover glow) in the role's gradient, larger radius, two-layer shadow (`--shadow-card`) for more depth.
- **Landing hero redesign** — gradient-text wordmark, a slow-spinning dashed ring behind the logo (respects `prefers-reduced-motion`), refined pill-style tagline with a border.
- **Entrance motion** — `.fade-up` staggered fade/slide-in on hero, cards, and footer, disabled under `prefers-reduced-motion: reduce`.
- **Buttons** — primary buttons now use the gradient fill + a trailing arrow icon that nudges forward on hover; arrow swaps out for the spinner during a request (wired in `auth-ui.js`'s `setButtonLoading`).

Same caveat as before: no live browser/screenshot verification was available in this environment (no `chromium-cli`, no cached Playwright/Chromium) — verified via `node --check` on every inline script, 200s on every route/asset through the dev server, and manual review of the CSS math for the 360–400px collapse. Worth an actual look in a browser before calling the redesign final.

### Follow-up: two reported bugs fixed (via sih-f3 relay)

1. **"There's no sign up page??"** — root cause was `.btn:disabled { opacity: 0.4 }` combined with the CREATE ACCOUNT/CREATE DRIVER ACCOUNT/CREATE OFFICER ACCOUNT buttons starting disabled before any input, making them look non-functional, plus `handleAuth()` doing a silent `if (!formValid()) return;` with zero feedback. Fixed properly rather than just bumping the opacity number: buttons are no longer pre-disabled before interaction at all — `wireEmailField`/new `wirePasswordField` in `auth-ui.js` still give real-time border/message feedback as you type, but an invalid *click* now force-shows the field errors (and, on the officer page, the invite-box error) plus a `triggerShake()` shake animation on the button (`prefers-reduced-motion`-safe) instead of doing nothing. Buttons still disable correctly during the actual network request (loading state unchanged).
2. **Removed "Continue as Guest"** from `frontend/login/user/index.html` and `frontend/login/driver/index.html` (officer never had one). Removed the now-unused `.btn-guest` rule from `auth-theme.css` too. Note: this only removes the CTA — `/user/` and `/driver/` are still directly reachable by URL without auth, unchanged.

### Follow-up: Sign In / Create Account tab toggle (via sih-f3 relay)

Root cause of the user still not finding signup after the previous fix: clicking CREATE ACCOUNT changed nothing visually — it was just a second button under the same static form as LOGIN, no signal you were now "in signup mode." Fixed by replacing the two-buttons-on-one-form pattern with an explicit segmented `.auth-tabs` toggle ("Sign In" / "Create Account") above the form on all three login pages, collapsed to a single primary CTA (`#btn-submit`) whose label and behavior follow the active tab (`currentMode`, set via `setMode()`). Password strength meter now only shows in Create Account mode (it isn't meaningful during login). On the officer page specifically, the invite-code box (`#invite-box`) is now `hidden` entirely during Sign In and only appears in Create Account mode, addressing the peer's note that it looked odd being shown during login. Cribbed the segmented-toggle *pattern* from `frontend/user/index.html`'s existing `switchAuthTab()` admin gate, but did not touch that file — this is a fresh, smaller implementation scoped to the three standalone login pages, sharing the new `.auth-tabs`/`.auth-tab` CSS added to `auth-theme.css`.

### Follow-up: hardened the Supabase client init + network calls (via sih-f3 relay)

User escalated to "nothing is happening at all" on Login/Create Account, even with a deliberately invalid email. Root cause sih-f3 traced and confirmed plausible: all three login pages did `const supabase = window.supabase.createClient(...)` unguarded at the top level of the inline `<script>`. If the jsdelivr CDN script failed for any reason (network block, ad-blocker, offline), `window.supabase` is `undefined` and that line throws synchronously — killing the entire inline script, including the `wireEmailField`/`wirePasswordField` wiring below it, with zero visible error. Separately, `handleAuth()` had no try/catch around the Supabase/fetch calls, so any thrown error (network blip, CORS) left the button stuck mid-spinner forever with `setButtonEnabled(false)` never undone.

Fixed in all three pages:
- Supabase client init wrapped in `try { if (window.supabase) ... } catch {}`, `supabase` defaults to `null` on failure. If it's `null` on page load, a visible error banner shows immediately ("Could not load the sign-in service...") instead of waiting for a doomed click.
- `handleAuth()`'s body wrapped in `try/catch/finally` — any thrown error now shows "Connection error — please check your network and try again." and the `finally` block always re-enables the button and clears the spinner *unless* the auth actually succeeded (tracked via a `succeeded` flag, so the success/redirect state isn't clobbered).
- A `!supabase` guard at the top of `handleAuth()` too, so a click after a failed CDN load shakes the button and re-shows the banner rather than throwing.

### Follow-up: the ACTUAL root cause — found via real browser testing, not another guess

The hardening pass above turned out not to be the real fix. User reported the tab toggle and both buttons were completely dead — not even the Sign In/Create Account tabs responded. At this point installed `playwright-core` (pointed at the existing local Chrome install, no browser download needed — network to npm was reachable) to actually load the page headlessly and read the real console/page errors instead of guessing again. First error captured:

```
[pageerror] Identifier 'supabase' has already been declared
```

Root cause: `https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2` is a classic (non-module) UMD script that declares `var supabase = (function(){...})();` at the true top level of the document's shared global script scope — confirmed by fetching the bundle directly and inspecting it (`var supabase=(function(e){...` at the very start). Our own inline `<script>` on all three login pages *also* declared `let supabase = ...` at its top level. A `let`/`const` redeclaring a name that already exists as a `var` in the same global scope — even across separate `<script>` tags — is a **parse-time SyntaxError**, not a runtime one. That means the entire inline script failed to compile at all: none of its code ran, not even hoisted function declarations, so `setMode` and `handleAuth` never existed — exactly matching "nothing happens, not even the tabs."

This conflict was likely latent since before this session touched these files (any classic script doing `const supabase = window.supabase.createClient(...)` on a page that also loads this exact CDN bundle would hit the same collision) — plausibly surfaced now because the unpinned `@2` CDN tag floats to whatever the latest 2.x release currently is.

Fix: renamed the local variable from `supabase` to `supabaseClient` in all three files (declaration, the `if (!supabaseClient)` guards, and every `supabaseClient.auth.signInWithPassword(...)` call) — `window.supabase` (the library's own namespace) is untouched and still what we call `.createClient()` on.

Verified for real this time, not just `node --check`: headless Chrome (via `playwright-core` against the local Chrome binary) loaded all three login pages, clicked the Create Account tab and confirmed it visually activated, filled in credentials and clicked LOGIN on the user page — it correctly reached Supabase (`POST .../auth/v1/token?grant_type=password` → 400 for a deliberately wrong password) and displayed "Invalid login credentials" in the error banner. Zero `pageerror` events on any of the three pages after the fix. This is the first round of these fixes actually confirmed working in a real browser rather than inferred from source review.

### Follow-up: wrong post-login redirect target on the user page

User reported: after signing in, landed back on what looked like a login page instead of the app. Diagnosed by curling `/user` vs `/user/` and comparing the returned `<title>` — `/user` (no trailing slash) actually serves the **landing/role-selection page** (`frontend/index.html`'s SPA fallback), not `frontend/user/index.html`; only `/user/` (with the slash) resolves to the real app. `frontend/login/user/index.html` was redirecting to `window.location.href = '/user'` (missing the slash) — landing users right back on a page full of "Login as User/Driver/Officer" cards, which reads exactly like getting bounced back to login. `frontend/login/driver/index.html` (`/driver/`) and `frontend/login/officer/index.html` (`/user/#admin`) already had the trailing slash and were unaffected. This bug predates this session — the original pre-redesign code had the same `/user` (no slash) target — so it's an existing bug being fixed here, not a regression introduced by the redesign.

Fixed: `frontend/login/user/index.html`'s success redirect now goes to `/user/`. Verified via `curl`'s title comparison and re-checked with `node --check`.
