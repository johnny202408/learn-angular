# Appendix B. Debugging Angular apps

Everything in this book worked when you typed it, at some point. Everything you build after this book will break. This appendix is what to reach for when it does.

## The three questions

When something is wrong, ask, in order:

1. **What did I expect to see?**
2. **What am I seeing instead?**
3. **What could bridge the gap?**

Skip step 1 and you will fix the wrong problem. Skip step 2 and you will guess. Answer both explicitly before you touch any code.

## The browser DevTools tour

Every debugging session touches at least one of:

- **Console** — errors, warnings, and your `console.log` output. `console.dir(obj)` prints an object's properties, expandable. `console.table(arr)` prints arrays of objects as a table. `console.trace()` prints the call stack at that point.
- **Network** — every HTTP request. Filter by "XHR" for API calls. Click a request to see headers, body, and response. Check status codes: 2xx good, 4xx client error, 5xx server error.
- **Elements** — the live DOM. Click an element to see its attributes and computed styles. `$0` in the console refers to the currently-selected element.
- **Sources** — the loaded JavaScript, source-mapped back to your TypeScript. Set breakpoints; step through code.
- **Performance** — record a session, see the flame chart. Chapter 16 covered this.
- **Application** — inspect `localStorage`, `sessionStorage`, cookies, IndexedDB, service workers, and cache storage. Useful when persistence code misbehaves.

Learn the keyboard shortcut for DevTools: F12 in most browsers, Cmd+Option+I on macOS.

## Angular DevTools

Install the Angular DevTools browser extension. It adds two tabs to the browser DevTools:

- **Components** — the live component tree, with props, state, and injected services. Click a component to see its inputs and outputs.
- **Profiler** — record change detection cycles. See which components re-rendered, when, and how long each took.

If the Components tab shows "Angular is not detected," you are looking at a page that isn't Angular, or Angular is running in production mode (which by default disables devtools support). Compass's dev build supports it out of the box.

## Reading Angular error messages

Angular errors are three parts: an **NG code** (like `NG0100`), a **short message**, and a **detailed message with a link**.

The NG code is your best friend. Search for it: `NG0100 site:angular.dev`. The official docs have an explanation with common causes for every code. (`angular.io` is a legacy domain that redirects to `angular.dev`; search results still work, but the current canonical domain is `.dev`.)

The most common codes:

- **NG0100 — ExpressionChangedAfterItHasBeenCheckedError.** Something changed a bound value during change detection. Look for a value being written in `ngAfterViewInit` or in an expression that computes different results on consecutive calls.
- **NG0200 — Circular dependency in DI.** Two services depend on each other. Redesign.
- **NG0201 — No provider found.** You injected something the current injector doesn't know about. Add `providedIn: 'root'` on the service, or `providers: [...]` in `app.config.ts`.
- **NG0950 — Required input is missing.** A component declared `input.required<T>()` but the parent didn't supply a value. Usually a `[value]` binding you forgot on `<app-thing>`.
- **NG05104 — Root element was not found.** The element `bootstrapApplication` was looking for (matching the root component's selector) isn't in `index.html`. Check that `<app-root>` (or whatever your selector is) exists in `src/index.html`.

The "detailed message with a link" is generated at runtime and is often the most useful part. It tells you which component, which template line, which expression.

## Reading TypeScript errors

TypeScript's compiler errors are dense but precise. Read the whole message; the last line is usually the punchline.

```
error TS2322: Type 'string | null' is not assignable to type 'string'.
  Type 'null' is not assignable to type 'string'.
```

The pattern: "type X is not assignable to type Y." Y is what a function or field expects. X is what you handed it. The fix is either to narrow X (`if (x !== null) { ... }`), assert it (`x!` — sparingly), or change Y to accept the wider type.

Two extra tricks:

- **Hover over a red squiggle in VS Code.** The full error message appears, sometimes with quick-fix suggestions.
- **Cmd/Ctrl-click a type name** to jump to its definition. This works on `Task`, `HttpClient`, everything.

## `console.log` productively

You will `console.log` a lot. Two techniques:

**Label your logs.** `console.log('tasks after add:', tasks)` is much easier to find in the console than `console.log(tasks)` when there are twenty of them.

**Log signals with `()`.** `console.log('tasks:', this.tasks())` prints the current value. `console.log('tasks:', this.tasks)` prints the signal function itself, which is rarely what you want.

**Remove them before committing.** Or wrap them: `if (!environment.production) console.log(...)`.

## The Sources debugger

`console.log` is fast; the debugger is stronger. In VS Code, place a red dot next to a line by clicking in the gutter, then run `ng serve` and interact with the page — execution stops at the breakpoint, and you can inspect every variable in scope, step over, step into, and continue.

Debug with the browser's DevTools instead if you prefer: open Sources, navigate to your `.ts` file (source maps make them visible), click the line number to set a breakpoint. Same experience, browser-native.

For particularly tricky bugs, `debugger;` in your code acts as a hardcoded breakpoint. Remove it before committing (or your linter will).

## Common Angular gotchas

A grab bag of things that trip people up.

**"Signal shows as a function, not its value."**

You forgot the parentheses. `{{ tasks }}` prints the function object; `{{ tasks() }}` prints its current value.

**"Template says nothing changed, but I clearly changed the data."**

You mutated an array or object in place. Angular tracks references. Use spread to produce a new one: `this.tasks.update(t => [...t, newTask])`.

**"My HTTP call fires twice."**

You subscribed to a cold Observable twice. Every subscribe re-fires the request. Use `firstValueFrom`, an `async` pipe, or `shareReplay(1)`.

**"My subscription runs forever."**

You didn't tear it down. Use `takeUntilDestroyed()` or the `async` pipe.

**"The template compiler says a component doesn't exist."**

You didn't add it to `imports` in the parent component's `@Component`. Standalone components explicitly declare their dependencies.

**"`ng serve` doesn't refresh."**

Save the file (Cmd/Ctrl+S). Some editors have unsaved-file indicators; if you see a dot next to the filename, save.

**"Two-way binding doesn't update."**

`[(ngModel)]` requires `FormsModule` to be imported into the component. Or use a signal-based `model()`.

**"Route doesn't match."**

Trailing slashes, missing leading slash, or the wildcard route above your target. `path: 'foo/bar/'` won't match `/foo/bar`.

**"CORS error in the console."**

Not an Angular problem. The backend needs to send permissive `Access-Control-Allow-Origin` headers. Fix on the server, not the client.

**"Route params are `undefined`."**

You are reading them synchronously in the constructor, but the router hasn't populated them yet. Either use `withComponentInputBinding()` + `input()`, or subscribe to `route.paramMap`.

**"Everything is fine locally but broken in production."**

Something is different. Common culprits: environment variable substitution not configured (Chapter 19), a package installed as `devDependencies` that is actually needed at runtime, aggressive minification breaking a library that relies on function names.

## Zone.js weirdness

If you are still on Zone.js (which the current default `ng new` is), sometimes async code updates a signal but the DOM doesn't refresh. The signal API is generally safe; but some older subscription patterns emit outside Angular's zone.

Fix: wrap the offending code in `NgZone.run()`, or migrate to signals + `provideExperimentalZonelessChangeDetection`. Zoneless removes an entire class of bug.

## When to ask for help, and how

You will get stuck. When you do:

1. **Search the exact error message.** Someone has hit it. Their StackOverflow answer is your fastest path.
2. **Check the official Angular docs.** `angular.dev` has an excellent search.
3. **Ask on the Angular Discord** or on StackOverflow. Include a minimal reproduction: the smallest code that shows the problem. Half the time you find the fix while distilling the repro.

Do not:

- Post twenty files of code hoping someone will read all of them.
- Say "it doesn't work." Say what you expected, what you saw, and what you already tried.
- Copy an error message without context. Include the surrounding code.

The rule of the room: come with the three questions from the top of this appendix answered, and someone will help you fast.

## Reading stack traces

A stack trace goes bottom-up: the last line is the outermost caller, the first line is where the error was thrown. Read it in reverse for the "why," and forward for the "where."

Angular stack traces are noisier than plain JS traces because they include internal framework calls. Ignore anything under `zone.js`, `platform-browser`, or `core.mjs` — those are Angular's plumbing. Look for the first line that names *your* code.

Source maps make the file names in the trace refer to your `.ts` files, not the compiled JS. If you see filenames like `main-a1b2c3.js`, source maps aren't working — usually because you built without them or the map files aren't being served.

## The "delete and see" technique

When something works and you don't know why, or breaks and you don't know why, delete pieces of code until behavior changes. Whatever you last deleted is the cause.

This works especially well for CSS: rules cascading unexpectedly, styles bleeding across components, weird layout. Comment out sections; watch what changes.

## When you have exhausted every idea

Take a walk. Genuinely. The debugger's most powerful feature is your own attention, and attention degrades with fatigue. A ten-minute break saves an hour of guessing.

If the walk doesn't work: read the code you wrote most recently, aloud, from the top. Not skim — read. You will notice the typo or the transposed argument on the first pass, and you will feel foolish, and it will happen again next month. This is part of the job.
