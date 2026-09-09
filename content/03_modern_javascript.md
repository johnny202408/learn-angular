# Chapter 3. Modern JavaScript you'll actually use

Angular is TypeScript on the outside and JavaScript on the inside. Everything the compiler produces, the browser runs. If a piece of JavaScript syntax looks unfamiliar in an Angular example later in the book, the odds are it is one of the features in this chapter. There are dozens more we will not cover — the modern JavaScript language is very large — but the subset here is roughly a hundred percent of what Angular application code actually uses.

If you have written recent JavaScript before, you can read this chapter as a checklist and skim past what you already know. If not, plan on trying every example in a browser's developer console (open your browser, press F12, click "Console") so the syntax lands in your fingers.

## Modules: `import` and `export`

Every file in a modern JavaScript or TypeScript project is a *module*. A module is a file that can *export* things (functions, classes, constants, types) for other files to use, and *import* things from other modules. This is the mechanism by which your app is split into files without polluting a global namespace.

There are two flavors of exports:

```ts
// tasks.ts

// Named export: exports a symbol under its own name.
export interface Task {
  id: string;
  title: string;
}

export function isOverdue(task: Task): boolean { /* ... */ return false; }

// Default export: one per file, imported without curly braces.
export default class TaskService {
  // ...
}
```

And correspondingly, two flavors of imports:

```ts
// app.ts

import TaskService from "./tasks";          // default
import { Task, isOverdue } from "./tasks";  // named
import * as tasks from "./tasks";           // everything, namespaced
```

Angular's style guide, and this book, prefer *named exports* almost universally. Default exports save one pair of braces but cost clarity: a default export's name at the import site is whatever the importer types, so `import Foo from "./bar"` and `import Baz from "./bar"` reference the same thing. Named exports keep names honest across the codebase.

Import paths that start with `./` or `../` are *relative* — they point to another file in your project. Paths that start with anything else are *bare specifiers* and refer to installed packages (`@angular/core`, `rxjs`, and so on).

> **Watch out.** Do not put the `.ts` extension in your imports (`from "./tasks.ts"`). Angular's build tooling handles the extension for you. In some other JavaScript environments — notably Node.js in ESM mode — you *do* need the extension. Angular is the first case, not the second.

## Arrow functions

An arrow function is a shorter way to write a function, with one important semantic difference from a normal function: it does not have its own `this`.

```ts
// Long form
const isDone = function(task) { return task.done; };

// Arrow, block body
const isDone = (task) => { return task.done; };

// Arrow, expression body — no braces, no return keyword
const isDone = task => task.done;

// Multiple parameters need parentheses
const compare = (a, b) => a.priority - b.priority;
```

The lack of its own `this` matters when you pass an arrow function as a callback:

```ts
class TaskService {
  tasks: Task[] = [];

  loadTasks() {
    fetch("/api/tasks")
      .then(res => res.json())
      .then(data => {
        // `this` here still refers to the TaskService instance,
        // because the arrow function inherits it from loadTasks.
        this.tasks = data;
      });
  }
}
```

If the inner callback had been a normal `function`, `this` inside it would be `undefined` (in strict mode) or the global object — a bug source that plagued JavaScript for a decade before arrows arrived. In Angular code, you will almost always want arrows for callbacks.

## Template literals

Backtick strings can contain interpolated expressions and span multiple lines:

```ts
const name = "Anna";
const greeting = `Hello, ${name}. Today is ${new Date().toDateString()}.`;
```

They are strictly better than string concatenation for anything longer than trivial. Angular templates themselves are template literals when you write inline templates:

```ts
@Component({
  template: `
    <h1>Welcome, {{ user.name }}</h1>
    <p>You have {{ taskCount() }} tasks today.</p>
  `,
})
```

The `{{ }}` inside is Angular's template syntax, not JavaScript's `${}`. They coexist because they never overlap: the outside literal is JavaScript, evaluated once when the component class is defined; the `{{ }}` is Angular's, re-evaluated whenever the data changes.

## Destructuring

Destructuring pulls fields out of an object (or elements out of an array) into named variables in a single expression.

```ts
const task = { id: "t1", title: "Buy milk", done: false };

// Instead of:
const id = task.id;
const title = task.title;

// You can write:
const { id, title } = task;
```

You can rename on the way out and provide defaults:

```ts
const { id: taskId, title, done = false } = task;
```

Destructuring works in function parameters, too:

```ts
function label({ title, done }: Task): string {
  return done ? `[x] ${title}` : `[ ] ${title}`;
}

label({ id: "t1", title: "Buy milk", done: false, /* ... */ });
```

Array destructuring uses the same idea with square brackets:

```ts
const [first, second, ...rest] = [1, 2, 3, 4, 5];
// first = 1, second = 2, rest = [3, 4, 5]
```

The `...rest` on the last line is the spread/rest operator, which we look at next.

## Spread and rest

The three-dot operator `...` has two related uses.

**Spread** expands the elements of an array (or the properties of an object) inline:

```ts
const priorities = [1, 2, 3];
const withZero = [0, ...priorities];        // [0, 1, 2, 3]

const base = { title: "Untitled", done: false };
const withId = { ...base, id: "t1" };       // { title, done, id }
```

Object spread is how you make a shallow copy of an object, and how you produce a modified copy without mutating the original:

```ts
const task: Task = { /* ... */ };
const updated = { ...task, done: true };
// task.done is still whatever it was; updated.done is true.
```

This "don't mutate; produce a new object" pattern is *the* pattern of modern reactive code in Angular. When we get to signals in Chapter 7, you will see it constantly.

**Rest** collects the remaining elements of an array or the remaining parameters of a function into a single variable:

```ts
function sum(first: number, ...others: number[]): number {
  return others.reduce((acc, n) => acc + n, first);
}

sum(1, 2, 3, 4);   // 10
```

Same three dots, opposite direction: spread expands, rest collects.

## Default parameters

Parameters can have defaults, and the defaults can reference earlier parameters:

```ts
function paginate(items: Task[], page: number, size: number = 20): Task[] {
  return items.slice(page * size, (page + 1) * size);
}

paginate(all, 0);        // uses size = 20
paginate(all, 0, 50);    // uses size = 50
```

Default parameters kick in whenever the argument is `undefined` — passing `null` does *not* trigger the default. This is worth remembering the first time it surprises you.

## Optional chaining and nullish coalescing

Two operators that quietly replaced a lot of defensive `if` chains.

**Optional chaining** — `?.` — returns `undefined` short-circuit if the left side is `null` or `undefined`, instead of throwing:

```ts
const city = user?.address?.city;
// Equivalent to:
const city2 = user && user.address ? user.address.city : undefined;
```

**Nullish coalescing** — `??` — returns the right side if the left side is `null` or `undefined`, otherwise the left side:

```ts
const display = user.nickname ?? user.name ?? "Anonymous";
```

The important distinction from `||` (which you may have seen used similarly) is that `??` only falls through on `null` and `undefined`, not on other falsy values. `0 || 10` gives you 10; `0 ?? 10` gives you 0. In Compass, `task.priority ?? 3` is a safe "default priority to 3 if unset," while `task.priority || 3` would incorrectly rewrite an intentional priority of 0.

## Promises

A **Promise** is a value that will exist in the future. Any operation that takes time — a network request, a file read, a timer — returns a Promise. A Promise is always in one of three states: *pending* (still waiting), *fulfilled* (produced a value), or *rejected* (produced an error).

You attach callbacks with `.then()` and `.catch()`:

```ts
fetch("/api/tasks")
  .then(res => res.json())
  .then(tasks => console.log(tasks))
  .catch(err => console.error("Something went wrong:", err));
```

Each `.then` receives the value the previous step returned. If any step throws or returns a rejected Promise, control jumps to the nearest `.catch`.

This "chain of thens" style used to be the standard way to write asynchronous code. It works, and Angular's underlying HTTP machinery still uses Promises in places, but the ergonomics are awkward as soon as the chain grows. Modern code uses `async`/`await` instead.

## `async` / `await`

`async` marks a function as returning a Promise, and lets you use `await` inside it. `await` pauses the function at that expression until the awaited Promise resolves, and then resumes with its value.

```ts
async function loadTasks(): Promise<Task[]> {
  const res = await fetch("/api/tasks");
  const tasks: Task[] = await res.json();
  return tasks;
}

// Later:
const tasks = await loadTasks();
```

Errors in `await`ed Promises come out as thrown exceptions, so you can use plain `try`/`catch`:

```ts
try {
  const tasks = await loadTasks();
} catch (err) {
  console.error("Could not load tasks:", err);
}
```

`async`/`await` is a nicer way to write the same computation a chain of `.then()`s expresses — but it is *the same computation*. Nothing runs synchronously. `await` still yields control back to the browser between steps. It is syntactic sugar, and it is delicious.

> **Note.** Angular sometimes uses Promises, sometimes uses *Observables* (an RxJS type), and increasingly uses signals for reactive state. Chapter 11 unpacks the difference between Promises and Observables — for now, the important thing is that you understand Promises, because everything else in the async world builds on them or replaces them.

## Array methods you will use constantly

Modern JavaScript's array methods are the toolkit of everyday application code. You will lean on them daily.

```ts
const tasks: Task[] = /* ... */;

// map: transform each element
const titles = tasks.map(t => t.title);

// filter: keep the elements that match
const active = tasks.filter(t => !t.done);

// find: get the first element that matches, or undefined
const buyMilk = tasks.find(t => t.title === "Buy milk");

// some / every: test the array as a whole
const anyOverdue = tasks.some(isOverdue);
const allDone = tasks.every(t => t.done);

// reduce: fold the array into a single value
const total = tasks.reduce((sum, t) => sum + (t.done ? 1 : 0), 0);

// includes: does the array contain this value?
const hasWork = tags.includes("work");

// sort: mutating! usually you want to copy first
const byPriority = [...tasks].sort((a, b) => a.priority - b.priority);
```

Three warnings about `sort` and its friends:

1. `sort`, `reverse`, and `splice` mutate the array in place. If you want a new sorted array without disturbing the original, spread it first: `[...tasks].sort(...)`.
2. `sort` with no comparator function coerces elements to strings, which is a legendary source of bugs. Numeric sorts *need* a comparator: `.sort((a, b) => a - b)`.
3. `reduce` is powerful and overused. If you find yourself writing a `reduce` that could be a `for` loop with two variables, the `for` loop is usually clearer.

## `for` loops

You have three main ways to iterate:

```ts
// for..of iterates values in an array-like or iterable
for (const task of tasks) {
  console.log(task.title);
}

// forEach is fine for side effects; can't break out of it
tasks.forEach(task => console.log(task.title));

// classical for is still useful when the index matters
for (let i = 0; i < tasks.length; i++) {
  console.log(`${i}: ${tasks[i].title}`);
}
```

`for..in` also exists but iterates *keys of an object*, not elements of an array. Because arrays have string keys ("0", "1", ...), `for..in` will do surprising things on arrays. Prefer `for..of` for arrays and `Object.keys(obj)` / `Object.entries(obj)` for objects.

## Objects and shallow copies

Copying objects is a place beginners get burned. Assignment does not copy; it creates a new reference to the same object.

```ts
const original = { title: "Buy milk", done: false };
const alias = original;
alias.done = true;
console.log(original.done);  // true — surprise
```

To copy, use spread (or `Object.assign`):

```ts
const copy = { ...original };
copy.done = true;
console.log(original.done);  // still false
```

This is a *shallow* copy: nested objects are still shared. If your object has nested objects and you need a deep copy, use `structuredClone(value)` (built into modern browsers).

## Classes, briefly

Angular is class-forward: components, services, directives, and pipes are all classes. You do not need to learn everything about classes today — Chapter 5 will do that — but the syntax is unsurprising:

```ts
class Counter {
  private count = 0;

  increment(): void {
    this.count += 1;
  }

  get value(): number {
    return this.count;
  }
}

const c = new Counter();
c.increment();
console.log(c.value);   // 1
```

The `private` keyword is TypeScript's, not JavaScript's — at runtime the field is accessible, but the compiler will refuse to let external code touch it. Modern JavaScript also has real `#` private fields; Angular's codebase uses TypeScript `private` for convention, so we will too.

## What we deliberately skipped

Generators (`function*`), the `Symbol` type, `Proxy`, `Reflect`, `Map` and `Set` (you will meet these when they help), regular expressions in detail, and the many subtleties of `this`. All are useful; none are required to build Compass. When you meet one of them, look it up on MDN — the Mozilla Developer Network is the canonical JavaScript reference.

## What comes next

Chapter 4 gets you a running Angular application. You will install Node.js, install the Angular CLI, run `ng new compass`, and take a slow tour of every file the CLI produces. By the end of Chapter 4, you will have Angular's default starter screen open in your browser and you will understand what every part of it is doing.

### Exercises

1. Given `const nums = [3, 1, 4, 1, 5, 9, 2, 6]`, use array methods to produce (a) an array of squares, (b) the sum of the squares, (c) the largest number, and (d) whether every number is less than 10. Write each as a single expression.

2. Write a function `updateTask(tasks: Task[], id: string, changes: Partial<Task>): Task[]` that returns a new array where the task with matching id has `changes` merged into it, and every other task is untouched. Use `map` and spread; do not mutate the input. (The type `Partial<Task>` means "all fields of Task, but every one is optional.")

3. Convert this Promise chain to `async`/`await`:

```ts
function loadWithAuth(): Promise<Task[]> {
  return fetch("/api/session")
    .then(res => res.json())
    .then(session => fetch("/api/tasks", { headers: { Authorization: session.token } }))
    .then(res => res.json());
}
```

Then think about what happens if the first `fetch` fails. Where does the error surface in each version?
