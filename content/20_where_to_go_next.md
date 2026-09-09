# Chapter 20. Where to go next

Compass exists. You built it. In the process you met every idea a working Angular developer relies on: components, templates, signals, dependency injection, HTTP, RxJS, forms, routing, state management, directives, pipes, performance, testing, SSR, deployment. That is a full skill set. Not a starter kit — a working set. If you understood what you typed in each chapter, you can walk into an Angular codebase and be productive.

This chapter is the map for what to do with that.

## The ecosystem beyond Compass

Compass used a small subset of the Angular ecosystem. Here is what else is out there, in the order you are most likely to want it.

### Angular Material and the CDK

**Angular Material** (`@angular/material`) is Google's Material Design component library for Angular. Buttons, dialogs, tables, tabs, snackbars, autocompletes, date pickers, drag-and-drop — all designed to a coherent visual system and tested against accessibility guidelines.

**Angular CDK** (`@angular/cdk`) is the primitives under Material. If you don't want the Material look but want the a11y-correct behaviors (a proper focus trap, an accessible dialog, keyboard navigation for tables, drag-and-drop, virtual scrolling, overlays), CDK is your library. Even large custom design systems reach for CDK to avoid re-implementing the hard parts.

Compass would benefit from CDK for its edit dialog, keyboard navigation, and drag-and-drop between "today" and "later." Add it any time — CDK has no visual opinion.

### PrimeNG, Nebular, and other UI kits

Not every project wants Material. **PrimeNG** is a large component library with a business-app aesthetic. **Nebular** is a comprehensive UI kit built around a theme system. **Taiga UI** is a modern Angular UI kit. **Spartan/ui** is a shadcn-inspired kit.

The pattern is the same in each: install, import, use. The right choice depends on how your app should look; if you're building an internal tool, PrimeNG's density is a match; if it should feel modern and light, Spartan is a match.

### NgRx and the state ecosystem

Chapter 14 introduced state patterns. The libraries worth knowing beyond that:

- **`@ngrx/signals`** — signal-based state, with `signalStore`, `withEntities`, and effects.
- **`@ngrx/store`** — the classic Redux-for-Angular. Actions, reducers, selectors, effects. Bigger commitment, bigger payoff on complex apps.
- **`@ngrx/data`** — reduces the "we need an entity store" boilerplate on top of Store.
- **`@rx-angular/state`** — a lighter, RxJS-first alternative to NgRx.

Pick the smallest one that solves your problem. Do not adopt NgRx Store on a small app "just in case"; the ceremony will drag every feature.

### Nx: the monorepo tooling

**Nx** is a monorepo tool with deep Angular integration. If your team is building multiple Angular apps that share code — a customer app and an admin app that both use the same design system, say — Nx makes the shared library, code-generation, testing, and caching much better than what plain Angular CLI provides.

Nx also works for polyglot repos (Angular + Node + Nest + React). Its overhead pays off around 5+ people and 2+ apps.

### Testing beyond what we covered

Chapter 17 covered TestBed, harnesses, and Playwright. Two more libraries worth knowing:

- **Cypress** — an older Playwright competitor. Solid, especially for teams already using it.
- **Storybook** — not a test runner, but adjacent: interactive documentation for your components, with visual regression testing available via addons. Perfect for design systems.
- **jest-preset-angular** or **Jest with @angular/build** — if you want to use Jest instead of Jasmine. Vitest is now the more forward-looking alternative.

### Server frameworks that pair well

If you build a backend to go with Compass, three Angular-adjacent choices:

- **NestJS** — a Node backend framework whose design is unmistakably inspired by Angular (decorators, DI, modules). Angular devs learn it in a day.
- **AnalogJS** — a meta-framework built on Angular, similar in shape to Next.js for React. If you want file-based routing, server functions, and SSR/SSG baked in, AnalogJS is worth exploring.
- **Astro with Angular islands** — Astro is a content-first framework that can embed Angular components as interactive "islands." Useful for content-heavy sites that need small interactive pieces.

### Real-time and offline

Compass in this book had a mutation queue but no real-time. Two libraries make it interactive:

- **`@microsoft/signalr`** (SignalR) or **socket.io-client** — WebSocket abstractions for pushing updates from the server to the client.
- **RxDB** — a client-side reactive database with server-sync built in. It replaces `MutationQueue` and much of `TaskStore` with a small, working library.

If Compass ever grows into a collaborative app, one of these will be in the stack.

### Accessibility

Angular apps can be accessible; they can also be inaccessible. The tools:

- **`@angular/cdk/a11y`** — focus trap, focus monitor, live announcers.
- **`axe-core`** and **`@axe-core/playwright`** — automated a11y audits. Add to CI.
- The MDN pages on ARIA and semantic HTML — required reading if you're the person on the team who cares about a11y.

## A study plan for the next month

Concrete things to do, in order.

**Week 1: Build again.** Pick a new small app — a reading list, a workout log, a bookmark manager — and build it from scratch, using only the ideas in this book. Give yourself a week, and don't peek back at Compass except when stuck. This is where the material becomes muscle memory.

**Week 2: Read someone else's code.** Clone a small, well-regarded Angular open-source project. Some starting points:

- **Angular Material's source** — good code, high standards, well-tested.
- **Nx's example apps** — mid-sized realistic monorepos.
- **Angular Realworld** — the "realworld" reference implementation for the Angular framework.

Read for a few hours, following one feature end-to-end. Note idioms you didn't know.

**Week 3: Contribute.** Find an issue tagged `good first issue` on any Angular-adjacent project — Angular itself, Angular Material, NgRx, RxJS. Fix it. The PR process teaches you as much as the code did.

**Week 4: Answer questions.** Open Stack Overflow or the Angular Discord and answer beginner Angular questions. The best way to consolidate what you know is to explain it to someone else who is stuck.

## Staying current

Angular has a well-run release cadence and a reasonable public record. Where to keep up:

- **The official blog** at `blog.angular.io` announces releases and RFCs.
- **The Angular Twitter/X account** (`@angular`) posts release videos.
- **This Week in Angular** (a newsletter, findable via web search) summarizes the ecosystem weekly.
- **YouTube channels**: Deborah Kurata, Joshua Morony, Angular Air, Angular Nation — good for feature deep-dives.
- **Conferences**: ng-conf (US), NG-DE (Germany), NG Poland — talks are usually on YouTube afterward.

You do not need to consume all of these. Pick one or two and check in monthly.

## What Angular is becoming

At the time of writing, Angular is in the middle of a quiet transformation. Signals, standalone components, and the new control flow have shifted the mental model; zoneless is coming; SSR and hydration are mature. If you learned Angular five years ago, the framework today would surprise you.

That trajectory is worth knowing because the ideas you learned in this book are the ideas Angular is moving toward, not away from. Signals will keep expanding — signal-based forms, resource, effect improvements. NgModules will keep receding. Zoneless will become the default. The gap between "this book" and "the future" is small; the gap between "an older Angular book" and "the future" is large.

## A closing note

You started this book not knowing what a framework was. You are ending it having built and deployed a real Angular application, complete with authentication, offline support, tests, and CI. The steps between those two points — every chapter — were designed to be small enough to take one at a time and large enough that at the end you were doing real work.

Compass is yours. Extend it. Use it. Rewrite it in a year to see how you have grown. The best sign that a foundation is solid is that you can build past it, and this book was meant to leave you a foundation, not a ceiling.

Angular is a large framework in a large ecosystem. You will not know all of it. You do not need to. You know enough to look up what you don't, understand what you find, and add it to your working set. That is what "learning a framework" actually means, and you have done it.

Good luck. Ship things. Come back to the exercises in a few months and see how much easier they are.
