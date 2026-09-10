# Chapter 15. Directives, pipes, and reusable UI

Components are Angular's biggest reuse unit. Pipes and directives are the smaller ones. A *pipe* is a function you can call inside a template expression — small, pure, transformation-shaped. A *directive* is behavior you attach to an existing element without wrapping it in another component. Both let you factor out repetition without introducing new tags or new component boundaries.

This chapter covers building both. We add a `TimeAgo` pipe that renders "2 hours ago" from a timestamp; an `Autofocus` directive that focuses an input on render; a `LongPress` directive that emits an event after a hold; and, briefly, a shared `EmptyState` component that uses content projection. By the end, Compass has a small toolkit of reusable UI primitives that the rest of the book (and any future feature) can reach for.

## Pipes: template-only transformation

Compass currently uses `| date: 'shortDate'` in a few places. That is a built-in pipe. Angular ships several: `date`, `currency`, `percent`, `slice`, `keyvalue`, `json`, `titlecase`, `lowercase`, `uppercase`, `async`. You have used most of them.

Custom pipes are for transformations you find yourself repeating. The rules of a good pipe:

- **Pure.** Given the same inputs, always return the same output. No side effects. No global state.
- **Fast.** Pipes run every change detection. Anything expensive should be memoized or moved to a `computed`.
- **Small.** A pipe with 200 lines is a component or a service in disguise.

### Building `TimeAgo`

Compass shows `createdAt` on hover, and we want the display to be "just now," "5 minutes ago," "2 hours ago," "yesterday," "3 days ago." Perfect pipe material.

Generate it:

```bash
ng generate pipe time-ago
```

`src/app/time-ago.pipe.ts`:

```ts
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'timeAgo' })
export class TimeAgoPipe implements PipeTransform {
  transform(value: string | Date | number | null | undefined): string {
    if (value === null || value === undefined || value === '') return '';
    const date = value instanceof Date ? value : new Date(value);
    if (isNaN(date.getTime())) return '';

    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 45) return 'just now';
    if (seconds < 90) return 'a minute ago';

    const minutes = Math.floor(seconds / 60);
    if (minutes < 45) return `${minutes} minutes ago`;
    if (minutes < 90) return 'an hour ago';

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hours ago`;
    if (hours < 42) return 'yesterday';

    const days = Math.floor(hours / 24);
    if (days < 30) return `${days} days ago`;

    const months = Math.floor(days / 30);
    if (months < 12) return `${months} months ago`;
    return `${Math.floor(months / 12)} years ago`;
  }
}
```

Two rules of the road:

- **Handle bad input gracefully.** `null`, `undefined`, invalid strings — return `''` rather than throwing. Templates should not blow up because a value hasn't loaded yet.
- **Accept a union of reasonable types.** Consumers pass in different shapes; a pipe that only accepts one type causes ceremony at call sites.

Use it in a template:

```html
<span title="{{ task.createdAt | date: 'medium' }}">
  Added {{ task.createdAt | timeAgo }}
</span>
```

Any component that uses the pipe in its template must import it:

```ts
@Component({
  imports: [TimeAgoPipe],
  // ...
})
```

### Pipes with arguments

A pipe can take arguments: `{{ value | myPipe: arg1: arg2 }}`. Arguments become extra parameters to `transform`:

```ts
@Pipe({ name: 'truncate' })
export class TruncatePipe implements PipeTransform {
  transform(value: string, maxLength: number = 100, ellipsis: string = '…'): string {
    if (!value) return '';
    return value.length <= maxLength ? value : value.slice(0, maxLength - ellipsis.length) + ellipsis;
  }
}
```

Use it: `{{ description | truncate: 80 }}`.

### Pipes and change detection

Pipes are called on every change detection cycle by default (they are *pure* pipes, and Angular caches their output). Angular re-invokes a pipe only if any of its arguments has a new reference. That is why we `[...tasks]` before sorting: the new reference triggers re-evaluation.

An *impure* pipe (`@Pipe({ pure: false })`) is called every change detection whether inputs changed or not. Almost always the wrong choice. If you find yourself considering impure, ask why you aren't using a signal.

## Attribute directives: behavior on existing elements

An attribute directive attaches behavior to whatever it's placed on. The classic use case is small pieces of imperative browser API — focus, tooltip, click-outside, resize observer — where wrapping the element in another component would be overkill.

### `Autofocus`

Generate:

```bash
ng generate directive autofocus
```

`src/app/autofocus.directive.ts`:

```ts
import { Directive, ElementRef, inject, afterNextRender } from '@angular/core';

@Directive({
  selector: '[appAutofocus]',
})
export class AutofocusDirective {
  private el = inject<ElementRef<HTMLElement>>(ElementRef);

  constructor() {
    afterNextRender(() => this.el.nativeElement.focus());
  }
}
```

Use it in any template — for instance, on the edit-task input:

```html
<input type="text" formControlName="title" appAutofocus />
```

Whenever the directive is created, the element receives focus after the next render (`afterNextRender` is a modern lifecycle hook that runs once, after DOM has been committed). No components involved. The element stays a native `<input>`.

Notice the selector: `[appAutofocus]`. Directives use attribute selectors, matched anywhere the attribute appears. The `app` prefix keeps them from colliding with existing attributes.

### `LongPress`

A `LongPress` directive that emits an event after the user has been holding the element for a threshold of time.

```ts
import { Directive, ElementRef, inject, output, DestroyRef, input } from '@angular/core';

@Directive({
  selector: '[appLongPress]',
})
export class LongPressDirective {
  threshold = input<number>(500);   // milliseconds
  longPress = output<void>();

  constructor() {
    const el = inject<ElementRef<HTMLElement>>(ElementRef).nativeElement;
    const destroyRef = inject(DestroyRef);

    let timeout: number | undefined;

    const start = () => {
      timeout = window.setTimeout(() => this.longPress.emit(), this.threshold());
    };
    const cancel = () => {
      if (timeout) window.clearTimeout(timeout);
    };

    el.addEventListener('mousedown', start);
    el.addEventListener('touchstart', start);
    el.addEventListener('mouseup', cancel);
    el.addEventListener('mouseleave', cancel);
    el.addEventListener('touchend', cancel);

    destroyRef.onDestroy(() => {
      el.removeEventListener('mousedown', start);
      el.removeEventListener('touchstart', start);
      el.removeEventListener('mouseup', cancel);
      el.removeEventListener('mouseleave', cancel);
      el.removeEventListener('touchend', cancel);
      cancel();
    });
  }
}
```

Use it:

```html
<div appLongPress [threshold]="800" (longPress)="onLongPress()">
  Hold me
</div>
```

Directives can have inputs and outputs just like components. The whole reactive machinery works the same way. What's missing is the template — a directive has no view of its own; it augments a host element.

`DestroyRef` is Angular's DI-based tear-down mechanism. Injecting it and calling `onDestroy` is cleaner than an `ngOnDestroy` method. It also composes with `takeUntilDestroyed` under the hood.

## Structural directives — mostly, don't

Structural directives are the ones prefixed with `*` (`*ngIf`, `*ngFor`, `*ngSwitchCase`). They add or remove elements from the DOM. Since the new control flow (`@if`, `@for`, `@switch`) covers every real case, you almost never write your own structural directive in modern Angular.

The one place they still appear is when you want to add a template-shaped API — take a piece of template content and render it under some condition or with some enrichment. If you find yourself needing this, look up the docs on `TemplateRef` and `ViewContainerRef`. For an application-code book, we can leave it there.

## `HostBinding` and `HostListener`, or their modern equivalents

An older pattern for directive behavior used decorators:

```ts
@HostBinding('class.active') isActive = false;
@HostListener('click') onClick() { this.isActive = !this.isActive; }
```

Modern Angular uses `host` in the metadata block:

```ts
@Directive({
  selector: '[appToggleActive]',
  host: {
    '[class.active]': 'isActive',
    '(click)': 'onClick()',
  },
})
export class ToggleActiveDirective {
  isActive = false;
  onClick() { this.isActive = !this.isActive; }
}
```

The two forms are equivalent; the `host` block is preferred going forward. In tiny directives, the imperative approach we used for `LongPress` (adding event listeners directly on the element in the constructor) is also fine and sometimes clearer.

## Content-projected components: `EmptyState`

Some reusable UI is a component with slots. Compass has several places that need an "empty state" — a friendly message when a list has no items. Rather than repeat the markup, extract a component.

```ts
@Component({
  selector: 'app-empty-state',
  template: `
    <div class="empty-state">
      <div class="icon"><ng-content select="[icon]"></ng-content></div>
      <h3>{{ title() }}</h3>
      <p class="body"><ng-content></ng-content></p>
      <div class="actions"><ng-content select="[actions]"></ng-content></div>
    </div>
  `,
  styles: `
    .empty-state { padding: 40px; text-align: center; color: #666; }
    .icon { font-size: 3rem; margin-bottom: 12px; }
    h3 { margin: 0 0 6px; font-size: 1.2rem; }
    .body { margin: 0 0 16px; }
  `,
})
export class EmptyState {
  title = input.required<string>();
}
```

Usage in `TaskList`:

```html
@if (tasks().length === 0) {
  <app-empty-state title="Nothing to do today.">
    <span icon>🌤</span>
    Enjoy some free time, or add something below.
    <button actions (click)="focusInput()">Add a task</button>
  </app-empty-state>
}
```

Three named slots (`icon`, `default`, `actions`), all optional, filled by the caller. Content projection is what lets a design system's components stay declarative — the caller composes markup, the container styles.

## When to reach for what

A checklist for "component, directive, or pipe."

**Pipe** — you have a value; you want a differently-shaped value in the template. No behavior, no DOM changes, no state.

**Directive** — you want to attach behavior to an element that already has a role. Focus, drag-and-drop, intersection observer, tooltip trigger. Zero or minimal DOM changes.

**Component** — the reusable thing is a piece of markup with its own visual identity, or has state, or needs to project content.

Getting this right saves a lot of code. Wrapping a `<div>` in an `<app-tooltip-host>` component when a `[appTooltip]` directive would do doubles the elements in the DOM. Pipe-ing a computation when a component-owned `computed` would do fragments the logic across the codebase.

## Naming conventions

Convention across kinds of reusable UI:

- **Components** get an `app-` prefix on the tag: `<app-task-row>`, `<app-card>`.
- **Directives** get an `app` prefix on the attribute selector: `[appAutofocus]`, `[appLongPress]`.
- **Pipes** are usually unprefixed (`timeAgo`, `truncate`) because they don't collide with HTML the way tags and attributes do — the framework's built-in pipes are also unprefixed. A prefix is fine if you're publishing a library, but application code rarely needs it.

For application-code components and directives, the prefix keeps things unambiguous. For pipes, keep the name short and specific.

## What comes next

Chapter 16 measures Compass's performance and applies the tools that matter. `OnPush` change detection, `@defer` blocks for parts that don't need to load immediately, image optimization, and bundle analysis. By the end of Chapter 16, Compass will feel snappy on a mid-range phone.

### Exercises

1. Build a `Currency` pipe that formats a `number` as USD to two decimal places with commas ("1,234.56"). Then remove it and use the built-in `currency` pipe. Compare — how many built-in pipes do you not need to write?

2. Build a `ClickOutside` directive that emits when the user clicks outside the element it is attached to. Use it to close a dropdown menu component. Hint: listen on `document.click`; check whether the target is a descendant of `el.nativeElement`.

3. Convert Compass's "task row" from a component into a directive on `<li>` — `<li appTaskRow [task]="task" (toggled)="onToggle($event)">`. What can you keep? What has to move? At the end, decide whether the component or the directive is the better shape and undo whichever loses.
