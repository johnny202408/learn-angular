# Chapter 2. TypeScript enough for Angular

This chapter is a working knowledge of TypeScript, written for people who have not used it before and do not want to become full-time TypeScript scholars. By the end you will be able to read every TypeScript expression the rest of the book uses, and write your own without guessing. You will not, and should not, know everything TypeScript can do. Its type system is deep enough to have its own bookshelf; we are not visiting that bookshelf today.

The examples in this chapter are motivated by Compass. Every time we introduce a new TypeScript feature, we will show it with a shape you will later have in your app: a task, a habit, a user, a completion event. That way, by the time we start writing Angular components in Chapter 5, the types will already feel familiar.

## Why types at all

If you have written a small script in a language like Python or plain JavaScript, you probably wrote something like this:

```js
function totalMinutes(sessions) {
  let sum = 0;
  for (const s of sessions) sum += s.duration;
  return sum;
}
```

This works. It also gives you no help. Somewhere else in the program, a colleague passes you an array of *strings* by mistake, or an object that spells the field `durationMinutes` instead of `duration`. The function still runs; it produces `NaN` or `"0[object Object]"` or something else surreal, and by the time you notice, you are hunting through the output for the source of the weirdness.

TypeScript adds a small amount of ceremony to prevent that hunt. You annotate what a function expects; the TypeScript compiler checks every place that function is called; if a caller violates the contract, you find out immediately, before the code runs. In an editor, this manifests as a red squiggle under the offending line and a specific message about what is wrong. In a build, it stops the build.

The same function in TypeScript:

```ts
interface Session {
  duration: number;
}

function totalMinutes(sessions: Session[]): number {
  let sum = 0;
  for (const s of sessions) sum += s.duration;
  return sum;
}
```

Now the compiler knows: the function takes an array of things that each have a `duration` field which is a number, and returns a number. Pass it anything else and TypeScript objects. There is nothing magic about this — the compiler is just checking that names and shapes agree — but the payoff in a codebase larger than one file is substantial. Angular is built to lean on that payoff.

## Running TypeScript, in one paragraph

TypeScript is not something browsers run directly. A tool called the TypeScript compiler (`tsc`) reads `.ts` files, checks the types, and produces plain JavaScript files that a browser (or Node.js) can run. In Angular projects, you almost never invoke `tsc` yourself; the Angular CLI runs it as part of `ng serve` and `ng build`. For this chapter, if you want to try TypeScript in isolation, use the online **TypeScript Playground** at `typescriptlang.org/play` — it lets you type TypeScript on the left and see the compiled JavaScript on the right, no installation required. From Chapter 4 onward, the CLI takes over.

## The primitives

TypeScript's basic types are `string`, `number`, `boolean`, `null`, and `undefined`. There are others, but these are the ones you will type a hundred times a day.

```ts
let title: string = "Buy milk";
let priority: number = 2;
let done: boolean = false;
let due: string | null = null; // more on the "|" in a moment
```

TypeScript is smart about inferring types when you assign a value at the point of declaration:

```ts
let title = "Buy milk";  // inferred as string
```

You do not need to write `: string` when the value already tells TypeScript what the variable holds. In practice, you annotate types on *function parameters and return types*, on *object shapes*, and on things you're going to assign to later; you leave everything else to inference. A codebase that annotates every trivial `let` is a codebase full of noise.

> **Note.** `null` and `undefined` are distinct in TypeScript, as they are in JavaScript. Angular tends to prefer `null` for "we know there's no value here" and reserves `undefined` for "the value was never set." A field that is *optional* is one that might be `undefined`; a field that is *nullable* is one that is present but might be `null`. It is a subtle distinction that will matter in Chapter 12 when we talk about forms.

## Arrays and tuples

An array's type is `Type[]`, or equivalently `Array<Type>`:

```ts
const priorities: number[] = [1, 2, 3];
const tags: string[] = ["home", "work"];
```

Empty arrays need an annotation because there is nothing to infer from:

```ts
const completed: string[] = [];   // fine
const uh = [];                    // inferred as any[], which you don't want
```

Tuples are fixed-length, position-typed arrays. You will use them rarely in application code:

```ts
const point: [number, number] = [42, 7];
```

## Object types with `interface`

The bread and butter of TypeScript in an Angular application is describing the shape of objects. TypeScript offers two ways to do this — `interface` and `type` — and for object shapes they are almost interchangeable. Use `interface` for object shapes; use `type` for unions, intersections, and things that are not just an object.

Here is Compass's central type, as it will appear in Chapter 5:

```ts
interface Task {
  id: string;
  title: string;
  done: boolean;
  createdAt: string;    // ISO 8601 date
  dueDate: string | null;
  tags: string[];
}
```

A value that claims to be a `Task` must have all six of these fields, with these types. Extra fields are an error (in most contexts). Missing fields are an error. Wrong types are an error. This shape becomes a contract that every part of the app can rely on.

### Optional properties, readonly, and index signatures

You will meet three annotations that modify how a field behaves.

```ts
interface Habit {
  id: string;
  name: string;
  color?: string;                // may be undefined
  readonly createdAt: string;    // cannot be reassigned after construction
  metadata: { [key: string]: string };  // arbitrary string→string map
}
```

`color?: string` means the field is optional; a value satisfying `Habit` need not include it, and if it is there it may be `string` or `undefined`. `readonly` prevents reassignment through this type — helpful for id-like fields that must never be mutated in place. The last form, `{ [key: string]: string }`, is called an *index signature*; it says "any string key maps to a string value" and is useful for open-ended dictionaries.

## Union types and literal types

A *union* type is a value that could be one of several types. You saw one already: `string | null`. Unions are constrained "or"s: this value is *either* a string *or* the value `null`.

Unions of literal strings are one of TypeScript's most useful patterns:

```ts
type Status = "todo" | "doing" | "done" | "archived";

interface Task {
  id: string;
  title: string;
  status: Status;
}
```

Now `status` cannot be an arbitrary string; it must be exactly one of those four. Try to write `task.status = "in-progress"` and TypeScript will refuse. This is how you enforce a closed set of options — a poor person's enum, and in most cases the better choice.

> **Watch out.** TypeScript does have an `enum` keyword, and Angular's early years used it heavily. Modern practice is to prefer union types of string literals. `enum` compiles into runtime JavaScript objects, which bloat your bundle; union types compile into nothing (they exist only at type-check time). Chapter 5 uses unions throughout.

## Type narrowing

If a variable has a union type, TypeScript will *narrow* it inside a branch of code where it can tell what the value actually is:

```ts
function greeting(name: string | null): string {
  if (name === null) {
    return "Hello, stranger.";
  }
  // Here, TypeScript knows name is string, not string | null.
  return `Hello, ${name}.`;
}
```

The three most common narrowing patterns:

- `typeof x === "string"` narrows `x` to `string`.
- `x === null` or `x === undefined` narrows through `if`s.
- `"field" in x` narrows to the subset of a union that has that field.
- `x instanceof Foo` narrows to `Foo`.

Narrowing is one of the features that makes TypeScript feel like it is *helping* rather than fighting. If TypeScript ever says "possibly undefined" and you know it isn't, the answer is almost always to check with an `if`, not to bypass the check.

## Functions

Function types annotate parameters and, optionally, return types:

```ts
function isOverdue(task: Task, now: Date): boolean {
  if (task.dueDate === null) return false;
  return new Date(task.dueDate) < now;
}
```

Arrow functions work the same way:

```ts
const isOverdue = (task: Task, now: Date): boolean => {
  if (task.dueDate === null) return false;
  return new Date(task.dueDate) < now;
};
```

If TypeScript can infer the return type from the body, you can omit the annotation — but it is good practice to annotate return types on exported functions, because it forces you to think about what a function actually promises to return.

Function parameters can be optional or have defaults:

```ts
function label(task: Task, prefix?: string): string {
  return `${prefix ?? ""}${task.title}`;
}

function paginate<T>(items: T[], page: number, size = 20): T[] {
  return items.slice(page * size, (page + 1) * size);
}
```

The second example uses a *generic*, which we look at next.

## Generics, gently

A generic is a type parameter — a placeholder for "some type we will fill in at the call site." The classic use is a function that works over any array without losing type information:

```ts
function first<T>(items: T[]): T | undefined {
  return items[0];
}

first([1, 2, 3]);            // T is number; returns number | undefined
first(["a", "b"]);           // T is string; returns string | undefined
```

The name `T` is convention. Use single letters for very general parameters (`T`, `U`, `K`, `V`), or descriptive names when clarity helps (`<Item>`, `<Payload>`).

You will see generics constantly in Angular. `signal<Task[]>([])` creates a signal holding an array of `Task`. `HttpClient.get<Task[]>('/api/tasks')` tells the compiler what shape to expect back from the server. In each case, the generic is the answer to "what type is inside the thing?"

Do not write your own generic functions when you are learning. Reach for them the third or fourth time you copy-paste a function and only change its types. Until then, plain typed functions are almost always the right tool.

## Type inference is your friend

TypeScript is aggressive about inferring types, and you should let it. Consider:

```ts
const tasks = tasksFromServer();          // inferred as Task[]
const titles = tasks.map(t => t.title);   // inferred as string[]
const activeCount = tasks.filter(t => !t.done).length;  // inferred as number
```

No annotations were needed — TypeScript walked through the whole chain and figured it out. The general rule: annotate the *inputs* and *outputs* of your public functions, and let TypeScript infer everything else.

## `any`, `unknown`, and the honest escape hatches

Sometimes you truly do not know the type of a value — you have just parsed some JSON off the wire, or you are calling into an old library with no types. TypeScript has two escape hatches:

- **`any`** turns off type checking for that value. Anything goes. This is dangerous; if you write `any` you are signing away every benefit of using TypeScript for that piece of data.
- **`unknown`** is the safe alternative. A value of type `unknown` can be anything, but you cannot do anything *with* it until you narrow it to a specific type first.

```ts
function parseTask(raw: unknown): Task {
  if (typeof raw !== "object" || raw === null) {
    throw new Error("Not an object");
  }
  const r = raw as { id?: unknown; title?: unknown; /* ... */ };
  if (typeof r.id !== "string" || typeof r.title !== "string") {
    throw new Error("Missing required fields");
  }
  // ...more checks...
  return { id: r.id, title: r.title, done: false, createdAt: "", dueDate: null, tags: [] };
}
```

Reach for `unknown` at the boundary of your app — parsing JSON, reading `localStorage`, dealing with untyped libraries. Reach for `any` almost never.

## Decorators, briefly

Angular relies heavily on *decorators* — functions written with an `@` prefix that attach metadata to a class or its members. You will see them constantly:

```ts
@Component({
  selector: "app-task-row",
  template: `<div>{{ task.title }}</div>`,
})
export class TaskRow {
  @Input() task!: Task;
}
```

For now, know only this: `@Component`, `@Input`, `@Output`, and their friends are how you tell Angular "this class is a component" or "this field is an input from a parent." Chapter 5 will explain what each does. TypeScript's role is simply to allow the syntax; the meaning is Angular's.

> **Note.** Decorators are officially standardized in modern JavaScript now, but Angular still uses the older *experimental* decorator flavor because it carries more metadata that Angular relies on. The Angular CLI configures your project so this Just Works; you should never have to think about it. If you ever see `experimentalDecorators` in a `tsconfig.json`, that is why.

## The `!` and `?` operators

Two small TypeScript-only sigils will appear often:

- `x!` is the *non-null assertion*. It tells the compiler "trust me, this is not null or undefined here." Use it sparingly; every `!` is a place where a runtime error can appear that the type system does not warn about. In component code, `@Input() task!: Task` uses `!` to promise "Angular will assign this before I use it," which is a promise Angular does keep — but only after component construction, not during it.
- `x?.y` is the *optional chaining* operator (which is actually plain JavaScript). It returns `undefined` if `x` is `null` or `undefined`, instead of throwing. `x?.y ?? "default"` combines it with the *nullish coalescing* operator we will meet in Chapter 3.

## What we deliberately skipped

TypeScript has conditional types, mapped types, template literal types, `infer`, discriminated unions in their full generality, and a hundred other tools. You will encounter some of them, mostly in error messages, and you will be tempted to dive down that rabbit hole. Resist. The features in this chapter are the ones you will use every single day in Angular. The rest is available when you need it.

## What comes next

Chapter 3 covers the modern JavaScript features Angular assumes you know: modules, arrow functions, destructuring, spread and rest, `async`/`await`, and the array methods you will lean on constantly. If you have already written recent JavaScript, you can skim it; if not, take it slow — Chapter 4 will assume every idea from Chapter 3.

### Exercises

1. Write an interface `Habit` with these fields: `id` (string), `name` (string), `frequency` (one of `"daily"`, `"weekly"`, `"custom"`), `color` (optional string), `createdAt` (a `readonly` string). Then write a function `describe(habit: Habit): string` that returns something like `"Read (daily)"`.

2. Given `type Result<T> = { ok: true; value: T } | { ok: false; error: string }`, write a function `unwrap<T>(r: Result<T>): T` that returns the value if `ok` is true and throws otherwise. Try to write it with narrowing rather than an `as` assertion.

3. In the Playground (`typescriptlang.org/play`), paste an object of shape `{ title: "test", priority: "high" }` and try to assign it to a variable of type `{ title: string; priority: number }`. Read the error message carefully. Then fix the object so it type-checks. Understanding this error format is a skill worth having.
