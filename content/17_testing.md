# Chapter 17. Testing: TestBed, component harnesses, Playwright

Compass works. You have seen it work: you have clicked around, added tasks, and refreshed the page. But "it worked when I tried it" is not the same as "it will keep working when we change it next month." Tests are the difference. A good test suite lets you rename a signal, extract a service, or move a component with confidence — the tests will tell you what broke.

This chapter covers three layers of testing in Angular:

- **Unit tests** for stores, services, and pipes with `TestBed`.
- **Component tests** for individual components, using the CDK component harnesses.
- **End-to-end tests** for user flows across the whole app, with Playwright.

You will not test everything. Compass, like every real app, will always have testable code you haven't tested. The goal is not coverage — it is confidence. Test what would ruin your day if it broke, and what you keep breaking accidentally.

## The testing setup Angular gives you

`ng new` scaffolds a testing setup out of the box: **Jasmine** as the assertion framework and **Karma** as the browser runner. Every generated file has a corresponding `.spec.ts` next to it.

Run the tests:

```bash
ng test
```

A browser window opens (Karma launches a real Chrome), runs the tests, and reports. On the second run, the browser stays open; changes to test files re-run the affected specs automatically.

If you want a modern, headless alternative, the Angular ecosystem also supports **Vitest** and **Web Test Runner**. Switching is a configuration change, not a rewrite — the test API is unchanged. Karma is being retired but is still the default at time of writing; Vitest is the direction of travel.

Regardless of runner, you write tests the same way: with Jasmine (`describe`, `it`, `expect`) and `TestBed`.

## `TestBed`: DI for tests

`TestBed` is Angular's testing container. It configures an injector, lets you register providers (real or fake), and lets you instantiate components and services under test.

The pattern:

```ts
import { TestBed } from '@angular/core/testing';
import { TaskStore } from './task-store';
import { TasksApi } from './tasks-api';

describe('TaskStore', () => {
  let store: TaskStore;
  let apiSpy: jasmine.SpyObj<TasksApi>;

  beforeEach(() => {
    apiSpy = jasmine.createSpyObj<TasksApi>('TasksApi', ['list', 'create', 'update', 'remove']);
    TestBed.configureTestingModule({
      providers: [
        TaskStore,
        { provide: TasksApi, useValue: apiSpy },
      ],
    });
    store = TestBed.inject(TaskStore);
  });

  it('starts with an empty tasks array', () => {
    expect(store.tasks()).toEqual([]);
  });

  it('loads tasks from the API', async () => {
    apiSpy.list.and.resolveTo([
      { id: 't1', title: 'a', done: false, createdAt: '', dueDate: null, tags: [] },
    ]);
    await store.load();
    expect(store.tasks().length).toBe(1);
    expect(store.tasks()[0].title).toBe('a');
  });

  it('surfaces errors from the API', async () => {
    apiSpy.list.and.rejectWith(new Error('boom'));
    await store.load();
    expect(store.tasks()).toEqual([]);
    expect(store.error()).toContain('Could not load');
  });
});
```

The key move: `{ provide: TasksApi, useValue: apiSpy }`. Because `TaskStore` gets `TasksApi` via DI (`inject(TasksApi)`), the test replaces it with a spy. The store cannot tell — it just calls methods on whatever it was handed.

`jasmine.createSpyObj` builds an object whose named methods are pre-stubbed with `jasmine.Spy`. Each spy method has `and.resolveTo(value)`, `and.rejectWith(err)`, `and.returnValue(v)`, `and.callFake(fn)` for controlling behavior, and `.calls.count()`, `.calls.mostRecent()`, etc. for asserting on how it was called.

This is what makes Angular so testable: because everything comes in through DI, everything can be swapped in tests without touching the code under test.

## Testing signals

Signals are values, not events. You test them by reading them at the right time.

```ts
it('remaining ignores done tasks', () => {
  store['_tasks'].set([
    { id: 't1', title: 'a', done: false, /* ... */ } as Task,
    { id: 't2', title: 'b', done: true,  /* ... */ } as Task,
  ]);
  expect(store.remaining()).toBe(1);
});
```

The bracket access `store['_tasks']` is a slight cheat — it reaches into the private signal to set state directly. For most tests, prefer to drive state through the public API (call `store.add`, `store.toggle`). Reaching for the private signal is fine when a test is explicitly about a derived value and you don't want to set up the whole API dance.

For async signal changes, `await` the promise that drives the change, then read:

```ts
it('sets loading true then false around a load', async () => {
  const seen: boolean[] = [];
  const stop = TestBed.runInInjectionContext(() =>
    effect(() => seen.push(store.loading()))
  );
  apiSpy.list.and.resolveTo([]);
  await store.load();
  expect(seen).toEqual([false, true, false]);
});
```

`effect` inside a test needs to run in an injection context, which `TestBed.runInInjectionContext` provides.

## Testing pipes

Pipes are functions. Test them like functions.

```ts
import { TimeAgoPipe } from './time-ago.pipe';

describe('TimeAgoPipe', () => {
  let pipe: TimeAgoPipe;

  beforeEach(() => {
    pipe = new TimeAgoPipe();
  });

  it('returns "just now" for recent times', () => {
    const twentySecondsAgo = new Date(Date.now() - 20_000).toISOString();
    expect(pipe.transform(twentySecondsAgo)).toBe('just now');
  });

  it('returns a minute count for < 45 minutes', () => {
    const tenMinutesAgo = new Date(Date.now() - 10 * 60_000).toISOString();
    expect(pipe.transform(tenMinutesAgo)).toBe('10 minutes ago');
  });

  it('handles null gracefully', () => {
    expect(pipe.transform(null)).toBe('');
  });
});
```

No `TestBed` needed — the pipe has no injected dependencies. This is the easiest kind of test, and pipes are often over-covered because of that. Test the interesting edge cases; skip the trivial ones.

## Testing components with `ComponentFixture`

`TestBed.createComponent` instantiates a component and returns a `ComponentFixture` — a wrapper with access to the component instance, its rendered DOM, and change detection controls.

```ts
import { TestBed } from '@angular/core/testing';
import { AddTaskForm } from './add-task-form';
import { By } from '@angular/platform-browser';

describe('AddTaskForm', () => {
  it('emits add with the trimmed title', async () => {
    await TestBed.configureTestingModule({
      imports: [AddTaskForm],
    }).compileComponents();

    const fixture = TestBed.createComponent(AddTaskForm);
    fixture.detectChanges();

    const emitted: string[] = [];
    fixture.componentInstance.add.subscribe(v => emitted.push(v));

    const input: HTMLInputElement = fixture.debugElement.query(By.css('input')).nativeElement;
    input.value = '  Buy milk  ';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    const form: HTMLFormElement = fixture.debugElement.query(By.css('form')).nativeElement;
    form.dispatchEvent(new Event('submit'));

    expect(emitted).toEqual(['Buy milk']);
  });
});
```

Two things to note:

- **`fixture.detectChanges()`** runs Angular's change detection for the fixture's tree. Call it after you mutate an input or a signal to see the rendered DOM update.
- **`By.css(selector)`** queries the rendered DOM. `fixture.debugElement.query(...)` returns a `DebugElement`; `.nativeElement` is the underlying HTML element.

This kind of test works but is verbose. For real component testing, the CDK component harnesses are much better.

## Component harnesses

A **harness** is a class that wraps a component and exposes its behavior at a task level — "click the submit button," "read the error message" — rather than at the DOM level. Angular's CDK library provides a base class and Angular Material provides harnesses for every Material component out of the box. You can write your own harnesses for your own components.

```ts
import { ComponentHarness } from '@angular/cdk/testing';

export class AddTaskFormHarness extends ComponentHarness {
  static hostSelector = 'app-add-task-form';

  private input = this.locatorFor('input');
  private submitButton = this.locatorFor('button[type=submit]');

  async setTitle(v: string): Promise<void> {
    const el = await this.input();
    await el.sendKeys(v);
  }

  async submit(): Promise<void> {
    const btn = await this.submitButton();
    await btn.click();
  }

  async isSubmitDisabled(): Promise<boolean> {
    const btn = await this.submitButton();
    return (await btn.getProperty('disabled')) as boolean;
  }
}
```

Using it in a test:

```ts
import { TestbedHarnessEnvironment } from '@angular/cdk/testing/testbed';

it('disables submit while empty', async () => {
  const fixture = TestBed.createComponent(AddTaskForm);
  const harness = await TestbedHarnessEnvironment.harnessForFixture(fixture, AddTaskFormHarness);
  expect(await harness.isSubmitDisabled()).toBe(true);
  await harness.setTitle('New task');
  expect(await harness.isSubmitDisabled()).toBe(false);
});
```

The test reads like the user's actions. No `dispatchEvent`, no `detectChanges`, no `nativeElement`. Every method is `async` because harnesses work identically in unit tests (TestBed) and end-to-end tests (Protractor / Playwright) — the async-ness is what makes that portability possible.

Writing a harness for each of Compass's components is more code than the components themselves. In practice, teams write harnesses for components used by multiple tests — the "add task form" gets one because five tests exercise it; a one-off component doesn't. Match your investment to the reuse.

## Testing components that inject services

The pattern is the same as testing stores: provide fakes.

```ts
it('shows tasks from the store', async () => {
  const fakeStore = {
    tasks: signal<Task[]>([{ id: 't1', title: 'a', done: false, /* ... */ } as Task]),
    remaining: signal(1),
    loading: signal(false),
    error: signal(null),
    load: () => Promise.resolve(),
    add: () => Promise.resolve(),
    toggle: () => Promise.resolve(),
  };
  await TestBed.configureTestingModule({
    imports: [TaskList],
    providers: [{ provide: TaskStore, useValue: fakeStore }],
  }).compileComponents();

  const fixture = TestBed.createComponent(TaskList);
  fixture.detectChanges();

  expect(fixture.nativeElement.textContent).toContain('a');
});
```

Signals in the fake need to be actual signals — the component reads them with `()`. Plain values won't do.

## End-to-end tests with Playwright

Unit tests exercise pieces. End-to-end (E2E) tests exercise the whole thing: a real browser, a real server, a real user flow.

Angular no longer scaffolds Protractor. Playwright is the modern choice; the CLI has an official schematic:

```bash
ng add @angular-eslint/schematics    # if you don't have it
ng add @playwright/test              # or manually per Playwright docs
```

A Playwright test:

```ts
import { test, expect } from '@playwright/test';

test('adds a task', async ({ page }) => {
  await page.goto('http://localhost:4200/');
  await page.fill('input[type=text]', 'Wash the car');
  await page.click('button[type=submit]');
  await expect(page.locator('li.task').filter({ hasText: 'Wash the car' })).toBeVisible();
});
```

The test drives a real browser. It clicks, types, waits for elements, and asserts. Playwright handles auto-waiting so you rarely need `sleep`s.

E2E tests need `ng serve` and `json-server` running. In CI, you script them to boot before the tests run and shut down after. Playwright has a `webServer` config option for this.

E2E tests are slow and flakey by nature (real network, real timing). Do not try to test every path with E2E. Test the *critical journeys*: sign in and see your tasks, add a task and refresh, delete a task and confirm it's gone.

## Testing routing and guards

The router has its own testing utilities. `RouterTestingHarness` is the modern way:

```ts
import { provideRouter } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';

it('navigates to task detail', async () => {
  await TestBed.configureTestingModule({
    providers: [provideRouter(routes)],
  }).compileComponents();

  const harness = await RouterTestingHarness.create();
  const detail = await harness.navigateByUrl<TaskDetail>('/task/t1', TaskDetail);
  expect(detail.id()).toBe('t1');
});
```

Guards and resolvers are functions; test them with a `TestBed` that provides their dependencies, and call them directly:

```ts
it('redirects unauthenticated users', () => {
  const routerSpy = jasmine.createSpyObj('Router', ['navigateByUrl']);
  const authSpy = { isSignedIn: signal(false) };
  TestBed.configureTestingModule({
    providers: [
      { provide: Router, useValue: routerSpy },
      { provide: AuthStore, useValue: authSpy },
    ],
  });
  const allowed = TestBed.runInInjectionContext(() => requireAuth({} as any, {} as any));
  expect(allowed).toBe(false);
  expect(routerSpy.navigateByUrl).toHaveBeenCalledWith('/login');
});
```

## What to test, in priority order

You cannot test everything. Roughly, invest in this order:

1. **State transitions in stores.** These are pure and easy to test, and they encode most of the business logic. `toggle` before / after; `add` when API succeeds and when it fails.
2. **User-visible behavior of critical components.** "Clicking submit adds the task." Do not test private methods; test what a user or another component observes.
3. **Guards and resolvers.** They gate access; a bug here has security consequences.
4. **Pipes with non-trivial logic.** Test the branches.
5. **A handful of end-to-end journeys.** Sign in, do the main action, sign out. Not every feature, just the ones whose failure would page you at 3 AM.

Skip the trivial. Do not test that `TaskList` sets `title = 'Tasks'`. Do not test the CLI-generated boilerplate.

## Continuous integration, briefly

Every test in `.spec.ts` runs with `ng test`. In CI, run it headless:

```bash
ng test --browsers=ChromeHeadlessNoSandbox --watch=false
```

Playwright:

```bash
npx playwright test
```

Compass's CI pipeline (Chapter 19 revisits deployment):

- Install: `npm ci`
- Lint: `ng lint`
- Type-check + unit test: `ng test --watch=false`
- Build: `ng build --configuration production`
- E2E: `npx playwright test`

If all pass, deploy.

## What comes next

Chapter 18 covers server-side rendering and hydration — the technique that gives your users their first paint before Angular has finished booting. Then Chapter 19 deploys Compass to the internet, and Chapter 20 sends you off with a plan for staying current.

### Exercises

1. Write a spec for `TaskStore.toggle` that covers the optimistic-update happy path and the reverting-on-failure path. Verify with the API spy that the store called `update` exactly once and, on failure, the tasks signal returned to its previous shape.

2. Write a component harness for `TaskRow`. Methods: `getTitle`, `isDone`, `clickToggle`, `clickDetails`. Use it in a test that verifies clicking the toggle emits the `toggled` output with the row's id.

3. Set up Playwright for Compass. Write one end-to-end test that starts on the home page, adds a new task, refreshes the browser, and asserts the task is still there. This confirms the full stack (frontend + json-server) is wired correctly.
