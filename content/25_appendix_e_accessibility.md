# Appendix E. Accessibility

The book teaches you to build a working Angular application. This appendix teaches you to build one that everyone can use. Accessibility (often shortened to *a11y* — "a" plus eleven letters plus "y") is not an add-on feature you sprinkle in at the end. It is a set of considerations that touch every part of the app you have already built.

If you skipped this in the main text and are reading it now that Compass is deployed, that's fine. If you can retrofit the ideas here in a few hours, retrofit them.

## Why a11y matters in an Angular app

Roughly one in five people uses the web with some kind of assistive technology, at least occasionally. Screen readers, magnifiers, keyboard-only navigation, voice control, high-contrast themes, reduced motion — the list is long. An inaccessible app doesn't just fail users with permanent disabilities; it fails anyone temporarily using their phone with one hand, anyone with a mouse battery about to die, anyone whose vision is tired at the end of a workday.

Single-page apps are particularly prone to a11y regressions because they replace some of the browser's default behaviors — page navigation, form submission, focus management — with code that has to explicitly re-implement them. When you route between screens with Angular's `Router`, the browser doesn't know a "navigation" happened; a screen reader user hears nothing. When your form submits without a full page reload, the browser doesn't announce success or failure; the assistive-technology user is left guessing. This appendix names those gaps and shows how to close them in Angular.

## Semantic HTML first

The most valuable a11y move in any Angular app is to use the right HTML element for the job. `<button>` for something clickable, `<a>` for something that navigates, `<input>` for user input, `<h1>`–`<h6>` for headings in order, `<nav>` for navigation regions, `<main>` for the primary content area.

Chapter 6 pointed at a specific bug in Compass: the task row was wrapped in a `<li>` with a `click` handler, not a `<button>`. That's the paradigm error. A screen reader announces `<li>` as "list item" — it does not communicate that this element is interactive. A keyboard user cannot focus it or activate it with Enter or Space. Fixing this is one line: replace the outer wrapper with a `<button>` styled to look like a row.

```html
<!-- Wrong -->
<li (click)="toggle(task.id)">
  <span>{{ task().title }}</span>
</li>

<!-- Right -->
<li>
  <button type="button" class="task-toggle" (click)="toggle(task.id)">
    <span>{{ task().title }}</span>
  </button>
</li>
```

The visual look can stay identical — that's what CSS is for. What changes is that screen readers now announce "button, Buy milk," keyboard users can Tab to it and press Enter, and browser default focus indicators appear when it's focused.

Similar substitutions across Compass:

- The nav links in `App`'s template are already `<a routerLink>` — correct.
- Any icon-only button needs a text label for screen readers: `<button aria-label="Delete task">×</button>`.
- Form labels: `<label>Title <input formControlName="title" /></label>` — associate every input with a label.

## The Angular CDK's a11y module

`@angular/cdk/a11y` provides three utilities that solve common SPA a11y problems:

**`LiveAnnouncer`** injects an off-screen ARIA live region and lets you programmatically announce messages to screen readers. Use it when the UI changes in a way that a visible user would notice but an assistive-technology user would miss — a toast notification, a "task added" confirmation, a route change.

```ts
import { LiveAnnouncer } from '@angular/cdk/a11y';

@Injectable({ providedIn: 'root' })
export class Announcer {
  private live = inject(LiveAnnouncer);
  taskAdded(title: string) {
    this.live.announce(`Task added: ${title}`, 'polite');
  }
}
```

`'polite'` means "wait for the current announcement to finish"; `'assertive'` interrupts. Prefer polite; save assertive for errors.

**`FocusTrap`** keeps keyboard focus within a container. The canonical use is a modal dialog: when the modal is open, Tab should cycle within the modal's focusable elements, not escape to the underlying page.

```ts
import { ConfigurableFocusTrapFactory } from '@angular/cdk/a11y';

private trapFactory = inject(ConfigurableFocusTrapFactory);
private trap = this.trapFactory.create(this.el.nativeElement);
// on open:
this.trap.focusInitialElement();
// on close:
this.trap.destroy();
```

**`FocusMonitor`** distinguishes between keyboard focus and mouse focus. Users who navigated with the keyboard should see a visible focus ring; users who clicked should not (their intent is clear from the click). Angular Material uses this to render focus rings only when appropriate.

## ARIA in templates

ARIA attributes give assistive technologies extra semantic information when native HTML falls short. Angular binds them with `[attr.aria-*]`:

```html
<!-- A tab list -->
<div role="tablist">
  <button role="tab"
          [attr.aria-selected]="isActive('today')"
          [attr.aria-controls]="'today-panel'"
          (click)="select('today')">
    Today
  </button>
</div>

<!-- A disabled-looking button that isn't a real <button> -->
<div role="button"
     tabindex="0"
     [attr.aria-disabled]="loading()"
     (click)="save()"
     (keydown.enter)="save()">
  Save
</div>

<!-- A loading state -->
<div [attr.aria-busy]="loading()">
  <!-- ... -->
</div>

<!-- An expandable region -->
<button [attr.aria-expanded]="open()" (click)="open.set(!open())">
  Details
</button>
@if (open()) {
  <div>Details content here.</div>
}
```

Rules of the road:

- **Native HTML beats ARIA every time.** If a `<button>` will do the job, don't use `role="button"` on a `<div>`. ARIA is the escape hatch, not the first tool.
- **If you use `role`, take responsibility for keyboard behavior.** A `role="button"` `<div>` needs `tabindex="0"` and `(keydown.enter)` / `(keydown.space)` handlers to behave like a real button.
- **`aria-hidden="true"` removes an element from the assistive-technology tree.** Useful for purely decorative icons, dangerous if applied to real content.

## Keyboard navigation

Every interactive element in Compass should be reachable and operable with the keyboard alone. The rules:

1. **Tab order follows visual order.** If the eye reads left-to-right top-to-bottom, so does the Tab key. Don't override with `tabindex="1"`, `"2"`, ... — that inverts control from users to you, and gets it wrong.
2. **Every focusable element has a visible focus indicator.** Browser defaults are ugly but functional. If you override them (`outline: none`), replace them (`:focus-visible { outline: 2px solid ... }`) or your app becomes unusable for keyboard users.
3. **Custom widgets follow the [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/) keyboard patterns.** A tab list has specific expectations (arrow keys navigate, Home/End jump); a menu has others. Match the pattern for the widget you're building.

In Compass, this means:

- Tabbing across the header lands on "Today," then "Stats."
- Tab into the task list lands on the first task's toggle button.
- Pressing Enter on a task toggles it; Space also toggles.
- Tab into the "Add task" form lands on the input; Tab again lands on the Add button.
- On the task detail page, Tab cycles through Title, Due date, each tag, Add tag, Save, Cancel.

## Reactive forms and a11y

Chapter 12 built reactive forms; here is what to add.

**Associate labels explicitly.** `<label>` wrapping the input, or `<label for="id">` with `id` on the input. Never rely on placeholder text as a label — it disappears when the user types.

**Mark required fields.** `[required]="true"` on the control, plus visual indication (a `*` next to the label is conventional).

**Announce errors with `aria-live`.** When validation errors appear, screen reader users need to hear them.

```html
<label for="title">
  Title
  <span aria-hidden="true">*</span>
</label>
<input id="title" formControlName="title"
       [attr.aria-invalid]="form.controls.title.invalid && form.controls.title.touched"
       [attr.aria-describedby]="errorId" />
<div [id]="errorId" role="alert" aria-live="polite">
  @if (form.controls.title.touched && form.controls.title.invalid) {
    <span>Title is required.</span>
  }
</div>
```

`aria-invalid` tells screen readers this field is in error. `aria-describedby` links the error message to the field so screen readers read the error when the field is focused. `role="alert"` + `aria-live="polite"` makes the error announce itself as it appears.

**On submit failure, focus the first invalid control.** Users don't scroll back up looking for red squiggles; they wait for feedback. `viewChild()` + `elementRef.nativeElement.focus()` handles this.

## Route changes need announcement

When Compass navigates from `/` to `/stats`, the URL changes but nothing else about the page announces the change. Screen reader users may not realize they've moved.

The fix is a small service subscribed to the router:

```ts
@Injectable({ providedIn: 'root' })
export class RouteAnnouncer {
  private router = inject(Router);
  private live = inject(LiveAnnouncer);

  constructor() {
    this.router.events
      .pipe(filter(e => e instanceof NavigationEnd), takeUntilDestroyed())
      .subscribe(() => {
        const title = document.title;
        this.live.announce(`Navigated to ${title}`, 'polite');
      });
  }
}
```

Inject `RouteAnnouncer` once in `App`'s constructor. Screen reader users now hear the new page title on every navigation.

**Also: focus management on route change.** By default, focus stays wherever it was before navigation — usually a link that no longer exists on the new page. The convention is to focus the new page's `<h1>`. Add `tabindex="-1"` to each page's `<h1>` and focus it after navigation.

## Testing accessibility

Two-and-a-half layers of testing:

**Automated audits** catch about 30% of real a11y bugs but do it cheaply. Add `@axe-core/playwright` to your Playwright suite:

```ts
import AxeBuilder from '@axe-core/playwright';

test('home page has no a11y violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

Run this on every route in Compass. It catches missing labels, contrast issues, invalid ARIA, structural problems.

**Manual keyboard testing** catches most of the rest. Close your mouse in a drawer and use Compass with keyboard alone. Every action should be reachable via Tab; every interactive element should show a focus indicator; every widget should behave as its ARIA role promises.

**Screen reader testing** is the ground truth. On macOS, turn on VoiceOver (Cmd+F5) and try Compass. On Windows, install NVDA (free) and try it. You will hear the app the way an assistive-technology user hears it, which is a different experience from seeing it. Do this once per major feature; it catches things audits and keyboard tests miss.

## SPA-specific a11y traps

A short list of things that specifically bite Angular apps:

- **Toast notifications that appear briefly.** If they vanish before a screen reader can announce them, they don't exist to that user. Give them 5+ seconds and use `aria-live="polite"`.
- **Loading states.** A `<div>Loading…</div>` that appears and disappears is invisible to a screen reader unless you use `aria-live` or `aria-busy`.
- **Modal dialogs that don't trap focus.** Users press Tab and end up on elements behind the modal that they can't see.
- **Optimistic UI that renders before the server confirms.** Screen readers announce the optimistic content; when it reverts, they don't announce the revert unless you tell them to.
- **Deferred content via `@defer`.** When it eventually loads, screen readers may need an announcement. If the deferred region is important, wrap it in `aria-live`.
- **Icon fonts and SVG icons without labels.** `<span class="icon-plus"></span>` announces nothing. Add `aria-label` or hide it with `aria-hidden="true"` and provide text nearby.

## The a11y mindset

Every Angular pattern in this book has an a11y dimension. Signals updating the UI: does the update need to be announced? Routing between pages: does focus land somewhere sensible? Reactive forms: are errors linked to their inputs? Content projection: are the projected children still in the right tab order?

You don't need to solve all of this on day one. You need to know it exists, keep a11y in mind while you build, and re-check the app periodically with a keyboard and a screen reader. That is what turns "I built an Angular app" into "I built an Angular app anyone can use."
