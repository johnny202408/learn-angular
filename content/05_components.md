# Chapter 5. Components: the atom of an Angular app

We have set up the workshop; now we start building. This is the first chapter where you write real Angular code. By the end you will have deleted the CLI's starter template, replaced it with your own component, and displayed a hardcoded list of tasks in the browser. That is a small accomplishment on its own, and it is also the moment where the shape of an Angular application clicks into place.

Keep `ng serve` running in one terminal, and your editor open on the `compass` folder. Every code block in this chapter is meant to be typed in and observed.

## What a component is, revisited

In Chapter 1 I described a component as a *self-contained piece of the screen*: some HTML, some CSS, and some behavior, packaged together. Now that you have a project on your disk, we can be more concrete. A component is:

- **A TypeScript class** that holds the component's state (fields) and behavior (methods).
- **Decorated with `@Component`** — a piece of metadata that tells Angular "this class is a component, and here is its selector and its template."
- **Associated with a template**, which is a piece of HTML augmented with Angular's binding syntax.
- **Optionally associated with styles**, scoped so they do not leak to the rest of the app.
- **Used in another component's template by name**, via its selector.

That last point is the mechanism by which a component *tree* forms. Compass's root component (`App`) will eventually include a `<app-task-list>` in its template. That `<app-task-list>` is another component we are about to write. Inside `<app-task-list>` will be many `<app-task-row>` instances, one per task. Every element that starts with `app-` in your templates is a component you defined; every element that does not (like `<div>` or `<button>`) is regular HTML.

## The `@Component` decorator, field by field

Open `src/app/app.ts` (or `app.component.ts`; the filename depends on the CLI version, and the CLI defaults have varied). It looks something like:

```ts
import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly title = signal('compass');
}
```

Let's walk through the `@Component` fields one by one.

**`selector`** is the HTML tag name that represents this component. `'app-root'` means this component appears anywhere `<app-root>` is written. Selectors are how components find each other; they are also how the outside world (in this case, `index.html`) can drop your app into a page. Angular convention is a short, application-specific prefix (`app-` here) followed by the component's role. You will name components like `<app-task-row>`, `<app-add-task-form>`, `<app-habit-badge>`.

Why the prefix? To avoid collisions with real HTML elements and with third-party components. A tag like `<button>` is a native HTML element; a tag like `<mat-button>` is from Angular Material; a tag like `<app-button>` is yours. The prefix keeps them straight.

**`imports`** is a list of other components, directives, and pipes this component's template uses. In modern Angular, every standalone component declares its dependencies explicitly. If your template contains `<router-outlet>`, you must import `RouterOutlet`; if it contains `<app-task-row>`, you must import `TaskRow`. This is one of the things that surprises newcomers ("do I really have to list everything?") and then quietly earns its keep ("I moved this component into another app and it still works").

**`templateUrl`** points to the HTML file that this component renders. Alternatively you can use **`template`**, which takes an inline string:

```ts
@Component({
  selector: 'app-hello',
  template: `<h1>Hello.</h1>`,
})
export class Hello {}
```

Inline templates are convenient for tiny components (under about 10 lines). Anything larger belongs in a separate file. The book uses both, favoring separate files for real components and inline for one-liners.

**`styleUrl`** (or `styles`, or `styleUrls`) points to the component's scoped CSS. Everything in the file applies only inside instances of this component — a class called `.title` here will not collide with a `.title` class elsewhere in the app. This is done via *view encapsulation*, which Angular implements by adding a unique attribute to each element the component renders and rewriting your CSS to target that attribute. You do not need to think about the mechanism; you only need to know that CSS you write in a component stays inside that component.

## Building Compass's first real component

Let's replace the CLI's starter with something we own. We'll build a `TaskList` component that shows a hardcoded list of tasks. In later chapters we will replace the hardcoded data with signals, then with a service, then with HTTP.

From your `compass` folder:

```bash
ng generate component task-list
```

This creates `src/app/task-list/` containing:

```
task-list/
├── task-list.ts        (or task-list.component.ts)
├── task-list.html
├── task-list.css
└── task-list.spec.ts
```

Open `task-list.ts`:

```ts
import { Component } from '@angular/core';

@Component({
  selector: 'app-task-list',
  imports: [],
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
})
export class TaskList {}
```

We are going to give this component a *type* for tasks and a hardcoded list. First, let's put the type in its own file so we can share it later. Create `src/app/task.ts`:

```ts
export interface Task {
  id: string;
  title: string;
  done: boolean;
  createdAt: string;
  dueDate: string | null;
  tags: string[];
}
```

Now edit `task-list.ts`:

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
  tasks: Task[] = [
    {
      id: 't1',
      title: 'Buy milk',
      done: false,
      createdAt: '2026-01-15T09:00:00Z',
      dueDate: null,
      tags: ['home'],
    },
    {
      id: 't2',
      title: 'Write chapter 5',
      done: true,
      createdAt: '2026-01-14T18:30:00Z',
      dueDate: '2026-01-16T00:00:00Z',
      tags: ['work'],
    },
    {
      id: 't3',
      title: 'Call the plumber',
      done: false,
      createdAt: '2026-01-15T11:00:00Z',
      dueDate: '2026-01-18T00:00:00Z',
      tags: ['home', 'urgent'],
    },
  ];
}
```

Now edit `task-list.html` to display them. Chapter 6 covers the syntax in depth; for now, copy it and observe:

```html
<h1>Tasks</h1>
<ul class="task-list">
  @for (task of tasks; track task.id) {
    <li class="task" [class.done]="task.done">
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

And give it some scoped styling in `task-list.css`:

```css
:host {
  display: block;
  max-width: 480px;
  margin: 2em auto;
  font-family: system-ui, sans-serif;
}

h1 {
  font-size: 1.4rem;
  margin: 0 0 1em 0;
}

.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.task {
  padding: 12px 14px;
  border-bottom: 1px solid #eee;
  display: flex;
  gap: 12px;
  align-items: center;
}

.task.done .title {
  text-decoration: line-through;
  color: #999;
}

.due {
  margin-left: auto;
  font-size: 0.85rem;
  color: #666;
}

.empty {
  padding: 20px;
  text-align: center;
  color: #999;
  font-style: italic;
}
```

## Using the component

Two more edits and we can see it in the browser.

First, tell the root component to render `<app-task-list>`. Edit `src/app/app.ts`:

```ts
import { Component } from '@angular/core';
import { TaskList } from './task-list/task-list';

@Component({
  selector: 'app-root',
  imports: [TaskList],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {}
```

Two important changes: we removed the `RouterOutlet` import (we'll bring it back in Chapter 13), and we added `TaskList` to `imports`. Any component that appears in this component's template must be imported.

Second, edit `src/app/app.html`. Delete whatever the CLI put there and replace with:

```html
<app-task-list></app-task-list>
```

Save. Look at your browser tab. You should see a heading "Tasks" and three items — one with a strikethrough (the completed one) and two with due dates.

You just wrote your first Angular component and mounted it in the app. Take a minute to appreciate that.

## What `:host` is doing

You probably noticed the `:host` pseudo-class in `task-list.css`. That is how a component's stylesheet refers to the component's own root element — `<app-task-list>` itself, from outside. Inside the CSS file, `:host` is the wrapper; everything inside the component's template is descendant content of `:host`.

The distinction matters because Angular renders each component into its own element. When Angular sees `<app-task-list>` in `App`'s template, it does not replace that tag with the task list's markup; it *inserts* the markup inside the tag. That preserves the encapsulation boundary and gives you a place to hang styles like `display: block` or `margin` on the component as a whole.

## Component lifecycle, in one paragraph

Every component goes through a few moments in its life: it is *constructed* (the class is instantiated), then *initialized* (Angular has wired up its inputs), and eventually *destroyed* (the component is removed from the DOM, and it should clean up any subscriptions). Angular provides lifecycle *hooks* — methods you can define with specific names — for these moments: `ngOnInit`, `ngOnDestroy`, and a handful of others. In older Angular code these were everywhere.

In modern Angular, most of the reasons you would have reached for a lifecycle hook are better served by other primitives — signals, `computed`, `effect`, and DI-based reactivity. The remaining valid uses are narrow: doing one-time setup that needs to see inputs (rare — `computed` is usually better), or cleanup of external resources not managed by Angular (rare — `takeUntilDestroyed` is usually better). We will meet the hooks properly when we need them; do not go looking for them.

## Signal-friendly by default

Note that in this chapter, `tasks` is a plain field on the class — `tasks: Task[] = [...]`. That works: the template reads it and renders. But it is not *reactive*. If you later add a button that pushes a new task onto the list, Angular will re-render the list (thanks to zone-based change detection, which is the classic mechanism); but this behavior is on its way out. Modern Angular is moving toward signals as the reactive primitive, and Compass will make that shift starting in Chapter 7.

For now, plain fields are enough. Chapter 6 spends its time on the template syntax (`@for`, `@if`, `{{ }}`); Chapter 7 rewrites `tasks` as a signal. The pattern of the book is: introduce the plain version, feel the itch, learn the reactive version, sigh with relief.

## Inline vs external templates

Two styles, both are fine:

```ts
// External (default from `ng generate`)
@Component({
  selector: 'app-task-list',
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
})

// Inline
@Component({
  selector: 'app-empty-state',
  template: `
    <div class="empty">
      <p>{{ message }}</p>
    </div>
  `,
  styles: `
    .empty { padding: 20px; text-align: center; }
  `,
})
```

Rules of thumb: templates under about 10 lines of markup are fine inline; anything larger is easier to read in a separate file. If your inline template starts having `@for` and multiple `@if` branches, move it to a `.html` file — your editor will thank you (syntax highlighting, autocomplete, indentation all get better).

## View encapsulation, briefly

Every component has a `ViewEncapsulation` mode. The default is `Emulated`, which is what we described above — Angular scopes your CSS to the component by adding attributes. `None` disables scoping (your CSS becomes global — usually not what you want). `ShadowDom` uses the browser's actual Shadow DOM API for scoping, which is stronger but comes with quirks around styling, fonts, and third-party libraries.

You will almost always leave encapsulation on the default. The one time you would change it is if you were building a component library and needed the strongest possible isolation.

## What comes next

Chapter 6 covers everything that just happened in the template. You have seen `{{ }}`, `[class.done]`, `@for`, `@if`, `@empty`, and `| date: 'shortDate'`. In Chapter 6 we look at each of them properly, along with property bindings, event bindings, and two-way bindings. By the end of Chapter 6, Compass will respond to clicks — you will be able to toggle tasks between done and not done.

### Exercises

1. Add a fourth task to the hardcoded array — one that is `done: true` and has a `dueDate` in the past. Save and confirm it renders with the strikethrough and its overdue date. Do not use any Angular features other than the ones this chapter covered.

2. Change the `selector` in `task-list.ts` from `'app-task-list'` to `'compass-task-list'`. Save and refresh the browser. What breaks? Fix it. Notice that selectors are a small contract between two files (the component and its user).

3. Run `ng generate component habit-badge`. Read the four files the CLI produces. Which of them are new information after this chapter? Which are boilerplate you can now write from memory?
