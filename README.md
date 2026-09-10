# Learn Angular by Building Compass

**A project-driven, ~370-page book that takes a total beginner from "what is a framework?" to a deployed, tested, offline-ready, accessible Angular application — available in English and Hebrew.**

> This is the source for the book. All 20 chapters and 7 appendices live in `content/` (English) and `content-he/` (Hebrew) as plain Markdown. A small Python script (`build.py`) assembles them into A5 PDFs using WeasyPrint, with a full PDF outline for navigation. Edit any chapter, rerun the script, get a fresh PDF.

**Read the current build now:**

- **[English PDF](build/learn_angular.pdf)** — 369 pages, ~50,000 words, clickable outline for every chapter, section, and subsection.
- **[Hebrew PDF (עברית)](build/learn_angular_he.pdf)** — 378 pages, ~45,000 words, RTL layout, same coverage.

---

## Table of contents

- [At a glance](#at-a-glance)
- [About the book](#about-the-book)
- [Who this book is for](#who-this-book-is-for)
- [The Compass project](#the-compass-project)
- [Chapter-by-chapter guide](#chapter-by-chapter-guide)
  - [Part I — Foundations](#part-i--foundations)
  - [Part II — Components and templates](#part-ii--components-and-templates)
  - [Part III — Services and the outside world](#part-iii--services-and-the-outside-world)
  - [Part IV — Building a real app](#part-iv--building-a-real-app)
  - [Part V — Production](#part-v--production)
  - [Appendices A–G](#appendices)
- [Hebrew edition](#hebrew-edition)
- [Reading the PDFs](#reading-the-pdfs)
- [Building from source](#building-from-source)
- [Iterating on the book](#iterating-on-the-book)
- [Project structure](#project-structure)
- [Design notes](#design-notes)
- [Review history](#review-history)
- [What the book deliberately doesn't build](#what-the-book-deliberately-doesnt-build)
- [Contributing and feedback](#contributing-and-feedback)
- [License](#license)

---

## At a glance

| | |
|---|---|
| **Target framework** | Angular 18+ (signals, standalone components, new control flow, `inject()`, zoneless-ready) |
| **Target reader** | Total beginner to frontend development |
| **Format** | A5 PDF (also raw Markdown source) |
| **Editions** | English, Hebrew (RTL) |
| **Length** | 369 pages English · 378 pages Hebrew |
| **Structure** | 20 chapters + 7 appendices, 5 parts |
| **Spine project** | *Compass* — a personal task tracker that grows across chapters |
| **Pedagogy** | Project-driven; every concept introduced in service of one more feature |
| **Build** | `python3 build.py` (English) or `python3 build.py --lang he` (Hebrew) |
| **Source** | Plain Markdown in `content/` and `content-he/` |
| **PDF navigation** | Full outline / bookmarks (~388 clickable entries per language) |

---

## About the book

Most framework books either fly over concepts before you can touch them, or drown you in setup for fifty pages before rendering a single pixel. This book takes a third path: each concept lands exactly when you need it to add a feature to a real app, and each chapter's exercises reinforce that feature in code. The reader ends with a deployed application, not a folder of tutorials.

The book targets **modern Angular (v18+)** — signals as the default reactive primitive, standalone components without NgModules, the new template control flow (`@if`, `@for`, `@switch`, `@defer`), the `inject()` function, signal-based `input()` / `output()` / `model()`, `httpResource`, `provideZonelessChangeDetection`, and the direction of travel toward fully zoneless apps. Older Angular idioms (NgModules, `*ngIf`, constructor DI, `@Input()` decorators, RxJS-only state) get their own appendix so you can read legacy code without confusion, but the main text stays modern.

Highlights:

- **~50,000 words in English**, ~45,000 in Hebrew, delivered as A5 book pages with running headers, syntax-highlighted code blocks, and a full clickable PDF outline.
- **Signals-first, zoneless-ready pedagogy** — the book teaches Angular in the direction it is going, not the direction it came from.
- **Every chapter ends with exercises** — a mix of code exercises (with worked solutions in Appendix F) and reflection prompts.
- **Complete Hebrew edition** — same coverage, same code, translated pedagogical prose with a consistent glossary (transliterated Angular-specific nouns, translated general terms).
- **Reviewed by nine independent LLM agents** covering technical accuracy, internal consistency, code correctness, and Hebrew language quality — findings applied across three fix commits.
- **Six diagrams** for the concepts where visual aids beat prose: Compass's component tree, DI resolution walk, three RxJS marble diagrams, change-detection comparison, SSR lifecycle.
- **Accessibility appendix** covering `@angular/cdk/a11y`, ARIA in Angular templates, keyboard navigation, and route-change announcements.

## Who this book is for

Written for **total beginners to frontend development**. It assumes:

- You can read English (or Hebrew, for that edition).
- You can use a computer and a terminal.
- You are willing to type code into an editor and see what happens.

It does **not** assume:

- Any prior experience with Angular, React, Vue, or any other framework.
- Familiarity with TypeScript, Node.js, npm, or a build tool.
- Knowledge of how HTTP or servers work.

Chapter 2 teaches enough TypeScript to be productive. Chapter 3 covers the modern JavaScript features Angular relies on. Chapter 4 walks you through installing Node.js and the Angular CLI. If you already know one of those, skim; if you don't, take it slow — everything from Chapter 5 onward assumes them.

If you already write Angular professionally, this book is probably too gentle. It's designed for the first ~50 hours of the Angular learning curve, not the next 500.

## The Compass project

**Compass** is a personal task tracker. It has no code in this repository — it exists across the book's chapters as the vehicle for every concept. By Chapter 20 you will have built:

| Feature | Chapter |
|---|---|
| A single-screen to-do list with add and toggle | 5 – 6 |
| A signals-driven reactive UI with computed counts | 7 |
| A properly composed component tree (list / row / form) | 8 |
| A shared `TaskStore` service via dependency injection | 9 |
| A real HTTP backend with optimistic updates and revert | 10 |
| Search-as-you-type with RxJS operators | 11 |
| Reactive forms with typed values and validation | 12 |
| Routing, deep links, and lazy-loaded pages | 13 |
| Cross-store state, offline queue sketch, and persistence | 14 |
| Custom directives and pipes for reusable UI | 15 |
| Performance tuning: OnPush, `@defer`, image optimization | 16 |
| Unit, component-harness, and end-to-end tests | 17 |
| Server-side rendering and hydration | 18 |
| A deployed, CI-driven production build | 19 |

Compass is deliberately small enough to hold in your head and rich enough to justify every idea Angular offers. When you finish, it runs on the public internet.

## Chapter-by-chapter guide

### Part I — Foundations

**Chapter 1 — What Angular is, and when to reach for it.** A code-free map. Introduces the shape of a modern web app, the library-vs-framework distinction, and a plain-English tour of Angular's mental model. Ends with an honest preview of what Compass will (and won't) become.

**Chapter 2 — TypeScript enough for Angular.** The working subset of TypeScript. Types, interfaces, unions and literal types, narrowing, generics (lightly), decorators previewed, and the `!` / `?` / `??` operators. Motivated by shapes the book reuses — `Task`, `Habit`, `Session`.

**Chapter 3 — Modern JavaScript you'll actually use.** ES modules, arrow functions, template literals, destructuring, spread and rest, optional chaining, nullish coalescing, Promises, `async`/`await`, and the array methods you'll lean on daily.

**Chapter 4 — The CLI, your first app, and the anatomy of an Angular project.** Installing Node.js and the Angular CLI, running `ng new compass`, and a slow, file-by-file tour of everything the CLI produces (`package.json`, `angular.json`, `tsconfig.*`, `src/main.ts`, `src/index.html`, `src/app/*`, including the modern `provideBrowserGlobalErrorListeners` / `provideZonelessChangeDetection` defaults).

### Part II — Components and templates

**Chapter 5 — Components: the atom of an Angular app.** The `@Component` decorator field by field — selector, imports, template, styles. Inline vs external templates, view encapsulation, and the `:host` selector. You delete the CLI's starter and mount your first real component.

**Chapter 6 — Data binding and the new control flow.** Interpolation, property binding, event binding, and two-way binding. The modern `@if` / `@for` / `@switch` / `@let` syntax with `track`, `$index`, and `@empty` (the sub-block of `@for`). Class and style shortcuts. Built-in pipes. Explicit note on `ngModel` requiring `FormsModule`. Compass gains click-to-toggle and an "Add task" form.

**Chapter 7 — Signals: reactive state that feels normal.** `signal`, `computed`, `effect`, `set` vs `update`, and the "produce new arrays, never mutate" rule. Signal inputs (`input.required()`) and model signals (`model()`). Rewrites Compass's state as signals and lays out the zoneless-ready change-detection model.

**Chapter 8 — Composing components.** Passing data down with `input()`, sending events up with `output()`, and two-way binding via `model()`. Content projection with `<ng-content>` and named slots. `viewChild()`. Refactors Compass into `TaskList` / `TaskRow` / `AddTaskForm` — the container-and-presentation shape. Includes an ASCII diagram of Compass's full component tree.

### Part III — Services and the outside world

**Chapter 9 — Dependency injection, Angular's superpower.** Why DI exists, `@Injectable`, `providedIn: 'root'`, the `inject()` function, `provideX()` app-level providers, hierarchical injectors (with a walk-up diagram), and `InjectionToken`. Extracts Compass's task state into a shared `TaskStore`.

**Chapter 10 — HTTP: talking to real APIs.** `HttpClient`, request/response types, `firstValueFrom`, optimistic updates with rollback, HTTP interceptors (with imports), and the modern `httpResource` for signal-integrated fetches. Wires Compass to a `json-server` backend.

**Chapter 11 — RxJS essentials.** What an Observable is (contrasted with Promises and signals), the fifteen operators you'll reach for, and the two-way interop with signals via `toSignal` and `toObservable`. Marble diagrams for `debounceTime`, `switchMap`, and `exhaustMap`. Builds a search-as-you-type pipeline. Ends with a clear "signals for state, RxJS for streams" rule.

**Chapter 12 — Forms: capturing user input reliably.** Reactive forms over template-driven. `FormControl`, `FormGroup`, `FormArray`, `FormBuilder.nonNullable`, typed forms, built-in and custom validators, async validators, `valueChanges`, cross-field validation. Rebuilds "Add task," adds an edit form with title/due-date/tags using `effect()` to wait for required signal inputs.

### Part IV — Building a real app

**Chapter 13 — Routing: pages, params, guards, lazy loading.** Route definitions, `<router-outlet>`, `routerLink`, `routerLinkActive`, dynamic route parameters via `withComponentInputBinding()`, query parameters, guards (`canActivate` / `canMatch` / `canDeactivate`), resolvers (with proper `ResolveFn` imports), lazy loading with `loadComponent`, preloading. Compass becomes multi-page.

**Chapter 14 — State beyond one component.** The Store-per-concern pattern, cross-store reactivity via `effect`, a `persistedSignal` utility for `localStorage`, an offline mutation-queue sketch, and a survey of when NgRx SignalStore (`withEntities` from `@ngrx/signals/entities`) or classic NgRx is worth adopting.

**Chapter 15 — Directives, pipes, and reusable UI.** Custom pipes (`TimeAgo`, `Truncate`), attribute directives (`Autofocus`, `LongPress`) with clean `DestroyRef` teardown, the directive-vs-pipe-vs-component decision framework, `HostBinding`/`HostListener` and the modern `host` metadata, and a content-projected `EmptyState` component.

**Chapter 16 — Performance: change detection, `OnPush`, `@defer`, bundle analysis.** How to measure with Angular DevTools, Lighthouse, and `source-map-explorer`. `OnPush` and signal-driven fine-grained change detection (with a zone vs zoneless diagram). All `@defer` triggers with accurate descriptions (`on viewport`, `on idle`, `on interaction`, `on hover`, `on timer`, `on immediate`, `when`). `NgOptimizedImage` including the `fill` attribute.

### Part V — Production

**Chapter 17 — Testing.** Unit tests with `TestBed`, replacing services with spies via DI, testing signals (including async effects), testing pipes, `ComponentFixture` for DOM tests, custom **component harnesses** for readable test code, `RouterTestingHarness` (with `withComponentInputBinding` for signal inputs), and end-to-end tests with **Playwright**. Priority-ordered checklist of what to actually test.

**Chapter 18 — Server-side rendering and hydration.** SSR vs SSG vs CSR, `ng add @angular/ssr`, `provideClientHydration()`, `withHttpTransferCacheOptions` (imported from `@angular/platform-browser`), platform detection with `isPlatformBrowser`, per-route render modes (`Prerender` / `Server` / `Client`), and SEO metadata. Includes an ASCII diagram of the SSR request lifecycle.

**Chapter 19 — Deployment.** The two shapes of a production Angular app (static bundle vs Node server). Deploying to Netlify, Vercel, Cloudflare Pages, Firebase Hosting, or a container on Fly.io / Cloud Run. Environment configuration via `environment.ts` file replacements. HTTPS, CORS, cookies. A GitHub Actions pipeline that tests, builds, and deploys on every push. Modern `web-vitals` imports (`onINP` not `onFID`).

**Chapter 20 — Where to go next.** The Angular ecosystem beyond Compass: Angular Material and CDK, PrimeNG and other UI kits, NgRx (all flavors), Nx for monorepos, adjacent server frameworks (NestJS, AnalogJS), real-time/offline libraries, and accessibility tooling. A concrete four-week study plan for the month after finishing.

### Appendices

**Appendix A — Setting up your machine.** Platform-specific install notes for macOS, Windows, Linux. VS Code extension recommendations. Troubleshooting: PATH issues, `EACCES` errors, corporate proxies, port conflicts, file-watcher failures.

**Appendix B — Debugging Angular apps.** The three questions to ask before touching any code. Guided tour of browser DevTools and Angular DevTools. Reading Angular error codes (`NG0100`, `NG0201`, `NG0950`, `NG05104`) and TypeScript error messages. Common gotchas — missing `()` on signals, cold-Observable double-fetch, stale route params, CORS problems.

**Appendix C — Legacy Angular idioms you'll still meet.** Side-by-side old-vs-modern comparisons: NgModules ↔ standalone, constructor DI ↔ `inject()`, `@Input()` ↔ `input()`, `*ngIf`/`*ngFor` ↔ `@if`/`@for`, `RouterModule.forRoot` ↔ `provideRouter`, `@ViewChild` ↔ `viewChild()`, class-based interceptors ↔ `HttpInterceptorFn`, lifecycle hooks ↔ modern replacements. Correct migration schematic names (`ng generate @angular/core:standalone` and `:control-flow`).

**Appendix D — Resources.** Curated pointers for what to learn next: the official docs (`angular.dev`) and blog (`blog.angular.dev`), YouTube channels for tutorials (Joshua Morony, Decoded Frontend, Deborah Kurata, This Is Angular, Fireship, ng-conf and other conference channels), weekly newsletters, courses (Angular University, Ultimate Courses, Egghead), community forums (Discord, Stack Overflow, GH Discussions), podcasts and conferences, adjacent technology (TypeScript, RxJS, NgRx, Nx, NestJS, MDN), and a suggested-next-projects section for extending Compass.

**Appendix E — Accessibility.** A retrofit guide for the a11y considerations that touch every part of the app you built. Semantic HTML (buttons vs clickable divs), `@angular/cdk/a11y` (`LiveAnnouncer`, `FocusTrap`, `FocusMonitor`), ARIA in Angular templates via `[attr.aria-*]`, keyboard navigation, reactive forms with `aria-invalid` / `aria-describedby` / `role="alert"`, route-change announcements for screen readers, automated a11y auditing with `@axe-core/playwright`, eight SPA-specific traps.

**Appendix F — Solutions to selected exercises.** Worked solutions to the code exercises across Chapters 2, 3, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 19. Pure reflection prompts named as "yours to work through" — no answer provided by design.

**Appendix G — Cheat sheet.** A compact reference for the APIs and syntax you'll reach for most often: signals API, template syntax table, new control flow with `@defer` triggers, CLI commands, DI patterns, RxJS operator table, reactive-forms shape, router API, Angular error codes, common patterns (optimistic-update-with-revert, persisted signal, route param as input, search-as-you-type, testing spy), and a standalone-component skeleton.

## Hebrew edition

A **complete Hebrew (RTL) translation** of the book is available alongside the English one — all 20 chapters and 7 appendices, 378 pages, delivered from the same build pipeline. The English edition remains the primary deliverable; the Hebrew edition is fully independent and self-contained.

Read it: **[`build/learn_angular_he.pdf`](build/learn_angular_he.pdf)**

```bash
python3 build.py --lang he            # builds build/learn_angular_he.pdf
python3 build.py --lang he --html     # also emits an HTML preview
python3 build.py --lang he --chapter 07   # single-chapter Hebrew build for iteration
```

Translation conventions applied consistently across all 27 files in `content-he/`:

- **Angular-specific technical nouns are transliterated to Hebrew** (`קומפוננטה`, `סיגנל`, `דירקטיבה`, `פייפ`, `פריימוורק`, `ראוטר`, `באנדל`).
- **Established Hebrew tech terms are used where they exist** (`הזרקת תלויות` for dependency injection, `תבנית` for template, `שירות` for service, `רינדור בצד השרת` for SSR).
- **Product names, code identifiers, and CLI commands stay in Latin script** (Angular, TypeScript, Node.js, npm, VS Code, GitHub, Compass, `ng new`, `HttpClient`, `input()`).
- **Code blocks and inline `code` stay LTR** inside Hebrew prose. `style-he.css` uses `direction: ltr` on `<pre>` and `<code>` so shell commands, TypeScript, and templates render as authored.

The RTL stylesheet is `style-he.css` — the build script picks it automatically when `--lang he` is passed. It also flips blockquote and code-block accent borders to the right side, moves the running header to top-left (mirror of the English top-right), and sets a Hebrew-friendly font stack (Frank Ruhl Libre → David CLM → Rubik → David → serif fallback).

**Provenance note.** The Hebrew edition is an LLM translation of the original English source. It reads naturally, applies the glossary consistently, and has been reviewed by an independent LLM Hebrew reviewer with grammar and idiom findings applied. Before wider distribution, a native Hebrew speaker who also knows Angular is the recommended next reader — technical translation catches nuance in both dimensions that no LLM pass fully replicates.

## Reading the PDFs

The two most recent builds are committed at `build/learn_angular.pdf` and `build/learn_angular_he.pdf`. GitHub renders PDFs inline in the file browser — click either file to read it in your browser without downloading.

Both PDFs have **full outline / bookmarks**. Any PDF reader that shows an outline sidebar (Preview, Adobe, Firefox's built-in reader, Chrome's built-in reader, most mobile readers) will let you click straight to any chapter, section, or subsection instead of scrolling ~370 pages.

To download locally, either clone the repo or use GitHub's "Download raw file" button on the PDF's page.

## Building from source

Requirements:

- **Python 3.10 or later**.
- **WeasyPrint's system dependencies** — Pango, Cairo, GDK-PixBuf.
  - On Debian/Ubuntu: `sudo apt install libpango-1.0-0 libpangoft2-1.0-0`.
  - On macOS with Homebrew: `brew install pango`.
  - On Windows: see [WeasyPrint's install docs](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).

Then:

```bash
git clone https://github.com/johnny202408/learn-angular.git
cd learn-angular
pip install -r requirements.txt
python3 build.py                     # English → build/learn_angular.pdf
python3 build.py --lang he           # Hebrew  → build/learn_angular_he.pdf
```

### Faster iteration

While drafting or editing, building the whole ~370-page book on every save is unnecessary:

```bash
python3 build.py --chapter 07              # just Chapter 7 (English)
python3 build.py --lang he --chapter 07    # just Chapter 7 (Hebrew)
python3 build.py --chapter 07 --html       # also emit an HTML preview
```

The single-chapter PDF lands at `build/learn_angular_ch07.pdf` (or `learn_angular_he_ch07.pdf` for the Hebrew variant). The `--html` flag emits `build/learn_angular*.html` — useful for inspecting typography and layout without opening the PDF.

## Iterating on the book

Content lives in Markdown, one file per chapter, ordered by filename prefix (`NN_slug.md`). The build script sorts by prefix and assembles. To reorder chapters, rename files. To add a chapter, drop a new `.md` in `content/` (and `content-he/` if translating) with the next number in sequence.

Styling lives in `style.css` (English, LTR) and `style-he.css` (Hebrew, RTL). Both use identical page geometry (A5, 22mm × 20mm margins) and identical code-block treatment; they differ in text direction, font stack, and border sides.

Common edit-then-rebuild loops:

- **Fix a typo:** open the `.md` file, edit, save, rerun `python3 build.py`.
- **Change page size or fonts:** edit `style.css` and `style-he.css`, rerun both builds.
- **Add a new appendix:** create `content/28_appendix_h_*.md` and `content-he/28_appendix_h_*.md`, update the frontmatter to mention it, update the README, rerun.

## Project structure

```
learn-angular/
├── README.md                       # you are here
├── build.py                        # Markdown → PDF assembler
├── requirements.txt                # weasyprint, markdown, pygments, pyyaml
├── metadata.yaml                   # title, subtitle, edition
├── style.css                       # A5 book layout (English, LTR)
├── style-he.css                    # A5 book layout (Hebrew, RTL)
├── content/                        # English content (27 files)
│   ├── 00_frontmatter.md           # title + preface + how to read
│   ├── 01_what_is_angular.md
│   ├── 02_typescript.md
│   ├── 03_modern_javascript.md
│   ├── 04_cli_first_app.md
│   ├── 05_components.md
│   ├── 06_binding_and_control_flow.md
│   ├── 07_signals.md
│   ├── 08_composing_components.md
│   ├── 09_dependency_injection.md
│   ├── 10_http.md
│   ├── 11_rxjs.md
│   ├── 12_forms.md
│   ├── 13_routing.md
│   ├── 14_state.md
│   ├── 15_directives_and_pipes.md
│   ├── 16_performance.md
│   ├── 17_testing.md
│   ├── 18_ssr_hydration.md
│   ├── 19_deployment.md
│   ├── 20_where_to_go_next.md
│   ├── 21_appendix_a_setup.md
│   ├── 22_appendix_b_debugging.md
│   ├── 23_appendix_c_legacy.md
│   ├── 24_appendix_d_resources.md
│   ├── 25_appendix_e_accessibility.md
│   ├── 26_appendix_f_solutions.md
│   └── 27_appendix_g_cheatsheet.md
├── content-he/                     # Hebrew content (27 files, same structure)
│   └── … 00 through 27 in Hebrew
└── build/
    ├── learn_angular.pdf           # English, 369 pages, with PDF outline
    └── learn_angular_he.pdf        # Hebrew, 378 pages, with PDF outline
```

Chapters are ordered by filename prefix. `build.py` sorts them lexically before assembly. There is no separate table-of-contents file — the PDF outline is generated automatically from the heading structure by WeasyPrint (`bookmark-level` / `bookmark-label` on `h1`/`h2`/`h3` in the stylesheets).

## Design notes

Some deliberate choices worth naming.

**Signals before RxJS (Chapter 7 before Chapter 11).** Historically Angular books taught observables first because they were the only reactive primitive. With signals as the default in v18+, teaching RxJS first buries a beginner in operators before they've built anything. Signals get them productive; RxJS then arrives as "here's what you reach for when signals aren't enough."

**Testing is Chapter 17, not Chapter 3.** Beginners who see `TestBed` before they've felt the pain of a component breaking silently don't retain it. The project-driven approach plants "we'll test this properly later" pins throughout, then cashes them in.

**Modern-first, legacy in an appendix.** The main text uses `input()`, `inject()`, `@if`, `provideRouter`, `provideZonelessChangeDetection`. Older forms are documented in Appendix C so you can read legacy code without confusion, but they don't clutter the learning path.

**Accessibility is retrofitted, not integrated.** In an ideal book, every chapter would fold a11y into its topic. In this book, a11y sits in Appendix E, and each chapter's a11y implications are noted in prose (buttons vs clickable divs in Ch 6, focus management in Ch 8's `viewChild` section, route announcements in Ch 13) rather than fully explored. This is a real gap and the appendix is the honest acknowledgement of it — for the next revision, integrating a11y throughout is on the list.

**A5 page size.** Smaller than typical technical books; two pages fit on a monitor side-by-side, and the printed page is comfortable to hold.

**ASCII diagrams over SVG.** The six diagrams in the book are all ASCII inside `pre` blocks. That's uglier than SVG but portable (renders identically in the English and Hebrew editions since code blocks stay LTR in both), editable (no graphics program needed), and predictable across paginated layouts.

**Markdown all the way down.** No LaTeX, no proprietary format. `build.py` is under 100 lines. Anyone with Python and Pango installed can rebuild.

## Review history

The book has been through a **multi-agent LLM review-and-fix cycle**:

- **9 independent LLM reviewers** ran in parallel — 4 tech-accuracy reviewers (one per book part), 1 internal-consistency reviewer (cross-chapter drift, forward-reference verification, `Task` interface consistency), 2 code-sample correctness reviewers (mental compilation of every `ts`/`html`/`css`/`bash` block in the code-heavy chapters), 2 Hebrew language reviewers (grammar, gender agreement, glossary drift, anglicism catches).
- **~50 unique defects** identified after deduplication. Cross-agent-confirmed findings (caught by 2+ reviewers) were prioritized.
- **Three fix commits** applied the findings: (1) English mechanical fixes — renamed APIs, wrong error codes, missing imports, `EditTask` constructor bug, `LongPress` teardown leak, wrong `@defer` trigger descriptions; (2) Hebrew grammar/typo/anglicism pass; (3) preface honesty rewrite + new Appendix D (resources).
- **Enhancement pass** added the PDF outline, six diagrams, and Appendices E–G.

The one review dimension **not** covered here: a **native Hebrew speaker who is also an Angular developer**. That remains the highest-leverage remaining review — subtle idiom preferences and register issues are the kind of thing an LLM Hebrew reviewer flags less reliably than a human. If you know one, the Hebrew edition is at a good point to hand off.

## What the book deliberately doesn't build

Compass is honest about its scope. The following features are named in the book as **excellent next projects** (Appendix D has a full section on how to build them with the tools the book taught):

- **Authentication.** Wire Compass to Firebase Auth, Auth0, or a small NestJS backend with JWT. Add the `requireAuth` guard from Chapter 13 in earnest.
- **Habit tracking.** Build the `HabitStore` sketched in Chapter 9's exercises. Give habits a `frequency` field, per-habit history, and a `streakDays` computed signal.
- **Offline sync.** Wire up the `MutationQueue` sketch from Chapter 14. Buffer mutations to `localStorage` when offline; drain them (with proper ordering and revert-on-failure) when the browser comes back.
- **Drag-and-drop between buckets.** Use `@angular/cdk/drag-drop` to move tasks between "today," "this week," and "later" columns.
- **A real chart on the stats page.** Compass's stats page ends the book as a stub. Wire it up to Chart.js or D3 (lazy-loaded via `@defer`).

Each is a self-contained project that fits in a weekend or two, uses only the tools the book taught, and produces something you can show.

## Bonus — the author's Claude Code statusline (unrelated to the book)

This book was written entirely inside [Claude Code](https://docs.claude.com/en/docs/claude-code), and along the way the author's terminal statusline grew a small feature that turned out handy enough to share: a `🟢:PORT` segment that appears when a dev server is listening on one of the common ports, and disappears when nothing is up.

**Idle (no dev servers) — quiet:**

```
user@host:~/dev/py106 | Sonnet 4.6 | ctx: 42% | main | IL: +26°C | 19:57:22
```

**Server up on :8000 — indicator slides in between `main` and `IL:`:**

```
user@host:~/dev/py106 | Sonnet 4.6 | ctx: 42% | main | 🟢:8000 | IL: +26°C | 19:55:59
```

The segment stays silent when nothing is listening — no clutter in the common case. When any of the checked ports has a listener, they show up as `🟢:PORT` (multiple if several are up at once).

Save as `~/.claude/statusline.sh` and `chmod +x`:

```bash
#!/usr/bin/env bash
# Claude Code status line: user@host:dir | model | context% | git branch | dev servers | weather IL | time

input=$(cat)

# Identity: user@host:dir (from PS1 style)
identity="$(whoami)@$(hostname -s):$(pwd)"

# Model display name
model=$(echo "$input" | jq -r '.model.display_name // empty' 2>/dev/null)

# Context used percentage
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty' 2>/dev/null)

# Git branch (skip optional locks)
branch=$(git -c core.hooksPath=/dev/null branch --show-current 2>/dev/null)

# Dev servers: check common ports; silent when nothing is listening.
# Ports checked: 3000 (Node/json-server), 4200 (Angular), 5173 (Vite),
#                8000 (Django/FastAPI/uvicorn), 8080 (many).
# Override with STATUSLINE_PORTS env var, e.g. STATUSLINE_PORTS="8000 9000".
servers=""
ports=${STATUSLINE_PORTS:-"3000 4200 5173 8000 8080"}
for port in $ports; do
  if lsof -i :"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    servers="${servers}${servers:+ }🟢:$port"
  fi
done

# Weather in Israel (Celsius), cached for 10 minutes to avoid slowing the prompt
weather_cache="/tmp/.claude_weather_il.cache"
weather=""
if [ -f "$weather_cache" ]; then
  cache_age=$(( $(date +%s) - $(stat -c %Y "$weather_cache" 2>/dev/null || echo 0) ))
else
  cache_age=99999
fi
if [ "$cache_age" -gt 600 ]; then
  fetched=$(curl -s --max-time 4 "wttr.in/Israel?format=%t&m" 2>/dev/null | tr -d '\n')
  if [ -n "$fetched" ]; then
    echo "$fetched" > "$weather_cache"
    weather="$fetched"
  fi
else
  weather=$(cat "$weather_cache" 2>/dev/null)
fi

now=$(date +"%H:%M:%S")

parts=()
parts+=("$identity")
[ -n "$model" ] && parts+=("$model")
[ -n "$used_pct" ] && parts+=("ctx: $(printf '%.0f' "$used_pct")%")
[ -n "$branch" ] && parts+=("$branch")
[ -n "$servers" ] && parts+=("$servers")
[ -n "$weather" ] && parts+=("IL: $weather")
parts+=("$now")

printf '%s' "${parts[0]}"
for part in "${parts[@]:1}"; do
  printf ' | %s' "$part"
done
printf '\n'
```

Then reference it from `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "refreshInterval": 5
  }
}
```

`refreshInterval: 5` re-runs the command every 5 seconds, so the port indicator flips within seconds of starting or stopping a server. Override the ports checked with `export STATUSLINE_PORTS="8000 9000"` in your shell rc — defaults are 3000, 4200, 5173, 8000, 8080. Change `wttr.in/Israel` to your location, or delete the weather segment entirely — it's the only piece that costs network I/O.

Requirements: `lsof` (universal on macOS/Linux), `jq` (for pulling model and context info from Claude Code's JSON input), and `curl` (for the weather segment; drop it if you skip weather). The port check is ~1 ms per call, so even five ports at 5-second intervals adds no perceptible latency.

## Contributing and feedback

Written for personal use, but if you spot errors, unclear passages, or code samples that no longer work with the current Angular version, please open an issue. Pull requests welcome for typos and clarifications.

If you have subject-matter expertise — Angular framework internals, RxJS depths, native Hebrew fluency — a review comment on any specific chapter would be genuinely useful. The book has been reviewed by LLMs; it hasn't been reviewed by a human expert.

## License

The source and PDFs are shared publicly for individual learning use. If you'd like to teach from it, translate it into additional languages, or redistribute it, please open an issue first.
