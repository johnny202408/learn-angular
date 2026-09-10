# Chapter 7. Signals: reactive state that feels normal

The Compass code you have now works. Click a task, it toggles; add a task, it appears; clear the input, the button re-disables. It works because Angular runs *change detection* — a check of every binding in every visible component — after every DOM event. In small apps this is fine. In large apps it becomes a bottleneck, and it makes it hard to reason about *why* something re-rendered.

Signals are Angular's answer to both problems. A signal is a piece of reactive state that knows exactly who is looking at it. When a signal changes, only the parts of the screen that read that signal are marked to re-render — nothing else. Once your components read signals rather than plain fields, Angular can update the screen precisely rather than sweepingly. The mental model is *values that push*.

This chapter introduces signals, rewrites Compass's Chapter 6 code to use them, and covers when to reach for computed and effect. By the end you will have a mental model for reactive state that will guide every remaining chapter.

## The problem signals solve

Imagine a Compass screen with a hundred tasks and three components on the page: the task list, a "remaining count" chip in the header, and a progress bar at the bottom. All three depend on the same data.

In the pre-signal model, the flow is: you click a task, its `done` flag flips, and Angular re-checks every binding on the page — a hundred `[class.done]`s, the header's `{{ remaining }}`, the progress bar's `[style.width]`, and everything else. Angular is fast enough that this is usually invisible, but the mechanism is: *when in doubt, re-check everything*.

With signals, the flow is: you click a task; the task's `done` signal changes; Angular knows exactly which template bindings read that signal (one `[class.done]`, one item in the `remaining` computation, one item in the `progress` computation) and updates just those. Twenty updates instead of ten thousand.

The performance win is real but not the reason to reach for signals. The reason is that *your code* becomes precise. "Where does this value come from?" always has an answer — a chain of signals and computations you can trace. "Why did this re-render?" always has an answer — a signal it reads changed.

## Creating a signal

The simplest signal wraps a single value:

```ts
import { signal } from '@angular/core';

const count = signal(0);
```

To *read* the signal, call it as a function:

```ts
console.log(count());   // 0
```

That is deliberate. Signals are functions, and reading is an act. Every read is tracked — Angular records who read the signal so it can notify them later.

To *write*, use `set` or `update`:

```ts
count.set(10);
count.update(n => n + 1);
```

`set` replaces the value; `update` computes the next value from the current one. For most state, both are interchangeable. `update` is useful when the new value depends on the old — a counter, a toggle, an array append.

That's it. Read with `()`, write with `set` or `update`, and Angular does the rest.

## Reading in templates

The same rule applies in templates: to read a signal, call it as a function.

```html
<p>Count: {{ count() }}</p>
```

The parentheses are not optional. `{{ count }}` prints the function object itself (something like `[object Function]`). The compiler will not catch this — it looks like valid TypeScript — so getting the parentheses wrong is a common early mistake. If your interpolation prints `function(){...}` in the browser, you forgot the `()`.

## Signals of arrays and objects

A signal can hold any value, including arrays and objects. But signals track *references*, not deep state. If you mutate an array in place, the signal has no idea anything changed and will not notify its readers.

```ts
const tasks = signal<Task[]>([]);

// Wrong: mutates in place, no notification
tasks().push(newTask);

// Right: produce a new array
tasks.update(current => [...current, newTask]);
```

This is the same "produce a new object" pattern we met in Chapter 3, now with a name. Immutable updates are how signals work. It sounds inconvenient the first time; it becomes second nature quickly, and it makes state changes visible and testable.

## `computed`: derived values

A computed signal is a signal whose value is derived from other signals. It re-computes when its inputs change, and caches its result until they do.

```ts
import { computed } from '@angular/core';

const tasks = signal<Task[]>([]);
const remaining = computed(() => tasks().filter(t => !t.done).length);
const done = computed(() => tasks().length - remaining());
```

You read a computed the same way you read any signal: `remaining()`. You never write to a computed — its value is a function of its inputs and cannot be set directly.

Two things make `computed` powerful:

- **Automatic dependency tracking.** The framework watches which signals your function reads. If those signals change, the computed re-runs. If they do not, it doesn't. You never register dependencies by hand.
- **Lazy evaluation and caching.** A computed does not run until something reads it. Once it has run, its result is cached; subsequent reads return the cache. The cache is invalidated when any dependency changes. If your `progress` computed depends on `tasks`, and `tasks` doesn't change, `progress()` costs nothing to call fifty times.

## `effect`: side effects at the edge

Some things need to happen *when signals change*, but do not produce a value. Saving to `localStorage`, updating the page title, logging analytics, calling a non-Angular library — these are *effects*.

```ts
import { effect } from '@angular/core';

class TaskList {
  tasks = signal<Task[]>([]);

  constructor() {
    effect(() => {
      const current = this.tasks();
      localStorage.setItem('compass:tasks', JSON.stringify(current));
    });
  }
}
```

The effect function runs once immediately (to establish dependencies) and again every time any signal it reads changes. Here it saves the current task list to `localStorage` on every change.

Rules of the road for effects:

- **Register effects in a DI context.** In a component, that means the constructor or a class field initializer. Outside those, use `runInInjectionContext`.
- **Be careful writing to signals from inside an effect.** Writing to a signal that the same effect *reads* creates a cycle: the write re-triggers the effect, which writes again. Angular will throw or warn on obvious cycles. Writing to *unrelated* signals is allowed and sometimes necessary, but reach for it sparingly — most of the time, a `computed` is what you actually want.
- **Reach for `computed` first.** If you find yourself writing an effect that reads signals and computes a value, that is a computed. Effects are for outputs to the outside world.

Effects are the closest thing signals have to a footgun. Used well, they replace lifecycle hooks and observable subscriptions. Used badly, they create spooky action at a distance. Chapter 14 revisits them when we build a signal-based state layer.

## Rewriting Compass with signals

Time to convert `TaskList` from Chapter 6. Open `src/app/task-list/task-list.ts` and change it to:

```ts
import { Component, signal, computed } from '@angular/core';
import { Task } from '../task';

@Component({
  selector: 'app-task-list',
  imports: [],
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
})
export class TaskList {
  tasks = signal<Task[]>([
    { id: 't1', title: 'Buy milk', done: false, createdAt: '2026-01-15T09:00:00Z', dueDate: null, tags: ['home'] },
    { id: 't2', title: 'Write chapter 7', done: true, createdAt: '2026-01-14T18:30:00Z', dueDate: '2026-01-16T00:00:00Z', tags: ['work'] },
    { id: 't3', title: 'Call the plumber', done: false, createdAt: '2026-01-15T11:00:00Z', dueDate: '2026-01-18T00:00:00Z', tags: ['home', 'urgent'] },
  ]);

  draft = signal('');

  remaining = computed(() =>
    this.tasks().filter(t => !t.done).length
  );

  toggle(taskId: string): void {
    this.tasks.update(current =>
      current.map(t =>
        t.id === taskId ? { ...t, done: !t.done } : t
      )
    );
  }

  add(): void {
    const title = this.draft().trim();
    if (title === '') return;
    this.tasks.update(current => [
      ...current,
      {
        id: crypto.randomUUID(),
        title,
        done: false,
        createdAt: new Date().toISOString(),
        dueDate: null,
        tags: [],
      },
    ]);
    this.draft.set('');
  }

  onInput(event: Event): void {
    this.draft.set((event.target as HTMLInputElement).value);
  }
}
```

And `task-list.html`:

```html
<h1>Tasks — {{ remaining() }} left</h1>

<form (submit)="add(); $event.preventDefault()">
  <input
    type="text"
    placeholder="What needs doing?"
    [value]="draft()"
    (input)="onInput($event)" />
  <button type="submit" [disabled]="draft().trim() === ''">Add</button>
</form>

<ul class="task-list">
  @for (task of tasks(); track task.id) {
    <li class="task" [class.done]="task.done" (click)="toggle(task.id)">
      <span class="title">{{ task.title }}</span>
      @if (task.dueDate) {
        <span class="due">due {{ task.dueDate | date: 'shortDate' }}</span>
      }
    </li>
  } @empty {
    <li class="empty">Nothing to do. Nice.</li>
  }
</ul>
```

Save, refresh. Compass looks and behaves the same as before. Every important line of code, though, is different:

- `tasks` and `draft` are signals, read with `()`.
- `toggle` and `add` use `update` to produce a new array; nothing mutates in place.
- `remaining` is computed once, and re-computed only when `tasks` changes.
- The template calls signals: `remaining()`, `draft()`, `tasks()`.

Under the covers, Angular now knows exactly which parts of the template depend on which signals. If we made this component `changeDetection: ChangeDetectionStrategy.OnPush` — which Chapter 16 explains and which we will apply globally — Angular would refuse to re-check anything that could not possibly have changed. That is the performance model of a signal-driven app.

## Signal inputs

Component *inputs* — values passed from a parent — have historically been declared with the `@Input()` decorator:

```ts
export class TaskRow {
  @Input() task!: Task;
}
```

Modern Angular offers a signal-based alternative: `input()` (and `input.required()`), which produces a signal.

```ts
import { Component, input } from '@angular/core';

@Component({ /* ... */ })
export class TaskRow {
  task = input.required<Task>();

  // In methods and computed, read it like any other signal:
  isOverdue = computed(() => {
    const t = this.task();
    return t.dueDate !== null && !t.done && new Date(t.dueDate) < new Date();
  });
}
```

Two shapes are useful:

- **`input<Type>()`** — optional; the default is `undefined`, and the signal returns `Type | undefined` unless you supply a default: `input<number>(0)`.
- **`input.required<Type>()`** — required; the compiler enforces that every parent supplies a value.

Signal inputs are the modern default. They compose naturally with `computed` (as above) and with `effect`. When Chapter 8 refactors Compass into a tree of components, we will use `input()` throughout.

## Model inputs: two-way binding, properly

`ngModel` is one way to get two-way binding on native inputs; another is `[(value)]` on your own components, powered by *model inputs*.

```ts
import { Component, model } from '@angular/core';

@Component({
  selector: 'app-quantity-picker',
  template: `
    <button (click)="value.set(value() - 1)">−</button>
    <span>{{ value() }}</span>
    <button (click)="value.set(value() + 1)">+</button>
  `,
})
export class QuantityPicker {
  value = model.required<number>();
}
```

A parent uses it with the `[(name)]` syntax:

```html
<app-quantity-picker [(value)]="count" />
```

`model` gives you a writable signal that automatically propagates changes to the parent via a matched output. It is the modern replacement for the "input + output" pair that older Angular code used. Chapter 8 revisits model inputs alongside plain inputs.

## When to use signals — and when not

The rule of thumb: **signals for state that lives inside your app**; **RxJS for streams from the outside world**.

- **Use signals for:** UI state (open/closed, selected id, form draft), derived state (filtered list, computed counts), reactive computations, and cross-cutting state you would previously have kept in a service (Chapter 14 covers signal stores).
- **Use RxJS for:** HTTP responses (which are naturally observables), DOM event streams that need debounce or `switchMap`, WebSocket connections, long-running data streams.
- **Use plain fields for:** values that never change over the life of a component, or that don't affect the template. If nothing reads it reactively, it does not need to be a signal.

Reaching for signals everywhere is a beginner mistake. Reaching for RxJS everywhere is an early-career-Angular mistake. Both cost simplicity. Chapter 11 covers the interop between them (there is a `toSignal` and a `toObservable`, and both are two lines of code).

## Change detection in a signal world

Change detection in Angular used to be *zone-based*: a library called Zone.js patched every async API in the browser (timers, Promises, XHR, event listeners) so that Angular could learn when any of them fired and re-check the app. It works, but it is a broad brush and it costs measurable CPU on every event.

Modern Angular is moving toward *zoneless* apps. In a zoneless app, Angular only re-checks when a signal changes. There is no ambient re-check on every setTimeout; there is no monkey-patched Promise. Bindings that read signals are precise; nothing else runs.

The default `ng new` still enables Zone.js for backward compatibility, but the trajectory is clear. Every design decision in this book — signals for state, `input()` over `@Input()`, `model()` for two-way — is on the zoneless path. If you follow this book's patterns, migrating to zoneless later will be a configuration change, not a rewrite.

## What comes next

Chapter 8 breaks Compass's monolithic `TaskList` into a tree of components: a list, individual rows, and an add-task form. You will meet component composition properly — `input()`, `output()`, and content projection — and by the end you will have a Compass that is structured like a real Angular app, not a proof of concept.

### Exercises

1. Add a computed signal `overdueCount` that counts tasks whose `dueDate` is in the past and are not `done`. Display it under the heading: "3 overdue." Only show the line when there is at least one overdue task.

2. Add an `effect` that logs to the console every time the tasks list changes, in the format `"tasks: 5 (2 done)"`. Then click around and read the console. When does the effect fire? Does it fire when you type in the input? Why or why not?

3. Add a "clear completed" button. It should be disabled when nothing is completed. Wire it up to update the `tasks` signal by filtering out done tasks. Use `update`, not `set`; do not mutate the array.
