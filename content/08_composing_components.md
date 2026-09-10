# Chapter 8. Composing components

A real Angular app is not one big component; it is a tree of small ones. Each has a narrow job, and together they compose into a screen. Composition is what makes an app maintainable — you can rename, replace, or reuse any component without touching the rest — and it is what lets a codebase grow past a few thousand lines without becoming a swamp.

In this chapter we split Compass's `TaskList` component into three: a list, individual task rows, and an add-task form. Along the way we cover the tools of composition: `input()` for passing data down, `output()` for sending events up, `model()` for two-way binding, and content projection for slotting arbitrary content inside a container component.

By the end, Compass will look and behave exactly as it does now — but it will be structured like Angular apps that survive contact with real teams.

## What composition looks like

Right now, `TaskList` owns everything: the array of tasks, the draft input state, the add and toggle logic, and the entire template that renders form and rows. That is fine for a hundred lines. It fails at ten thousand.

We are going to break it up:

- **`TaskRow`** — renders one task. It takes a `task` as input and emits an event when the user toggles it.
- **`AddTaskForm`** — renders the input and Add button. It emits an event when the user submits a new title.
- **`TaskList`** — owns the tasks array and coordinates the two. It becomes short and readable.

Here's where Compass will end up, structurally, after this and the next few chapters:

```
App (root)
├── <header> nav bar with links
├── <router-outlet>
│    │
│    ├── Home           ← / route
│    │    └── TaskList
│    │         ├── AddTaskForm         ← draft input, "Add" button
│    │         └── TaskRow × N         ← one per task
│    │
│    ├── Stats          ← /stats route
│    │
│    └── TaskDetail     ← /task/:id route
│         └── EditTask               ← form for title, due date, tags
```

Each box is a component. Solid arrows are *contains* relationships (the parent renders the child in its template). Every component is standalone; every one has its own file. This is the shape of an Angular app.

This "container / presentation" division is the most common way to structure Angular components. The container knows about state and orchestrates the parts; the presentational components know only about what they render and what events they emit. Presentational components tend to be small, pure, easy to test, and easy to reuse.

## Passing data down: `input()`

We met `input()` briefly in Chapter 7. Here we use it in earnest.

Create `TaskRow` with the CLI:

```bash
ng generate component task-row
```

Edit `src/app/task-row/task-row.ts`:

```ts
import { Component, input, output, computed } from '@angular/core';
import { Task } from '../task';

@Component({
  selector: 'app-task-row',
  imports: [],
  templateUrl: './task-row.html',
  styleUrl: './task-row.css',
})
export class TaskRow {
  task = input.required<Task>();
  toggled = output<string>();

  isOverdue = computed(() => {
    const t = this.task();
    return t.dueDate !== null && !t.done && new Date(t.dueDate) < new Date();
  });

  onToggle(): void {
    this.toggled.emit(this.task().id);
  }
}
```

Three things to notice:

- **`task = input.required<Task>()`** declares that this component takes a required input of type `Task`. If a parent forgets to pass one, the template compiler complains.
- **`toggled = output<string>()`** declares an event this component can emit. The type parameter is the payload type — we emit the task's id.
- **`isOverdue` is a computed signal** that depends on `task()`. Because `task` is itself a signal, every time the parent passes a new value, `isOverdue` recomputes.

The template, in `task-row.html`:

```html
<li class="task" [class.done]="task().done" [class.overdue]="isOverdue()">
  <button class="toggle" (click)="onToggle()">
    <span class="title">{{ task().title }}</span>
    @if (task().dueDate) {
      <span class="due">due {{ task().dueDate | date: 'shortDate' }}</span>
    }
    @if (isOverdue()) {
      <span class="overdue-badge">overdue</span>
    }
  </button>
</li>
```

Notice `task().title` — you read a signal input just like any other signal, with `()`. The template repeats `task()` a few times; it is a cheap call (signals cache), and cleaner than assigning to a local first.

And `task-row.css`:

```css
:host { display: block; }

.task { padding: 0; margin: 0; border-bottom: 1px solid #eee; }
.task.done .title { text-decoration: line-through; color: #999; }
.task.overdue .title { color: #c73a52; }

.toggle {
  width: 100%; text-align: left; background: none; border: 0;
  padding: 12px 14px; display: flex; gap: 12px; align-items: center;
  cursor: pointer; font: inherit; color: inherit;
}

.due { margin-left: auto; font-size: 0.85rem; color: #666; }
.overdue-badge {
  font-size: 0.75rem; padding: 2px 6px; border-radius: 4px;
  background: #ffe3e3; color: #c73a52; margin-left: 8px;
}
```

The row is now a self-contained thing you can drop anywhere.

## Sending events up: `output()`

`output()` produces something with an `emit(value)` method. Calling it fires the event on the component; the parent listens with the `(name)="handler($event)"` syntax.

We already wrote `this.toggled.emit(this.task().id)` inside `TaskRow`. A parent will subscribe with:

```html
<app-task-row [task]="t" (toggled)="toggle($event)" />
```

`$event` in the handler is whatever was passed to `emit(...)` — here, the task id string. TypeScript flows the type through, so the parent's `toggle` method will get a typed `string`.

`output()` replaces the older `@Output() eventEmitter = new EventEmitter<T>()` pattern. Both still work; new code uses `output()`.

## Adding the form: `AddTaskForm`

Create it:

```bash
ng generate component add-task-form
```

Edit `src/app/add-task-form/add-task-form.ts`:

```ts
import { Component, signal, output } from '@angular/core';

@Component({
  selector: 'app-add-task-form',
  imports: [],
  templateUrl: './add-task-form.html',
  styleUrl: './add-task-form.css',
})
export class AddTaskForm {
  draft = signal('');
  add = output<string>();

  submit(): void {
    const title = this.draft().trim();
    if (title === '') return;
    this.add.emit(title);
    this.draft.set('');
  }

  onInput(event: Event): void {
    this.draft.set((event.target as HTMLInputElement).value);
  }
}
```

Template `add-task-form.html`:

```html
<form (submit)="submit(); $event.preventDefault()">
  <input
    type="text"
    placeholder="What needs doing?"
    [value]="draft()"
    (input)="onInput($event)" />
  <button type="submit" [disabled]="draft().trim() === ''">Add</button>
</form>
```

Style, `add-task-form.css`:

```css
:host { display: block; margin-bottom: 1em; }
form { display: flex; gap: 8px; }
input { flex: 1; padding: 10px; font: inherit; border: 1px solid #ccc; border-radius: 6px; }
button {
  padding: 10px 16px; font: inherit; border: 0; border-radius: 6px;
  background: #7a3fbf; color: white; cursor: pointer;
}
button:disabled { background: #ccc; cursor: not-allowed; }
```

`AddTaskForm` owns its own draft state (the user's in-progress typing). It emits an `add` event with the final title when the user submits. The parent does not need to know or care how the form works — it plugs into two contracts: the `add` output, and the tag `<app-add-task-form>`.

## The refactored `TaskList`

Now `TaskList` becomes short. Replace its class with:

```ts
import { Component, signal, computed } from '@angular/core';
import { Task } from '../task';
import { TaskRow } from '../task-row/task-row';
import { AddTaskForm } from '../add-task-form/add-task-form';

@Component({
  selector: 'app-task-list',
  imports: [TaskRow, AddTaskForm],
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
})
export class TaskList {
  tasks = signal<Task[]>([
    { id: 't1', title: 'Buy milk', done: false, createdAt: '2026-01-15T09:00:00Z', dueDate: null, tags: ['home'] },
    { id: 't2', title: 'Write chapter 8', done: true, createdAt: '2026-01-14T18:30:00Z', dueDate: '2026-01-16T00:00:00Z', tags: ['work'] },
    { id: 't3', title: 'Call the plumber', done: false, createdAt: '2026-01-15T11:00:00Z', dueDate: '2026-01-18T00:00:00Z', tags: ['home', 'urgent'] },
  ]);

  remaining = computed(() => this.tasks().filter(t => !t.done).length);

  onAdd(title: string): void {
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
  }

  onToggle(id: string): void {
    this.tasks.update(current =>
      current.map(t => (t.id === id ? { ...t, done: !t.done } : t))
    );
  }
}
```

And the template `task-list.html`:

```html
<h1>Tasks — {{ remaining() }} left</h1>

<app-add-task-form (add)="onAdd($event)" />

<ul class="task-list">
  @for (task of tasks(); track task.id) {
    <app-task-row [task]="task" (toggled)="onToggle($event)" />
  } @empty {
    <li class="empty">Nothing to do. Nice.</li>
  }
</ul>
```

Save. The app looks identical. Every piece of behavior is unchanged. But now:

- `TaskRow` can be reused wherever a task needs to render.
- `AddTaskForm` can be reused wherever you need to gather a title.
- `TaskList` is fifteen lines of orchestration.

This is the shape of an Angular app.

## Two-way with `model()`

`model()` gives you an input-output pair with `[(name)]` binding, packaged as one signal. It is useful when a child owns *some* of a shared piece of state — the classic case is a text input like the one we just built.

Suppose we wanted `AddTaskForm` to expose its `draft` to the parent for external display. We could do it by hand with an output; `model()` does it in one line.

Rewrite `add-task-form.ts`:

```ts
import { Component, model, output } from '@angular/core';

@Component({ /* ... */ })
export class AddTaskForm {
  draft = model('');
  add = output<string>();

  submit(): void {
    const title = this.draft().trim();
    if (title === '') return;
    this.add.emit(title);
    this.draft.set('');
  }

  onInput(event: Event): void {
    this.draft.set((event.target as HTMLInputElement).value);
  }
}
```

Now a parent can do:

```html
<app-add-task-form [(draft)]="currentDraft" (add)="onAdd($event)" />
```

Any change from either side is reflected in the other. If the parent doesn't care about the draft, it can just pass an `(add)` handler and skip `[(draft)]`. `model()` gives you optionality that a hand-rolled input/output pair does not.

For now, `TaskList` doesn't need to see the draft — the current template omits `[(draft)]` and everything works. Consider `model()` when you find yourself writing paired inputs and outputs whose names would just add "Change" to each other.

## Content projection: `<ng-content>`

Some components are not defined by the data they receive, but by the *content they wrap*. A modal dialog, a card, a collapsible section — each is a container whose interior is filled in by its caller. Angular's tool for this is *content projection*, via the `<ng-content>` element.

Here is a `Card` component:

```ts
import { Component, input } from '@angular/core';

@Component({
  selector: 'app-card',
  imports: [],
  template: `
    <div class="card">
      <h2 class="card-title">{{ title() }}</h2>
      <div class="card-body">
        <ng-content></ng-content>
      </div>
    </div>
  `,
  styles: `
    .card { border: 1px solid #ddd; border-radius: 8px; padding: 16px; }
    .card-title { margin: 0 0 8px 0; font-size: 1.1rem; }
  `,
})
export class Card {
  title = input.required<string>();
}
```

A parent uses it like this:

```html
<app-card title="Today">
  <p>Three tasks remaining.</p>
  <button>Refresh</button>
</app-card>
```

Whatever appears between `<app-card>` and `</app-card>` in the parent's template ends up wherever `<ng-content>` sits in the child's template. This lets one component define layout while callers fill in content.

### Named slots

If a container has multiple insertion points, use the `select` attribute:

```html
<!-- inside SplitCard -->
<div class="left">
  <ng-content select="[left]"></ng-content>
</div>
<div class="right">
  <ng-content select="[right]"></ng-content>
</div>
<div class="footer">
  <ng-content select="footer"></ng-content>
</div>
```

The parent tags each piece of content to route it to a slot:

```html
<app-split-card>
  <p left>Left column content.</p>
  <p right>Right column content.</p>
  <footer>Footer content.</footer>
</app-split-card>
```

Content that doesn't match any `select` goes to a plain `<ng-content>` if there is one, or is dropped otherwise.

Content projection is how you build design systems: cards, dialogs, tabs, table wrappers. Compass will use it in Chapter 15 when we introduce a shared "empty state" component.

## Accessing children: `viewChild` and `viewChildren`

Occasionally a parent needs to reach *into* a child — to focus an input, to trigger a method, to read a piece of state that isn't exposed via an output. Angular offers `viewChild()` and `viewChildren()` for this.

```ts
import { Component, viewChild, ElementRef, AfterViewInit } from '@angular/core';

@Component({
  selector: 'app-search',
  template: `<input #searchInput type="text" />`,
})
export class Search implements AfterViewInit {
  input = viewChild<ElementRef<HTMLInputElement>>('searchInput');

  ngAfterViewInit() {
    this.input()?.nativeElement.focus();
  }
}
```

`viewChild('searchInput')` returns a signal whose value is whatever element or component matched the template reference `#searchInput`. You read it with `()` like any signal; it may be `undefined` if the element hasn't rendered yet.

`viewChild` is a last resort. If you find yourself reaching for it, first ask: could this be done with an input, an output, or a signal? Nine times out of ten, it can. The one-in-ten case usually involves imperative browser APIs (focus, scroll, `<video>` playback).

## Guidelines for splitting components

When to break one component into two? Signs:

- The template is longer than a screen. If you scroll to read it, you'll have trouble maintaining it.
- Two visually distinct sections have nothing to do with each other. A "header" and a "list" in the same component should almost always be separate components.
- You are about to copy-paste a chunk of markup for a second use. Extract it first.
- The class has more than about ten fields. Some of them are probably about a sub-concern.

When *not* to split? When the parts are meaningless on their own. A "task row title" is not a component; it is a `<span>`. A "task row that also has a delete button and an overdue badge" is a component. The test: could you imagine using this component somewhere else, or testing it in isolation? If yes, extract. If no, leave it.

## What comes next

Part III begins with Chapter 9 on *dependency injection* — the mechanism that will let us pull the task data out of `TaskList` and into a service that other components can share. Chapter 10 hooks that service up to an HTTP backend; Chapter 11 introduces RxJS for the parts of the app where signals are not enough; Chapter 12 replaces our hand-rolled form with reactive forms.

By the end of Part III, Compass will talk to a real server, save the tasks you add, and stop losing your work when you refresh.

### Exercises

1. Extract a `TaskCount` component that displays "3 tasks left" and takes `total` and `done` as inputs. Compute the "left" number inside the component with a `computed`. Use it in `TaskList` in place of the current heading text.

2. Add a delete button to `TaskRow`. It should emit a `deleted` output with the task id. Wire up `TaskList` to remove tasks on this event. Do not let clicking the delete button also fire the toggle; use `$event.stopPropagation()` in the click handler.

3. Build a `Panel` component with content projection: a titled container with a body slot and an optional actions slot. Its template should be roughly `<div class="panel">` `<header>{{ title() }} <ng-content select="[actions]"/></header>` `<div class="body"><ng-content/></div>` `</div>`. Use it to wrap the task list — pass "Today" as the title and a "Clear completed" button in the actions slot.
