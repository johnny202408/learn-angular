# Chapter 6. Data binding and the new control flow

Templates are how Angular describes a user interface. They are HTML plus a small set of extensions: interpolations to show data, bindings to connect data to attributes and events, and block syntax to render lists and conditionals. This chapter covers every extension you will use daily. By the end, Compass will let you click a task to toggle it between done and not done.

Keep the state of Compass from Chapter 5. We will add to `task-list.ts` and `task-list.html` throughout.

## Interpolation: getting values onto the page

You met `{{ }}` in Chapter 5. It evaluates a TypeScript expression against the component's fields and inserts the result as text.

```html
<h1>{{ heading }}</h1>
<p>You have {{ tasks.length }} tasks.</p>
<p>Active: {{ tasks.filter(t => !t.done).length }}</p>
```

Anything you put between the double braces is an expression, not a statement. That means:

- You can call methods and use operators: `{{ user.firstName + ' ' + user.lastName }}`.
- You cannot assign, throw, or use `new`. `{{ x = 5 }}` will not compile as a template expression.
- The expression must be *side-effect-free*, or Angular will call it many times per second and the app will misbehave.

Interpolation always produces text. To bind to *attributes* or *properties* of an element, you use one of the binding forms below.

## Property binding: `[prop]="expression"`

Property binding sets an HTML element's *property* (not its attribute — those are different, more on that shortly) to the value of an expression.

```html
<img [src]="user.avatarUrl" [alt]="user.name" />
<input [value]="task.title" [disabled]="task.done" />
<a [href]="'/tasks/' + task.id">Details</a>
```

The square brackets on the left name the property. The double quotes on the right hold a TypeScript expression evaluated in the component's context.

### Property vs attribute

HTML has both attributes (what you write in the source) and properties (what the DOM object actually holds). For most elements they are aligned, but not always. `<input value="hello">` sets the *initial* attribute; the running DOM element has a `.value` property that changes as the user types. Property binding writes to the property.

In the rare case you actually need to set an attribute (usually for ARIA), Angular has a special syntax:

```html
<button [attr.aria-label]="'Delete task ' + task.title">×</button>
```

`[attr.name]` sets the HTML attribute named `name`. If Angular ever gives you a "no such property" error on an element, this is often the fix.

### Class and style shortcuts

Two special forms of property binding are so common they get short syntax:

```html
<li [class.done]="task.done" [class.overdue]="isOverdue(task)">
<p [style.color]="task.done ? '#999' : 'inherit'">{{ task.title }}</p>
```

`[class.name]` toggles the class based on the truthiness of the expression. `[style.property]` sets the inline style property. Both forms accept multiple entries — you can have `[class.done]` and `[class.overdue]` on the same element.

For more elaborate class or style logic, bind an object or array:

```html
<li [class]="{ done: task.done, overdue: isOverdue(task) }">
<li [class]="cssClasses()">
```

## Event binding: `(event)="handler(...)"`

Event bindings run a component method when a DOM event fires.

```html
<button (click)="markDone(task)">Done</button>
<input (input)="onSearch($event)" />
<form (submit)="save()">…</form>
```

The parentheses on the left name the event (any DOM event: `click`, `input`, `focus`, `keydown`, whatever). The right side is a *statement* — this is the one place in a template where you can call a method for its side effect. `$event` inside the statement refers to the event object (the same object you would receive in a plain JavaScript listener).

Let's use it in Compass. Open `task-list.ts` and add a method:

```ts
export class TaskList {
  tasks: Task[] = [ /* ... */ ];

  toggle(task: Task): void {
    task.done = !task.done;
  }
}
```

And in `task-list.html`, wire up the click:

```html
<li class="task" [class.done]="task.done" (click)="toggle(task)">
  <span class="title">{{ task.title }}</span>
  @if (task.dueDate) {
    <span class="due">due {{ task.dueDate | date: 'shortDate' }}</span>
  }
</li>
```

Save. In the browser, click any task. It should toggle between done and not done, with the strikethrough appearing and disappearing.

Two things worth noting:

- The click handler mutates `task.done` in place. This works, but it works *only* because Angular's zone-based change detection re-checks templates after any DOM event. This is fragile: signals (Chapter 7) will make the same code more explicit and better-behaved.
- The whole `<li>` is now clickable. That is fine for now but bad accessibility practice — a proper implementation would use a `<button>` or add keyboard handling. We will fix that when we come back to accessibility.

## Two-way binding: `[(model)]="value"`

Two-way binding is Angular's syntax for the common pattern of "bind a property in *and* listen for changes going out." The canonical use is form inputs:

```html
<input [(ngModel)]="task.title" />
```

`ngModel` is a directive from `@angular/forms` — using it requires adding `FormsModule` to the component's `imports:` array. If you paste this into a standalone component without that import, the template compiler will complain with "Can't bind to 'ngModel'."

Reading right to left, the parentheses inside the brackets are the "banana in a box" mnemonic. The syntax expands to a property binding on `ngModel` and an event binding on `ngModelChange`:

```html
<!-- Equivalent to the above -->
<input [ngModel]="task.title" (ngModelChange)="task.title = $event" />
```

`ngModel` is one specific implementation of the two-way pattern. Signals-based two-way binding, which we will use in Compass, uses a *model input* — a concept we will meet in Chapter 8. For now, know only that `[(x)]` is Angular's syntax for two-way binding, and that its semantics are always "property in, event out." There is no magic — it is not a data binding library — just a syntactic bundle.

## The new control flow

Templates need to make decisions ("show this if the user is logged in") and repeat ("render one row per task"). Angular's modern syntax for these is called *the new control flow*: `@if`, `@for` (with its `@empty` sub-block), `@switch`, and the local-variable form `@let`. They replace an older set of *structural directives* — `*ngIf`, `*ngFor`, `*ngSwitchCase` — that you will still see in existing codebases. Both work; the new syntax became stable in Angular 17 (late 2023) and is the recommended default in every project since.

### `@if` and `@else`

```html
@if (user.loggedIn) {
  <p>Welcome back, {{ user.name }}.</p>
} @else if (user.pending) {
  <p>Confirming your email…</p>
} @else {
  <a routerLink="/login">Sign in</a>
}
```

Braces are required around the branches. You can nest freely. There is no ambiguity about where a branch ends.

### `@for` and `track`

```html
@for (task of tasks; track task.id) {
  <li>{{ task.title }}</li>
}
```

The `track` clause is required. It tells Angular how to identify each item across renders. When the array changes — you add a task, remove one, reorder — Angular uses `track` to decide which existing DOM nodes correspond to which items in the new array. Correct tracking means Angular reuses DOM nodes (fast); wrong tracking means Angular re-creates every node every time (slow).

Track by a stable identifier — a database id, a unique string — whenever you have one. Track by index (`track $index`) only as a last resort, and only when items are truly interchangeable.

The `@for` block has other useful contextual variables:

```html
@for (task of tasks; track task.id; let i = $index; let first = $first; let last = $last) {
  <li>
    #{{ i + 1 }}: {{ task.title }}
    @if (first) { <span>(first)</span> }
    @if (last) { <span>(last)</span> }
  </li>
}
```

Available: `$index`, `$first`, `$last`, `$even`, `$odd`, `$count`.

And, importantly, an `@empty` block:

```html
@for (task of tasks; track task.id) {
  <li>{{ task.title }}</li>
} @empty {
  <li>Nothing to do.</li>
}
```

`@empty` renders when the array is empty. This replaces an idiom you would have written with a separate `@if (tasks.length === 0)` — cleaner, and lets Angular optimize the empty case.

### `@switch`, `@case`, `@default`

For multi-branch dispatch on a single value:

```html
@switch (badgeFor(task)) {
  @case ('overdue') { <span class="badge overdue">Overdue</span> }
  @case ('due-today') { <span class="badge today">Today</span> }
  @case ('later') { <span class="badge later">Later</span> }
  @default { <span class="badge">—</span> }
}
```

(The `badgeFor(task)` method returns one of those literal strings based on the task's `dueDate` and `done` fields. Compass's `Task` interface has `done` and `dueDate`, not a `status` field.)

You can nest `@switch` inside `@for`, `@if` inside `@switch`, and so on. There are no restrictions.

### `@let`

`@let` binds a local variable inside a template so you can reuse a computation:

```html
@let activeCount = tasks.filter(t => !t.done).length;
@let hasActive = activeCount > 0;

@if (hasActive) {
  <p>{{ activeCount }} tasks remaining.</p>
} @else {
  <p>All done for today.</p>
}
```

Two things to know: `@let` bindings are scoped to their surrounding block; and the expression is re-evaluated on every change-detection cycle (like any template binding), so the binding stays fresh whenever any of its inputs change.

## Pipes: transform in-place

You have already used a pipe: `{{ task.dueDate | date: 'shortDate' }}`. A *pipe* is a function you can apply inside a template expression, using `|`. Its job is one-way, side-effect-free formatting.

Built-in pipes worth knowing:

```html
{{ task.title | uppercase }}
{{ task.title | lowercase }}
{{ task.title | titlecase }}
{{ task.createdAt | date: 'medium' }}
{{ percentage | percent: '1.0-2' }}
{{ price | currency: 'USD' }}
{{ someObject | json }}       <!-- great for debugging -->
{{ items | slice: 0 : 5 }}
```

Pipes can chain:

```html
{{ task.title | slice: 0 : 40 | titlecase }}
```

You will write your own pipes in Chapter 15. Until then, the built-ins cover most needs.

## Attribute bindings you will need

Beyond `class` and `style`, a few attribute bindings come up often:

```html
<button [disabled]="loading">Save</button>
<input [placeholder]="hint" [autofocus]="isNew" />
<a [href]="url" [target]="external ? '_blank' : '_self'">Link</a>
<img [src]="avatarUrl" [width]="size" [height]="size" [alt]="user.name" />
```

Most HTML attributes have a corresponding property, and Angular is smart enough to bind to the property. When it isn't (the aria-* case above), use `[attr.name]`.

## Bringing it together: an "Add task" input

Let's add a small form that appends a task to the list. Edit `task-list.ts`:

```ts
import { Component } from '@angular/core';
import { Task } from '../task';

@Component({
  selector: 'app-task-list',
  imports: [],
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
})
export class TaskList {
  tasks: Task[] = [ /* ... existing three tasks ... */ ];

  draft = '';

  toggle(task: Task): void {
    task.done = !task.done;
  }

  add(): void {
    const title = this.draft.trim();
    if (title === '') return;
    this.tasks = [
      ...this.tasks,
      {
        id: crypto.randomUUID(),
        title,
        done: false,
        createdAt: new Date().toISOString(),
        dueDate: null,
        tags: [],
      },
    ];
    this.draft = '';
  }
}
```

Two details worth naming:

- `this.tasks = [...this.tasks, newTask]` creates a *new array* rather than mutating the old one. In signal-based Angular (Chapter 7), this pattern is required; here it is optional but a good habit to build.
- `crypto.randomUUID()` is a browser built-in that produces a fresh id. In real apps the id often comes from the server; for now this suffices.

And in `task-list.html`, add a form at the top:

```html
<h1>Tasks</h1>

<form (submit)="add(); $event.preventDefault()">
  <input
    type="text"
    placeholder="What needs doing?"
    [value]="draft"
    (input)="draft = $any($event.target).value" />
  <button type="submit" [disabled]="draft.trim() === ''">Add</button>
</form>

<ul class="task-list">
  @for (task of tasks; track task.id) {
    <li class="task" [class.done]="task.done" (click)="toggle(task)">
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

Save. Type a task name. Press Add or hit Enter. It appears at the end of the list, cleared from the input, and the button re-disables until you type again.

Two things to notice about the form:

- `(submit)="add(); $event.preventDefault()"` handles form submission and stops the browser from reloading the page. `$event.preventDefault()` is the same call you would write in vanilla JavaScript.
- `(input)="draft = $any($event.target).value"` is *manual* two-way binding. It reads the input's `value` on every keystroke and copies it into `draft`. In Chapter 12 we will replace this with proper reactive forms, and in Chapter 8 you will meet `model()` — an even better version. For now, we do it by hand.

The `$any(...)` is a workaround: `$event.target` has type `EventTarget | null`, which does not know about a `.value` property. `$any` tells the template checker "trust me, don't fuss." In a component method with a properly typed handler, we would use an actual TypeScript cast; in a template expression, `$any` is the escape hatch.

## What you should not do in templates

Templates should be declarative descriptions of what to render given some data. There are a handful of things that *work* in templates but that you should not do:

- **Long expressions.** Anything more complex than a small ternary or method call belongs in the component class. Templates full of `?:` chains and nested method calls become read-only artifacts.
- **Method calls that do real work.** Every binding is evaluated many times as the app runs. If a template says `{{ expensiveComputation(item) }}`, that call happens on every change detection. Use a computed signal (Chapter 7) or move the work into the class.
- **Mutations.** No template expression should modify state. Event *statements* (`(click)="..."`) can, but interpolations and property bindings must be pure reads.

Following these rules makes templates fast, predictable, and debuggable. Break them, and you will spend afternoons wondering why something re-renders forty times per second.

## What comes next

Chapter 7 introduces signals — Angular's modern reactive state primitive. We will rewrite Compass's `tasks` field as a signal, and the app will behave the same but for entirely different reasons. Under the covers we will move from "Angular checks everything after every event" to "Angular updates exactly the parts of the screen whose signals changed."

### Exercises

1. Add a "Clear completed" button above the list that removes every done task. Wire it up with an event binding; do not mutate the array, produce a new one with `filter`. The button should be disabled when there is nothing to clear.

2. Show a count under the list: "3 tasks, 1 done, 2 remaining." Use `@let` to compute the counts once, and interpolation to display them.

3. The clickable `<li>` is bad accessibility. Move the click handler onto an inner `<button>` element, and use CSS to make the button visually match the row. Bonus: add a `(keydown.enter)` binding to the button so pressing Enter also toggles.
