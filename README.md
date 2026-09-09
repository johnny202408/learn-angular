# Learn Angular by Building Compass

**A project-driven, 313-page book that takes a total beginner from "what is a framework?" to a deployed, tested, offline-capable Angular application.**

> This is the source for the book. All 20 chapters and 3 appendices live in `content/` as plain Markdown. A small Python script (`build.py`) assembles them into a single A5 PDF using WeasyPrint. Edit any chapter, rerun the script, and you have a fresh PDF.

Read it now: **[`build/learn_angular.pdf`](build/learn_angular.pdf)** (313 pages · ~950 KB)

---

## Table of contents

- [About the book](#about-the-book)
- [Who this book is for](#who-this-book-is-for)
- [The Compass project](#the-compass-project)
- [Chapter-by-chapter guide](#chapter-by-chapter-guide)
  - [Part I — Foundations](#part-i--foundations)
  - [Part II — Components and templates](#part-ii--components-and-templates)
  - [Part III — Services and the outside world](#part-iii--services-and-the-outside-world)
  - [Part IV — Building a real app](#part-iv--building-a-real-app)
  - [Part V — Production](#part-v--production)
  - [Appendices](#appendices)
- [Reading the PDF](#reading-the-pdf)
- [Building the PDF from source](#building-the-pdf-from-source)
- [Project structure](#project-structure)
- [Design notes](#design-notes)
- [Contributing and feedback](#contributing-and-feedback)
- [License](#license)

---

## About the book

Most framework books either fly over concepts before you can touch them, or drown you in setup for fifty pages before rendering a single pixel. This book takes a third path: you meet each concept exactly when you need it to add a feature to a real app, and each chapter's exercises reinforce that feature in code.

The book targets **modern Angular (v18+)** — signals, standalone components, the new control flow (`@if`, `@for`, `@switch`, `@defer`), `inject()`, signal-based `input()`/`output()`, `httpResource`, and the trajectory toward zoneless change detection. Older Angular idioms (NgModules, `*ngIf`, constructor DI, `@Input()`/`@Output()` decorators, RxJS-only state) get their own appendix so you can read legacy code, but the main text moves forward.

Highlights:

- **313 pages, A5 book format**, with running headers, syntax-highlighted code blocks, and callouts for notes, warnings, and try-it experiments.
- **~46,500 words** across 20 chapters and 3 appendices — dense enough to teach, loose enough to read at the keyboard.
- **Every chapter ends with exercises** — a mix of code exercises, extensions to Compass, and reflection prompts.
- **Signals-first, zoneless-ready pedagogy** — the book teaches Angular in the direction it is going, not the direction it came from.

## Who this book is for

Written for **total beginners to frontend development**. It assumes:

- You can read English.
- You can use a computer and a terminal.
- You are willing to type things into an editor and see what happens.

It does **not** assume:

- Any prior experience with Angular, React, Vue, or any other framework.
- Familiarity with TypeScript, Node.js, npm, or a build tool.
- Knowledge of how HTTP or servers work.

Chapter 2 teaches enough TypeScript to be productive. Chapter 3 covers the modern JavaScript features Angular relies on. Chapter 4 walks you through installing Node.js and the Angular CLI. If you know any of that already, skim; if you don't, take it slow — the rest of the book depends on it.

If you already write Angular professionally, this book is probably too gentle. It's designed for the first ~50 hours of the Angular learning curve, not the next 500.

## The Compass project

**Compass** is a personal task and habit tracker. It has no code in this repository — it exists across the book's chapters as the vehicle for every concept. By the end of Chapter 20 you will have built:

| Feature | Chapter added |
|---|---|
| A single-screen to-do list with add and toggle | 5 – 6 |
| A signals-driven reactive UI with computed counts | 7 |
| A properly composed component tree (list / row / form) | 8 |
| A shared `TaskStore` service via dependency injection | 9 |
| A real HTTP backend with optimistic updates and revert | 10 |
| Search-as-you-type with RxJS operators | 11 |
| Reactive forms with validation and typed values | 12 |
| Routing, deep links, and lazy-loaded pages | 13 |
| Cross-store state, offline queue, and persistence | 14 |
| Custom directives and pipes for reusable UI | 15 |
| Performance tuning: OnPush, `@defer`, image optimization | 16 |
| Unit, component-harness, and end-to-end tests | 17 |
| Server-side rendering and hydration | 18 |
| A deployed, CI-driven production build | 19 |

Compass is deliberately small enough to hold in your head and rich enough to justify every idea Angular offers. When you finish, it will run on the public internet.

## Chapter-by-chapter guide

### Part I — Foundations

**Chapter 1 — What Angular is, and when to reach for it.** A code-free map of where you are. Introduces the shape of a modern web app, the library-vs-framework distinction, and a plain-English tour of Angular's mental model. Ends with a preview of what Compass will become.

**Chapter 2 — TypeScript enough for Angular.** The working subset of TypeScript. Types, interfaces, unions and literal types, narrowing, generics (lightly), decorators (previewed), and the `!` / `?` / `??` operators. Motivated throughout by shapes the book will reuse — `Task`, `Habit`, `Session`.

**Chapter 3 — Modern JavaScript you'll actually use.** ES modules, arrow functions, template literals, destructuring, spread and rest, optional chaining, nullish coalescing, Promises, `async`/`await`, and the array methods (`map`, `filter`, `reduce`, `find`) you'll lean on in every chapter afterward.

**Chapter 4 — The CLI, your first app, and the anatomy of an Angular project.** Installing Node.js and the Angular CLI, running `ng new compass`, and a slow, file-by-file tour of everything the CLI produces (`package.json`, `angular.json`, `tsconfig.*`, `src/main.ts`, `src/index.html`, `src/app/*`). By the end, `ng serve` is running and every file makes sense.

### Part II — Components and templates

**Chapter 5 — Components: the atom of an Angular app.** The `@Component` decorator field by field — selector, imports, template, styles. Inline vs external templates, view encapsulation, and the `:host` selector. You delete the CLI's starter and mount your first real component: a hardcoded task list.

**Chapter 6 — Data binding and the new control flow.** Interpolation, property binding, event binding, and two-way binding. The modern `@if` / `@for` / `@switch` / `@let` syntax with `track`, `$index`, and `@empty`. Class and style shortcuts. Built-in pipes. Compass gains a click-to-toggle and an "add task" form.

**Chapter 7 — Signals: reactive state that feels normal.** `signal`, `computed`, `effect`, `set` vs `update`, and the "produce new arrays, never mutate" rule. Signal inputs (`input.required()`) and model signals (`model()`). Rewrites Compass's fields as signals and explains the change-detection story that leads to zoneless Angular.

**Chapter 8 — Composing components.** Passing data down with `input()`, sending events up with `output()`, and two-way binding via `model()`. Content projection with `<ng-content>` and named slots. `viewChild()`. Refactors Compass into `TaskList` / `TaskRow` / `AddTaskForm` — the container-and-presentation shape.

### Part III — Services and the outside world

**Chapter 9 — Dependency injection, Angular's superpower.** Why DI exists, `@Injectable`, `providedIn: 'root'`, the `inject()` function, `provideX()` app-level providers, hierarchical injectors, and `InjectionToken`. Extracts Compass's task state into a shared `TaskStore` service.

**Chapter 10 — HTTP: talking to real APIs.** `HttpClient`, request/response types, `firstValueFrom`, optimistic updates with rollback, HTTP interceptors (auth headers, 401 handling), and the modern `httpResource` for signal-integrated fetches. Wires Compass to a `json-server` backend so tasks persist across refreshes.

**Chapter 11 — RxJS essentials.** What an Observable is (contrasted with Promises and signals), the fifteen operators you'll actually reach for (`map`, `filter`, `tap`, `debounceTime`, `distinctUntilChanged`, `switchMap`, `exhaustMap`, `catchError`, `retry`, `combineLatest`…), and the two-way interop with signals via `toSignal` and `toObservable`. Builds a search-as-you-type pipeline. Ends with a clear "signals for state, RxJS for streams" rule.

**Chapter 12 — Forms: capturing user input reliably.** Reactive forms over template-driven. `FormControl`, `FormGroup`, `FormArray`, `FormBuilder.nonNullable`, typed forms, built-in and custom validators, async validators, `valueChanges`, and cross-field validation. Rebuilds Compass's "add task" input and adds an edit form with title, due date, and a dynamic list of tags.

### Part IV — Building a real app

**Chapter 13 — Routing: pages, params, guards, lazy loading.** Route definitions, `<router-outlet>`, `routerLink`, `routerLinkActive`, dynamic route parameters via `withComponentInputBinding()`, query parameters, guards (`canActivate` / `canMatch` / `canDeactivate`), resolvers, lazy loading with `loadComponent`, and preloading strategies. Compass becomes a multi-page app with home, stats, and per-task detail routes.

**Chapter 14 — State beyond one component.** The Store-per-concern pattern (private writable signal, readonly public view, methods that describe intent), cross-store reactivity via `effect`, a `persistedSignal` utility for `localStorage`, an offline-mutation queue, and a survey of when NgRx SignalStore vs classic NgRx is worth adopting.

**Chapter 15 — Directives, pipes, and reusable UI.** Custom pipes (`TimeAgo`, `Truncate`), attribute directives (`Autofocus`, `LongPress`), a comparison of directive-vs-pipe-vs-component decision criteria, `HostBinding`/`HostListener` and the modern `host` metadata, and a content-projected `EmptyState` component that Compass reuses.

**Chapter 16 — Performance: change detection, `OnPush`, `@defer`, bundle analysis.** How to measure with Angular DevTools, browser Performance tab, Lighthouse, and `source-map-explorer`. `OnPush`, signal-driven fine-grained change detection, the roadmap to zoneless. `@defer` blocks with all their triggers. `NgOptimizedImage`. Making `computed` do memoization work for you.

### Part V — Production

**Chapter 17 — Testing.** Unit tests with `TestBed`, replacing services with spies via DI, testing signals (including async effects), testing pipes, `ComponentFixture` for DOM tests, custom **component harnesses** for readable test code, `RouterTestingHarness`, and end-to-end tests with **Playwright**. Includes a priority-ordered checklist of what to actually test.

**Chapter 18 — Server-side rendering and hydration.** SSR vs SSG vs CSR, `ng add @angular/ssr`, `provideClientHydration()`, transfer state (so the client doesn't re-fetch what the server already had), platform detection with `isPlatformBrowser`, per-route render modes (`Prerender` / `Server` / `Client`), and SEO metadata via `Title` and `Meta`.

**Chapter 19 — Deployment.** The two shapes of a production Angular app (static bundle vs. Node server). Deploying to Netlify, Vercel, Cloudflare Pages, Firebase Hosting, or a container on Fly.io / Cloud Run. Environment configuration via `environment.ts` file replacements. HTTPS, CORS, cookies. A GitHub Actions pipeline that tests, builds, and deploys on every push. Error reporting and analytics.

**Chapter 20 — Where to go next.** The Angular ecosystem beyond Compass: Angular Material and CDK, PrimeNG and other UI kits, NgRx, Nx for monorepos, adjacent server frameworks (NestJS, AnalogJS, Astro islands), real-time and offline libraries (SignalR, RxDB), and accessibility tooling. A concrete four-week study plan for the month after finishing the book.

### Appendices

**Appendix A — Setting up your machine.** Platform-specific installation notes for macOS, Windows, and Linux. Recommended VS Code extensions. A troubleshooting section that covers PATH issues, `EACCES` errors, corporate proxies, port conflicts, and file-watcher failures.

**Appendix B — Debugging Angular apps.** The three questions to ask before touching any code. A guided tour of browser DevTools and Angular DevTools. Reading Angular error codes (`NG0100`, `NG0201`, `NG0304`, …) and TypeScript error messages. Common gotchas — missing `()` on signals, cold-Observable double-fetch, stale route params, CORS problems. When and how to ask for help productively.

**Appendix C — Legacy Angular idioms you'll still meet.** Side-by-side old-vs-modern comparisons: NgModules ↔ standalone, constructor DI ↔ `inject()`, `@Input()` ↔ `input()`, `*ngIf`/`*ngFor` ↔ `@if`/`@for`, `RouterModule.forRoot` ↔ `provideRouter`, `@ViewChild` ↔ `viewChild()`, class-based interceptors ↔ `HttpInterceptorFn`, and lifecycle hooks ↔ modern replacements. Includes guidance on when to migrate old code and when to leave it alone.

## Reading the PDF

The most recent build is committed at [`build/learn_angular.pdf`](build/learn_angular.pdf). GitHub renders PDFs inline — click the file to read it in your browser without downloading.

If you'd rather have a local copy, either clone the repo or download the raw file directly from GitHub's "Download raw file" button on the PDF's page.

## Building the PDF from source

Requirements:

- Python 3.10 or later
- WeasyPrint's system dependencies (Pango, Cairo, GDK-PixBuf). On Debian/Ubuntu: `sudo apt install libpango-1.0-0 libpangoft2-1.0-0`. On macOS with Homebrew: `brew install pango`. On Windows, see [WeasyPrint's install docs](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).

Then:

```bash
git clone https://github.com/johnny202408/learn-angular.git
cd learn-angular
pip install -r requirements.txt
python3 build.py
```

The output lands at `build/learn_angular.pdf`.

### Iterating on a single chapter

While drafting or editing, building the whole 313-page book on every save is unnecessary:

```bash
python3 build.py --chapter 07     # builds just Chapter 7
python3 build.py --chapter 07 --html  # also emits an HTML preview
```

The single-chapter PDF lands at `build/learn_angular_ch07.pdf`.

### Regenerating the HTML preview

```bash
python3 build.py --html
```

Produces `build/learn_angular.html` — useful for inspecting typography and layout without opening the PDF.

## Hebrew edition (pilot)

A Hebrew (RTL) variant of the book is available as an **early pilot** — front matter and Chapter 1 only. It exists to prove out the toolchain (RTL layout, mixed-direction text, code blocks staying LTR inside Hebrew prose) and to establish glossary conventions. The English edition remains the primary, complete deliverable.

```bash
python3 build.py --lang he            # builds build/learn_angular_he.pdf
python3 build.py --lang he --html     # also emits an HTML preview
```

- Hebrew content lives in `content-he/`. Adding more chapters is a matter of translating and dropping files with matching `NN_slug.md` names.
- The RTL stylesheet is `style-he.css` — the build script picks it automatically when `--lang he` is passed.
- Code blocks, inline `code`, and technical identifiers stay left-to-right even inside Hebrew paragraphs; product names (Angular, TypeScript, Node.js, Compass) stay in Latin script.
- Angular-specific technical nouns are transliterated to Hebrew (`קומפוננטה`, `סיגנל`, `דירקטיבה`, `פייפ`); pedagogical prose uses natural Hebrew; established terms with strong Hebrew equivalents (`הזרקת תלויות` for dependency injection, `תבנית` for template, `שירות` for service) use the Hebrew form.

**The Hebrew pilot is an LLM-generated first pass.** It reads naturally and applies the glossary consistently, but before wider distribution it needs a review by a native Hebrew speaker who is also familiar with Angular — technical translation catches nuance in both dimensions and no unreviewed machine translation is publication-grade.

## Project structure

```
learn-angular/
├── README.md                       # you are here
├── build.py                        # Markdown → PDF assembler
├── requirements.txt                # weasyprint, markdown, pygments, pyyaml
├── metadata.yaml                   # title, subtitle, edition
├── style.css                       # A5 book layout, code highlighting, running headers
├── style-he.css                    # RTL stylesheet for the Hebrew pilot
├── content/
│   ├── 00_frontmatter.md           # Title + preface
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
│   └── 23_appendix_c_legacy.md
├── content-he/                     # Hebrew pilot content (front matter + Chapter 1)
│   ├── 00_frontmatter.md
│   └── 01_what_is_angular.md
└── build/
    ├── learn_angular.pdf           # the latest English build (313 pp)
    └── learn_angular_he.pdf        # the latest Hebrew pilot build (~18 pp)
```

Chapters are ordered by filename prefix; `build.py` sorts them lexically before assembly. To reorder, rename.

## Design notes

A few decisions worth naming:

- **Signals before RxJS (Chapter 7 before Chapter 11).** Historically Angular books taught observables first because they were the only reactive primitive. With signals as the default in v18+, teaching RxJS first buries a beginner in operators before they've built anything. Signals get them productive; RxJS then arrives as "here's what you reach for when signals aren't enough."
- **Testing is Chapter 17, not Chapter 3.** Beginners who see `TestBed` before feeling the pain of a component breaking silently don't retain it. The project-driven approach plants "we'll test this properly later" pins throughout, then cashes them in.
- **Modern-first, legacy in an appendix.** The main text uses `input()`, `inject()`, `@if`, `provideRouter`. Older forms are documented in Appendix C so you can read legacy code without confusion, but they don't clutter the learning path.
- **A5 page size.** Smaller than typical technical books; two pages fit on a monitor side-by-side, and the printed page is comfortable to hold.
- **Markdown all the way down.** No LaTeX, no proprietary format. `build.py` is under 100 lines. Anyone with Python and Pango installed can rebuild.

## Contributing and feedback

The book is written for personal use, but if you spot errors, unclear passages, or code samples that no longer work with the current Angular version, please open an issue. Pull requests welcome for typos and clarifications.

## License

The source and PDF are shared publicly for individual learning use. If you'd like to teach from it, translate it, or redistribute it, please open an issue first.
