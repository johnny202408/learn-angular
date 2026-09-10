# Chapter 11. RxJS essentials

You have seen RxJS twice already: `HttpClient` returned Observables, and we unwrapped them with `firstValueFrom`. That is enough for request-response HTTP, but not for the parts of Compass yet to come. Search-as-you-type, live streams, coordinated form updates, and route parameters — all of them are naturally streams of values over time, and RxJS is Angular's tool for streams.

This chapter is not a full tour of RxJS. That library has a hundred operators and a subculture of its own. What you need for Compass, and for most Angular application code, is a specific subset: what an Observable is, how it differs from a Promise and from a signal, a dozen operators, and the interop points between Observables and signals. That is what this chapter covers.

## What an Observable is

An **Observable** is a producer of values over time. It might produce zero values (and then complete), one value (like an HTTP response), a fixed sequence (like the digits of pi), or an unbounded stream (like mouse events until the window closes). It might complete normally or error out. And it does nothing until someone *subscribes* to it — Observables are lazy.

Contrast with the two things you already know:

- **A Promise** produces one value at most. Once created, a Promise starts working immediately (it is eager) and eventually resolves or rejects. It cannot be cancelled and cannot deliver more than one value.
- **A signal** holds a current value at all times. Reading it always returns the value. Writing it notifies anyone tracking it.

An Observable is neither. It is a *plan* for producing values, activated by subscription, capable of producing many, and cancellable.

Concretely:

```ts
import { Observable } from 'rxjs';

const numbers = new Observable<number>(subscriber => {
  subscriber.next(1);
  subscriber.next(2);
  subscriber.next(3);
  subscriber.complete();
});

numbers.subscribe({
  next: n => console.log('got', n),
  complete: () => console.log('done'),
});
// Prints: got 1, got 2, got 3, done
```

You will almost never construct Observables with `new Observable`. In application code, they come from *creation functions* and from Angular APIs.

## Creating Observables

The functions that turn something into an Observable:

```ts
import { of, from, fromEvent, interval, timer } from 'rxjs';

const three = of(1, 2, 3);                      // emits 1, 2, 3 and completes
const fromArray = from([1, 2, 3]);              // emits array elements
const fromPromise = from(fetch('/api/tasks'));  // wraps a Promise

const clicks = fromEvent<MouseEvent>(document, 'click');  // emits on every click
const ticks = interval(1000);                             // emits 0, 1, 2, ... each second
const delayed = timer(500);                               // emits 0 after 500ms and completes
```

Two of these — `fromEvent` and `interval` — produce unbounded streams. `subscribe` to them, and they emit forever, or until you unsubscribe.

Angular gives you Observables for many built-in things:

```ts
this.http.get<Task[]>('/api/tasks');            // one emission, then complete
this.route.params;                              // emits on every route param change
this.route.queryParams;                         // emits on every query param change
formControl.valueChanges;                       // emits on every form control change
```

Each of these is a well-defined stream, and each pairs naturally with a small pipeline of operators to produce the value you actually want.

## Operators and `pipe`

An operator is a function that takes an Observable and returns a new Observable. `pipe` composes operators into a chain.

```ts
import { of, map, filter } from 'rxjs';

of(1, 2, 3, 4, 5)
  .pipe(
    filter(n => n % 2 === 0),
    map(n => n * 10)
  )
  .subscribe(n => console.log(n));  // 20, 40
```

There are dozens of operators. You will use maybe fifteen of them regularly. Here is that shortlist, roughly in order of how often you will reach for them.

**`map(fn)`** transforms each emission through `fn`. If `fn` returns a Promise or Observable, it is *not* awaited — for that, use `switchMap` or friends.

**`filter(fn)`** drops emissions for which `fn` returns false.

**`tap(fn)`** runs `fn` on every emission for its side effects, without changing the stream. Useful for logging and debugging. `tap({ error })` also runs on errors.

**`take(n)`** takes the first `n` emissions, then completes. `take(1)` is common when you want an Observable to behave like a Promise.

**`takeUntil(otherObservable$)`** completes the source stream when `otherObservable$` emits. Angular has a specialized `takeUntilDestroyed()` that ties an Observable's lifetime to a component's — we'll use it below.

**`debounceTime(ms)`** waits `ms` after the last emission before passing it through. Perfect for search-as-you-type: the user pauses, the request goes.

**`distinctUntilChanged()`** suppresses consecutive duplicate values. Also very useful for search: don't refetch if the query hasn't actually changed.

**`switchMap(fn)`** flattens the source through an inner Observable, cancelling any in-flight inner Observable when a new one arrives. This is the operator that makes search-as-you-type work: each keystroke triggers a new HTTP request, and the previous request is cancelled.

**`mergeMap(fn)`** flattens, but lets all inner Observables run concurrently. Rarely what you want for user-driven work; useful when you want parallel processing.

**`exhaustMap(fn)`** flattens, but ignores new source emissions while an inner Observable is still running. The right operator for "save" buttons: if the user clicks twice, don't fire two saves.

**`concatMap(fn)`** flattens, queueing inner Observables so they run one after another. Useful for ordered writes.

**`catchError(fn)`** intercepts errors and either returns a fallback Observable or re-throws. This is how you provide a default value on a failed HTTP call.

**`retry({ count, delay })`** re-subscribes on error. We used it in Chapter 10.

**`combineLatest([a$, b$])`** takes multiple Observables and emits an array of their latest values whenever any of them emits. Angular's route params + query params combination is a common use.

**`startWith(value)`** prepends a value to the stream, so subscribers get an immediate emission.

The rule of learning: don't try to memorize all of them. Learn map, filter, tap, take, debounceTime, distinctUntilChanged, and switchMap. Look up the rest when a problem calls for them.

## A worked example: search-as-you-type

Suppose Compass gets a search box. The user types "buy m," and Compass fetches `/tasks?q=buy%20m`. If the user is still typing when a response arrives, the response should be thrown away — the query is stale.

```ts
import { fromEvent } from 'rxjs';
import { debounceTime, distinctUntilChanged, filter, map, switchMap } from 'rxjs';

const input = document.querySelector('input')!;

fromEvent<Event>(input, 'input').pipe(
  map(e => (e.target as HTMLInputElement).value.trim()),
  debounceTime(200),
  distinctUntilChanged(),
  filter(q => q.length >= 2),
  switchMap(q => http.get<Task[]>(`/api/tasks?q=${encodeURIComponent(q)}`)),
).subscribe(results => {
  render(results);
});
```

Read it top to bottom:

1. Every input event, get the trimmed value.
2. Wait 200ms after the last keystroke.
3. Only proceed if the query changed.
4. Only proceed if there are at least two characters.
5. Fire the HTTP request. If a new keystroke arrives while this request is in flight, cancel it and start a new one.

That six-line pipeline replaces what would otherwise be a manually-managed timer, an in-flight request tracker, a debounce ref, and a comparison for change. This is what RxJS is for.

## Signals and Observables: interop

Most of Compass's state lives in signals. Most of Angular's built-in APIs emit Observables. The interop is two functions:

**`toSignal(observable, options)`** turns an Observable into a signal.

```ts
import { toSignal } from '@angular/core/rxjs-interop';

class TaskList {
  private route = inject(ActivatedRoute);
  filter = toSignal(this.route.queryParamMap.pipe(
    map(params => params.get('tag') ?? 'all')
  ), { initialValue: 'all' });
}
```

Now `filter` is a signal you can read in the template as `filter()`, and it updates whenever the route's query params change. `toSignal` also cleans up the subscription when the component is destroyed.

**`toObservable(signal)`** turns a signal into an Observable.

```ts
import { toObservable } from '@angular/core/rxjs-interop';

class TaskStore {
  filter = signal('all');
  filter$ = toObservable(this.filter);

  filteredTasks$ = this.filter$.pipe(
    switchMap(f => this.api.list(f))
  );
}
```

`toObservable` emits every time the signal changes, and the emission is the signal's new value. Combined with operators, this lets you build "signal-driven fetch" pipelines without leaving reactive land.

## Subscribing safely

Every subscription is a resource. If your component subscribes and never unsubscribes, the callback keeps running after the component leaves the screen — a leak. Angular gives you three good options and one bad one.

**Best (usually): the `async` pipe.** Bind an Observable directly in a template, and Angular subscribes and unsubscribes for you.

```html
<p>{{ user$ | async }}</p>
```

**Second best: `toSignal`.** For non-template consumers of an Observable. Angular tears down the subscription on component destroy.

**Third: `takeUntilDestroyed()`.** For explicit subscriptions in a component context.

```ts
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

class TaskList {
  constructor() {
    this.route.params.pipe(takeUntilDestroyed()).subscribe(params => {
      // ...
    });
  }
}
```

`takeUntilDestroyed()` reads the current DestroyRef (from DI) and completes the Observable when the component is destroyed. No explicit `ngOnDestroy` needed.

**Bad: bare `.subscribe()` without any teardown.** This is the leak. If your linter is decent, it will yell at you.

## Cold vs hot, briefly

An Observable is *cold* if each subscriber gets its own run of the producer, and *hot* if all subscribers share one run.

`http.get()` is cold: each subscription fires a new request. `fromEvent(document, 'click')` is *also* cold, though it fools people: each subscribe attaches its own `addEventListener`, so multiple subscribers get their own listeners rather than a shared stream. If you want DOM events shared across subscribers, wrap with `share()` or convert to a signal.

You will rarely have to think about this explicitly. Where it matters: if you `subscribe` to an `http.get` result twice, you fire two requests. Use `shareReplay(1)` to share one request among many subscribers, or convert to a signal.

## When not to use RxJS

RxJS is powerful. It is also overused. Signs you have overreached:

- Your components have five nested `pipe` calls to compute something a `computed` signal would express in one line.
- You have a `Subject` field on a service being used as a stateful bag. Use a signal.
- You are `.subscribe()`-ing to something and setting a field with the result. Use `toSignal`.
- You are debouncing a signal by piping through `toObservable` and `debounceTime`. Fine — but check whether a `linkedSignal` or a small effect is not clearer for your case.

The rule of thumb from Chapter 7 stands: signals for state, RxJS for streams. When you find yourself using RxJS for state, migrate; when you find yourself using signals for streams, ask why.

## What comes next

Chapter 12 wraps up Part III with reactive forms. Compass currently has a hand-rolled "Add task" input. In Chapter 12 we replace it with `FormGroup`, add validation, and build an edit dialog for tasks with due dates and tags. After Chapter 12, Compass has a real backend, real forms, and real reactive behavior — everything a small app needs before it grows into multiple pages, which is Part IV's job.

### Exercises

1. Write an Observable pipeline that takes clicks on a "load more" button and, for each click, appends the next page of tasks. Use `exhaustMap` so multiple rapid clicks don't fire multiple requests. Verify by clicking quickly.

2. Convert the search-as-you-type pipeline in this chapter to a Compass component. Create a `SearchBox` with an input, wire the pipeline in its constructor, and emit an `results` output. Use `takeUntilDestroyed` on the subscription.

3. `HttpClient` returns cold Observables — every subscribe re-fires the request. Prove this: subscribe to the same `http.get(...)` Observable twice and check the network tab. Then add `shareReplay(1)` and confirm it fires once. Why is `shareReplay(1)` and not `shareReplay()`?
