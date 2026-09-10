# Appendix D. Resources — where to keep learning

The book you just finished is one door into Angular. The rooms on the other side are large, and most of them have people already inside them. This appendix is a curated list of where to go next — official material, video tutorials, blogs, books, communities, and adjacent tech worth knowing.

Everything here is a starting point, not a directive. Read one page from three sources and you will find yourself in a productive rabbit hole. Read the whole list and you will read for a year and build nothing. Pick one or two things per section.

## Official

**`angular.dev`** — the canonical documentation. Every API, every guide, every tutorial is here, kept in sync with the current version. If you land on `angular.io`, it will redirect; that domain is legacy. The "Guide" and "Reference" sections are worth bookmarking in that order.

**`blog.angular.dev`** — the team's official blog. Major-release announcements, deep-dive posts on new features (signals, zoneless, deferrable views), and RFCs when they arrive. Low-frequency but always high-signal.

**`github.com/angular/angular`** — the source of truth for the framework itself. The `CHANGELOG.md` is where every change lands before it makes the release notes. The Issues tab is where you'll open bug reports and check whether your bug is already known.

**Angular on YouTube** — the official channel publishes release videos, "Angular in X" explainers, and highlights from ng-conf. The production quality is high; the content is short.

## YouTube channels for tutorials

Independent Angular educators worth following, in rough order of how much modern-Angular content they publish:

- **Joshua Morony** — the largest independent Angular channel at the time of writing. Focuses on modern Angular (signals, standalone components, zoneless), RxJS patterns, and real-world architecture questions. Short and long-form. Excellent for solidifying what this book taught.
- **Decoded Frontend** (Dmytro Mezhenskyi) — deep-dive tutorials on specific Angular features. Covers reactive forms, RxJS, directives, and testing in depth. Slower-paced and more thorough than Joshua Morony's videos; better for the "wait, how does this work under the hood?" moments.
- **Deborah Kurata** — long-time Angular educator (also on Pluralsight). Her channel skews toward practical patterns for real applications. Strong on RxJS and state management.
- **This Is Angular** — a community channel featuring talks and interviews with Angular team members and community leaders.
- **Angular Nation / Angular Air** — community podcast/videocast with regular episodes on ecosystem topics.
- **Fireship** — not Angular-specific, but the occasional Angular video is a fast take on new features. Best for staying aware of the wider frontend landscape.

## Newsletters and blogs

- **This Week in Angular** — a weekly newsletter covering releases, blog posts, videos, and community projects. The single best way to stay current with 5 minutes of reading per week. Search for the current subscription URL.
- **`ng-newsletter.com`** — another long-running weekly Angular newsletter.
- **`inDepth.dev`** — deep technical articles from Angular team members and community experts. Slower-paced than the newsletters; better for the "I want to actually understand change detection" mood.
- **`blog.nrwl.io`** — the Nrwl (Nx) team's blog. Heavy on monorepo topics but also covers Angular architecture at scale.
- **`ngrx.io/docs`** — NgRx documentation and blog. Essential if you adopt any NgRx package.

## Books and long-form courses

The video-and-blog ecosystem is more current than any book, but there are still a few book-length resources worth mentioning:

- **Angular's own tutorials on `angular.dev`** — "Tour of Heroes" is the classic introduction; the newer "First Angular app" tutorial uses modern APIs. Both are free and current.
- **Angular University** (Vasco Cavalheiro) — a large course catalog on `angular-university.io`. Paid, but consistently updated and thorough.
- **Ultimate Courses** (Todd Motto) — modernized Angular courses at `ultimatecourses.com`.
- **Egghead** — bite-sized courses across the Angular ecosystem; some are free, some behind a subscription.

## Community and Q&A

- **Angular Discord** — the semi-official chat community. Fastest way to get a question answered in real time. Search for the current invite URL from `angular.dev`.
- **Stack Overflow** — the `[angular]` tag has decades of accumulated questions. Search before asking; if you must ask, follow the "minimal reproducible example" guidance in Appendix B.
- **r/Angular2** on Reddit — surprisingly active. Good for discussion; less good for specific technical questions.
- **`github.com/angular/angular/discussions`** — the official discussions forum. For questions that cross into framework internals or design decisions.

## Podcasts and conferences

- **Angular Air** — a long-running weekly podcast interviewing Angular team members and community figures. Historical episodes are worth mining.
- **ng-conf** (USA, annual) — the largest Angular conference. Talks are published to YouTube afterward. If you can only watch one conference's talks each year, watch this one.
- **NG-DE** (Germany) — the European Angular conference. Slightly deeper technical content on average than ng-conf's headline talks.
- **NG Poland** — the Polish Angular conference. Every year has at least a handful of talks worth watching.

## Adjacent technology

Angular sits on top of a stack; understanding the adjacent parts pays back quickly.

- **TypeScript** — Chapter 2 covered enough for Angular; the full language is much larger. `typescriptlang.org/docs/handbook/intro.html` is the canonical reference. When you find yourself stumped by a type error, that handbook is faster than searching.
- **RxJS** — `rxjs.dev` is the canonical docs. The interactive marble diagrams on the operator pages are the best way to build intuition for what each operator does.
- **NgRx** — if you go beyond hand-rolled signal stores, `ngrx.io` is the docs for both classic NgRx (Redux-style) and `@ngrx/signals`. Both are actively maintained.
- **Nx** — `nx.dev` is the docs for the monorepo tool with the best Angular integration. Worth learning if your team runs more than one Angular app.
- **NestJS** — `docs.nestjs.com`. If you need a Node backend that will feel familiar (decorators, DI, modules), NestJS is designed to be recognizable to Angular developers.
- **Web platform docs** — `developer.mozilla.org` (MDN) is the canonical reference for HTML, CSS, JavaScript, and browser APIs. When a template binding, event, or CSS property is confusing, MDN is faster than any framework doc.

## Suggested next projects

The features Compass deliberately doesn't build make excellent second projects. Each of them exercises a real skill and gives you something to show:

- **Add authentication.** Wire Compass to Firebase Auth, Auth0, or a small NestJS backend with JWT tokens. Add the `requireAuth` guard from Chapter 13 in earnest. Store the current user in a `UserStore` per the Chapter 14 pattern. Cover the login and logout flows with Playwright tests.
- **Add habit tracking.** Build the `HabitStore` sketched in Chapter 9's exercises. Give habits a `frequency` field, a per-habit history stored on the server, and a `streakDays` computed signal. Add a "today's habits" section to the home page and a per-habit history route.
- **Add offline sync.** Wire up the `MutationQueue` sketch from Chapter 14. Buffer mutations to `localStorage` when offline; drain them (with proper ordering and revert-on-failure) when the browser comes back. Test with Chrome DevTools' offline mode.
- **Add drag-and-drop between buckets.** Use `@angular/cdk/drag-drop` to move tasks between "today," "this week," and "later" columns. This exercises `viewChild`, `HostListener` (or the modern `host` metadata), and change detection under a stream of events.
- **Rewrite the stats page with a real chart library.** Compass's stats page ends the book as a stub. Wire it up to Chart.js or D3 (lazy-loaded via `@defer`) and show a real chart of task completions over time.
- **Ship it.** Pick a friend, actually deploy Compass with their name and their tasks, and see whether they use it a month later. Everything about maintaining a real app — bug reports, feature requests, deploy strategy — happens on the other side of shipping.

Each is a self-contained project that fits in a weekend or two, uses the tools this book taught, and produces something you can show. If you finish one, come back to the book and tell yourself which chapter's ideas turned out to be most important on the ground. That's how you consolidate a framework — not by reading more, but by shipping more.

## How to keep this list current

Everything above will drift. Channels rebrand. Newsletters shut down. Docs move. Two habits worth building:

- **Bookmark `blog.angular.dev` and check it every few weeks.** The team posts big changes there. If a big change happens and this appendix contradicts it, `blog.angular.dev` is right.
- **Subscribe to one weekly newsletter.** Five minutes per week is enough to know when the ecosystem shifts. If you learn about `provideZonelessChangeDetection` becoming default before it happens, you have half a year to migrate; if you learn about it three years later, you have a big deprecation to catch up on.

Angular is a large, actively-developed framework with a healthy community around it. You have exactly the tools you need to keep growing. The rest is a matter of showing up.
