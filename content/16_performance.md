# Chapter 16. Performance: change detection, `OnPush`, `@defer`, bundle analysis

Compass is fast on your laptop. It is probably not fast on a five-year-old phone on 4G. This chapter closes that gap. We measure Compass, apply the four techniques that matter most in an Angular app, and finish with a smaller, faster Compass that is ready for the real world.

The four techniques:

1. `OnPush` change detection (or, better, signals-driven change detection).
2. `@defer` blocks for parts of the UI that don't need to load immediately.
3. `NgOptimizedImage` for images that block time-to-interactive.
4. Bundle analysis, to see what your users actually download.

We will also touch on zoneless Angular — the direction of travel that ties several of these together.

## Measure first

Never optimize without measuring. Angular gives you three good views into performance, and the browser gives you a fourth.

**Angular DevTools** is a browser extension that shows your component tree with change-detection metrics. Every time Angular checks a component's bindings, it records how long it took. Slow components are colored red. Install it from the Chrome or Edge extension store and open it via the browser's regular DevTools panel.

**The Performance tab in the browser DevTools** records the entire main thread. Open it, click record, click around in Compass, stop. You will see the flame chart of every function that ran. Look for long tasks (>50ms) and functions high in the flame chart.

**Lighthouse** (built into Chrome DevTools) runs a synthetic audit that includes Largest Contentful Paint, Total Blocking Time, and Cumulative Layout Shift — the metrics Google uses to score user-perceived performance.

**`ng build --configuration production`** builds an optimized bundle and prints the final file sizes. This is the fastest way to see whether a change made the download bigger or smaller.

Run all four before you touch anything. If Compass is already fast enough for your target devices, close this chapter.

## Change detection: the classic story

Angular's default change detection is a *tree walk*. After every event (click, HTTP response, setTimeout, Promise resolution), Angular walks the entire component tree and checks every binding. If a binding's value has changed since the last check, it updates the DOM.

Zone.js is the library that intercepts every async API to trigger this walk. Without it, Angular has no idea when your code has changed state.

The walk is fast in small apps. It gets slow when the tree has thousands of bindings or when a single binding calls a method that does real work.

### `ChangeDetectionStrategy.OnPush`

You can opt a component out of the default tree-walking. `OnPush` mode tells Angular: "Only check this component when one of its input references changes, or an event fires on it, or an Observable it subscribes to via `async` pipe emits, or one of the signals it reads changes."

```ts
import { Component, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-task-row',
  changeDetection: ChangeDetectionStrategy.OnPush,
  // ...
})
```

`OnPush` reduces the amount of checking dramatically. In a signal-heavy app like ours, its side effects are barely visible — signals already know which components read them, and only those components get checked.

Best practice: **set `OnPush` on every component**. In a signal-driven codebase, you get precision for free. In a codebase mixing signals and older patterns, `OnPush` forces you to be explicit about state, which is a good thing.

### Zoneless: the direction of travel

Modern Angular can run without Zone.js entirely. Change detection triggers only from signal changes and from a few Angular-managed sources. Every `setTimeout` or `Promise.resolve()` no longer schedules a re-check.

Enabling it is one line in `app.config.ts`:

```ts
import { provideZonelessChangeDetection } from '@angular/core';

providers: [
  provideZonelessChangeDetection(),
  // Remove provideZoneChangeDetection() if it's there.
],
```

Then remove the `zone.js` polyfill from `angular.json` (in the `polyfills` array).

`provideZonelessChangeDetection` is the stable API (Angular v20+). Earlier versions used `provideExperimentalZonelessChangeDetection`, which was renamed once the feature stabilized — if you're on an older Angular, use that spelling. In a signal-first app — which Compass is — zoneless works. The parts that would break under zoneless are:

- Code that relies on `setTimeout` to cause a re-render. Rewrite to update a signal.
- `Promise.then` chains that update state without going through signals or `async` pipe. Same fix.
- Third-party libraries that dispatch DOM events outside Angular's awareness. Wrap the event source with a signal or an Observable that Angular can track.

Zoneless is stable as of Angular v20 (was called *experimental* zoneless in v18/v19). Every design decision in this book has been zoneless-ready — the switch is a single provider change plus removing the `zone.js` polyfill.

## `@defer` blocks

Some parts of the UI aren't needed on first paint. Compass's "stats" page has a chart library it can lazy-load. A task detail page has an image gallery that only matters when the user scrolls to it. The "unsubscribe" section of a settings page is rarely visited.

`@defer` blocks defer the loading and rendering of a chunk of template until a condition is met. The syntax:

```html
@defer (on viewport) {
  <app-heavy-chart [data]="stats()" />
} @placeholder {
  <div class="chart-placeholder">Loading chart…</div>
} @loading (after 100ms; minimum 300ms) {
  <div class="spinner"></div>
} @error {
  <p>Could not load the chart.</p>
}
```

The parts:

- **`@defer (on viewport)`** — start loading when the placeholder scrolls into view.
- **`@placeholder`** — what to render before the trigger fires. Must be simple markup; no heavy components allowed here (or the placeholder itself becomes heavy).
- **`@loading`** — what to render while the deferred chunk is downloading, if that takes long enough to be worth showing.
- **`@error`** — what to render if loading fails.

Triggers other than `on viewport`:

- `on idle` — when the browser is idle after page load (fires via `requestIdleCallback`).
- `on interaction` — when the user clicks or presses a key on a specified element.
- `on hover` — when the user hovers or focuses (`mouseenter`/`focusin`) — distinct from `interaction`.
- `on timer(30s)` — after a fixed delay.
- `on immediate` — as soon as non-deferred content on the page has finished rendering (useful for background chunks that don't need to block the initial paint).
- `when someSignal()` — programmatic trigger.

Deferred blocks are separate chunks in the build output. They download in the background, chunked by trigger. `@defer` is the single largest lever most Angular apps have for reducing initial bundle size without lazy-loading whole routes.

For Compass, we'll defer the stats page's chart until the container scrolls into view. That saves the chart library (a few hundred KB) from the initial bundle.

## `NgOptimizedImage`

Images are often the largest asset on a page. Angular's `NgOptimizedImage` directive handles size hints, lazy-loading below the fold, priority loading of the LCP image, and a few other tricks that lighthouse-audit checklists demand.

Import and use:

```ts
import { NgOptimizedImage } from '@angular/common';

@Component({
  imports: [NgOptimizedImage],
  // ...
})
```

```html
<img ngSrc="/assets/hero.jpg" width="800" height="400" priority alt="Compass" />
<img ngSrc="/assets/footer.jpg" width="1200" height="300" alt="footer" />
```

Notes:

- `ngSrc` (not `src`) enables the directive.
- `width` and `height` are required — *unless* you use `fill`, which sizes the image to fill its positioned parent (useful for responsive layouts). Either way, the directive prevents layout shift.
- `priority` marks this image as the LCP candidate. Include it on at most one image per screen.
- Off-screen images without `priority` are lazy-loaded by default.

For Compass we do not have many images (it is a text-heavy app), but if you add a user avatar or a habit-icon, use `NgOptimizedImage`.

## Bundle analysis

`ng build` prints file sizes. That is a start. For a real look at what's inside your bundle, use `source-map-explorer`:

```bash
npm install --save-dev source-map-explorer
ng build --configuration production --source-map
npx source-map-explorer dist/compass/browser/main-*.js
```

It opens an interactive treemap of your bundle: modules colored by size, grouped by source. You will usually find:

- **Angular itself**: 150–250 KB gzipped. Not much you can do about this.
- **Your own code**: usually tiny for a small app; the file you spent a week on is 10 KB.
- **Third-party libraries**: often the surprise. A charting library, a date library, or an icon set can dwarf everything else.

The two levers when third-party libraries dominate:

- **Tree-shaking**. Import only what you use. `import { format } from 'date-fns'` bundles just `format`; `import * as dateFns from 'date-fns'` bundles the whole thing.
- **Lazy or deferred loading**. Move the library behind an `@defer` or a lazy route. It does not need to be in the initial bundle.

Compass uses very few third-party libraries. If you extend it — with a chart library for the stats page, say — apply these levers early.

## `trackBy` in `@for`, revisited

You met `track` in Chapter 6. It matters for performance too.

```html
@for (task of tasks(); track task.id) {
  <app-task-row [task]="task" />
}
```

Without `track`, Angular would re-create every DOM node when the array reference changed. With `track task.id`, Angular reuses nodes by identity — moves them if positions changed, adds new ones for new ids, removes nodes for absent ids. Reused nodes preserve focus, animations, and any imperative state.

For long lists — hundreds of items — `track` by a stable id is the difference between "instant" and "sluggish."

For truly gigantic lists (thousands), reach for *virtual scrolling*: Angular Material's CDK includes a `cdk-virtual-scroll-viewport` that only renders the visible items. Compass will never need it, but it exists.

## `computed` and memoization

`computed` caches. That is one of its virtues.

```ts
readonly expensiveDerivation = computed(() => {
  // This body runs only when its dependencies change.
  return tasks().sort(complexComparator).slice(0, 20);
});
```

If your template calls `expensiveDerivation()` in ten places, the body runs once per change to `tasks`, and the ten reads return the cached result. Extracting expensive template expressions into `computed` is one of the most reliable wins in a signal-driven codebase.

The anti-pattern: an expensive method called from the template. `<span>{{ formatComplex(x) }}</span>` runs `formatComplex` on every change detection. Extract it: `readonly formatted = computed(() => formatComplex(x()))` and read `formatted()`.

## OnPush + signals in Compass

Turn on `OnPush` across Compass:

```ts
// Every component:
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  // ...
})
```

Because Compass reads state via signals, this changes nothing observable — but it lays the groundwork for zoneless. Angular's own scaffolding (via `ng generate component --change-detection=OnPush`) sets this for you if you configure it as the CLI default.

Add `@defer` to the stats page's chart section. Add `NgOptimizedImage` to any image you add. Add `computed` for any expensive derivation. That is 95% of the Angular-specific performance wisdom.

## Not-Angular-specific things that matter

Framework performance can only help so much if the surroundings are broken. Two non-Angular checklists:

- **HTTP is slow.** Cache responses on the server, use CDN, use Brotli compression, use HTTP/2 or HTTP/3, use service workers if offline matters. Chapter 18's SSR helps time-to-first-paint; Chapter 19's deployment picks affect all of the above.
- **Fonts are heavy.** Every custom font is a network request that blocks text rendering. Subset your fonts. Use `font-display: swap`. Consider system fonts if you can.

If your Lighthouse audit is bad and you cannot find the Angular problem, look outside Angular.

## What comes next

Part V begins with testing. Chapter 17 introduces `TestBed`, component harnesses, and Playwright for end-to-end tests. By the end of Part V, Compass has a test suite and a deployment plan, and Chapter 20 sends you off to the wider Angular world.

### Exercises

1. Turn on `OnPush` on every component in Compass. Run the app; verify everything still works. Then break something on purpose (call `this._tasks().push(...)` in `TaskStore` — mutating instead of updating). What happens under `OnPush`? What is the fix? Write down the rule.

2. Wrap the (yet-to-be-built) `StatsChart` component in an `@defer` block on the stats page. Trigger on viewport with a placeholder that reads "Loading chart…" Verify in the network tab that the chart's chunk downloads only when you scroll.

3. Run `source-map-explorer` against Compass's production build. What are the three largest things in your bundle? For each, decide whether it can be lazy-loaded, deferred, or tree-shaken.
