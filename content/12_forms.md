# Chapter 12. Forms: capturing user input reliably

Compass has one input right now: the "Add task" field. It works because it is trivial. Real applications have forms with multiple fields, validation rules, cross-field constraints, async checks, and complicated submit behavior. Trying to hand-roll all of that with `(input)` bindings the way we did in Chapter 6 is possible; it also loses more of an afternoon per form than it should.

Angular has two form systems: *template-driven forms* and *reactive forms*. They are not equivalent. Reactive forms are more powerful, more testable, and better-typed. This book uses reactive forms exclusively. Template-driven forms exist and have their fans; if you inherit an older codebase full of `ngModel`, know that it works and that Chapter 20's ecosystem tour will point you at resources for the older style.

In this chapter we replace the Chapter 6 "Add task" input with a reactive form, then build an edit dialog for tasks that lets the user change the title, set a due date, and tag it.

## Setting up

Reactive forms come from `@angular/forms`. Register the necessary providers by importing the `ReactiveFormsModule` directives in any component that uses them. Each standalone component that hosts a form imports what it needs:

```ts
import { FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  imports: [ReactiveFormsModule],
  // ...
})
```

`ReactiveFormsModule` is a bundle of directives — `formGroup`, `formControl`, `formControlName`, and so on. Templates that reference these directives must import the module.

## `FormControl`, `FormGroup`, `FormArray`

The three primitives of reactive forms.

**`FormControl<T>`** wraps a single value. It knows its current value, its validation state, whether the user has touched or blurred it, and it emits changes.

```ts
const title = new FormControl('', { nonNullable: true, validators: [Validators.required] });

title.value;          // ''
title.setValue('Buy milk');
title.valueChanges;   // Observable<string>
title.valid;          // boolean
title.errors;         // { required: true } or null
```

`nonNullable: true` is important. Without it, `title.value` has type `string | null`, and calling `.reset()` sets the control back to `null`. With `nonNullable: true`, the value is always `string`, and reset restores the initial value ('' here). Use it on almost every control.

**`FormGroup`** is a collection of named controls.

```ts
const form = new FormGroup({
  title: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  dueDate: new FormControl<string | null>(null),
  tag: new FormControl('', { nonNullable: true }),
});

form.value;            // { title: string, dueDate: string | null, tag: string }
form.valid;
form.get('title')?.setValue('...');
```

The form is *typed*: `form.value` has an inferred type derived from the shape of the controls. This is the reactive-forms feature that most changed the game in Angular 14 — before, form values were all `any`, and typos in template `formControlName` would silently break.

**`FormArray`** is a dynamic list of controls of the same shape. Useful for repeating rows: "add another tag," "add another author." We will use it later in this chapter for tags.

## `FormBuilder` is nicer

Constructing forms with `new FormControl(...)` is verbose. `FormBuilder` is a small helper service injected via DI:

```ts
private fb = inject(FormBuilder);

form = this.fb.nonNullable.group({
  title: ['', Validators.required],
  dueDate: [null as string | null],
  tag: [''],
});
```

`fb.nonNullable.group(...)` makes every control non-nullable by default. `fb.group(...)` (without `nonNullable`) uses the older nullable defaults. Prefer `fb.nonNullable`.

Each entry is `[initialValue, validators]`. Validators can be a single function or an array.

## Rebuilding "Add task" with reactive forms

Open `src/app/add-task-form/add-task-form.ts`. Replace it with:

```ts
import { Component, inject, output } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-add-task-form',
  imports: [ReactiveFormsModule],
  templateUrl: './add-task-form.html',
  styleUrl: './add-task-form.css',
})
export class AddTaskForm {
  private fb = inject(FormBuilder);
  add = output<string>();

  form = this.fb.nonNullable.group({
    title: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(120)]],
  });

  submit(): void {
    if (this.form.invalid) return;
    this.add.emit(this.form.getRawValue().title.trim());
    this.form.reset();
  }
}
```

Template:

```html
<form [formGroup]="form" (ngSubmit)="submit()">
  <input
    type="text"
    formControlName="title"
    placeholder="What needs doing?" />
  <button type="submit" [disabled]="form.invalid">Add</button>
</form>

@if (form.controls.title.touched && form.controls.title.invalid) {
  <p class="error">
    @if (form.controls.title.hasError('required')) { Title is required. }
    @if (form.controls.title.hasError('minlength')) { At least two characters, please. }
    @if (form.controls.title.hasError('maxlength')) { Please keep it under 120 characters. }
  </p>
}
```

Save. It works exactly like before, but:

- **The form's shape is enforced by TypeScript.** If you mistype `formControlName="titel"`, the template compiler tells you.
- **Validation is centralized.** No more `disabled` computation in the template — it reads `form.invalid`.
- **Errors have names.** Different messages for different constraints, without special-casing lengths in the template.
- **`.reset()` is one call.** No more manually clearing a signal.

`ngSubmit` (with no dollar sign in front) is a directive that catches form submissions and calls `submit()`, and it prevents the default browser reload. You no longer need `$event.preventDefault()`.

## Built-in validators

The `Validators` object exports the common cases:

```ts
Validators.required
Validators.requiredTrue           // for checkboxes
Validators.min(0)
Validators.max(100)
Validators.minLength(3)
Validators.maxLength(200)
Validators.pattern(/^[a-z0-9-]+$/i)
Validators.email
```

For anything else, write a validator by hand. A validator is a function `(control) => errors | null`.

```ts
function noWhitespace(control: AbstractControl): ValidationErrors | null {
  const v = (control.value ?? '').trim();
  return v.length === 0 ? { whitespace: true } : null;
}

new FormControl('', [Validators.required, noWhitespace]);
```

The error object's keys become entries in `control.errors`, which the template can check with `hasError('whitespace')`.

## An edit dialog: `FormGroup` and `FormArray` together

Compass will need to let the user edit a task: change the title, set or clear the due date, and manage the list of tags. This is a real form: a `FormGroup` with a nested `FormArray`.

Create it:

```bash
ng generate component edit-task
```

`edit-task.ts`:

```ts
import { Component, inject, input, output } from '@angular/core';
import {
  FormArray, FormBuilder, FormControl, FormGroup,
  ReactiveFormsModule, Validators
} from '@angular/forms';
import { Task } from '../task';

@Component({
  selector: 'app-edit-task',
  imports: [ReactiveFormsModule],
  templateUrl: './edit-task.html',
  styleUrl: './edit-task.css',
})
export class EditTask {
  task = input.required<Task>();
  saved = output<Partial<Task>>();
  cancelled = output<void>();

  private fb = inject(FormBuilder);

  form = this.fb.nonNullable.group({
    title: ['', [Validators.required, Validators.minLength(2)]],
    dueDate: [null as string | null],
    tags: this.fb.array<FormControl<string>>([]),
  });

  constructor() {
    // Populate the form when task changes.
    this.setFromTask();
  }

  private setFromTask(): void {
    const t = this.task();
    this.form.patchValue({
      title: t.title,
      dueDate: t.dueDate,
    });
    const tagsArray = this.form.controls.tags;
    tagsArray.clear();
    for (const tag of t.tags) {
      tagsArray.push(this.fb.nonNullable.control(tag, Validators.required));
    }
  }

  addTag(): void {
    this.form.controls.tags.push(
      this.fb.nonNullable.control('', Validators.required)
    );
  }

  removeTag(index: number): void {
    this.form.controls.tags.removeAt(index);
  }

  submit(): void {
    if (this.form.invalid) return;
    const raw = this.form.getRawValue();
    this.saved.emit({
      title: raw.title.trim(),
      dueDate: raw.dueDate,
      tags: raw.tags,
    });
  }

  cancel(): void {
    this.cancelled.emit();
  }
}
```

And a template that binds a `FormArray`:

```html
<form [formGroup]="form" (ngSubmit)="submit()" class="edit-task">
  <label>
    Title
    <input type="text" formControlName="title" />
  </label>

  <label>
    Due date
    <input type="date" formControlName="dueDate" />
  </label>

  <fieldset>
    <legend>Tags</legend>
    <div formArrayName="tags" class="tags">
      @for (control of form.controls.tags.controls; track $index; let i = $index) {
        <div class="tag-row">
          <input type="text" [formControlName]="i" />
          <button type="button" (click)="removeTag(i)">Remove</button>
        </div>
      }
    </div>
    <button type="button" (click)="addTag()">Add tag</button>
  </fieldset>

  <div class="actions">
    <button type="button" (click)="cancel()">Cancel</button>
    <button type="submit" [disabled]="form.invalid">Save</button>
  </div>
</form>
```

Two directives are new:

- `formArrayName="tags"` binds a container to a `FormArray`.
- Inside it, `formControlName="0"`, `"1"`, etc., bind each child to its slot. Using `[formControlName]="i"` with a template variable does this cleanly.

The form now supports adding and removing tags on the fly, with each tag validated individually. The typed form gives us `form.controls.tags.controls` as `FormControl<string>[]`, and TypeScript knows that `raw.tags` is `string[]`.

## Async validators, briefly

Occasionally validation needs to hit the server: "is this username available?" Async validators are functions that return an Observable or Promise of `ValidationErrors | null`.

```ts
function uniqueTitle(api: TasksApi): AsyncValidatorFn {
  return control => {
    if (!control.value) return of(null);
    return timer(300).pipe(
      switchMap(() => api.check(control.value)),
      map(taken => (taken ? { unique: true } : null))
    );
  };
}

// In the form:
title: ['', {
  validators: [Validators.required],
  asyncValidators: [uniqueTitle(this.api)],
}],
```

The `timer(300)` is a manual debounce so we don't spam the server on every keystroke. `form.pending` is `true` while the async validator is running — bind it in the template to show a spinner.

We will not add unique-title validation to Compass — tasks with duplicate names are fine — but you now know where to reach.

## `valueChanges` and reacting to form input

Every control and group has a `valueChanges` Observable:

```ts
this.form.controls.title.valueChanges
  .pipe(takeUntilDestroyed())
  .subscribe(v => console.log('title now:', v));
```

Or, converted to a signal:

```ts
titleValue = toSignal(this.form.controls.title.valueChanges, {
  initialValue: this.form.controls.title.value,
});
```

Both work. Reach for `toSignal` when you want the form's live state to drive `computed` derivations or effects.

For the common case of "when this control changes, run this side effect," use `valueChanges` with `takeUntilDestroyed` and don't reach for signals unless the effect happens to belong in a computed.

## Cross-field validation

Sometimes validity depends on more than one control. A due date must be after "start date"; a confirm-password must match a password. Add a validator to the group, not the controls.

```ts
form = this.fb.nonNullable.group({
  password: ['', Validators.required],
  confirm: ['', Validators.required],
}, {
  validators: (group) => {
    const p = group.get('password')?.value;
    const c = group.get('confirm')?.value;
    return p === c ? null : { mismatch: true };
  },
});
```

Read it in the template as `form.errors?.['mismatch']`.

## When to use template-driven forms

The short answer: on tiny forms where reactive forms are ceremony overkill. A single search input, a single toggle, a one-off checkbox: `[(ngModel)]` is fine. Anything with multiple fields, validation across them, or programmatic manipulation should be reactive.

The book uses reactive forms throughout because they scale from tiny to huge without changing paradigm. When you inherit an older Angular codebase and see `ngForm`, `ngModel`, `ngModelGroup`, you will be able to read it; you probably will not want to write new features in that style.

## Wiring `EditTask` into `TaskList`

We won't build the full modal experience in this chapter — routing to a detail page is Chapter 13's job. For now, add a temporary "edit" mode to `TaskList` that shows the form under a selected row.

```ts
export class TaskList {
  private store = inject(TaskStore);
  tasks = this.store.tasks;
  editingId = signal<string | null>(null);
  editing = computed(() => this.tasks().find(t => t.id === this.editingId()));

  onEdit(id: string): void { this.editingId.set(id); }
  onCancel(): void { this.editingId.set(null); }
  onSaved(changes: Partial<Task>): void {
    const id = this.editingId();
    if (id) this.store.applyChanges(id, changes);
    this.editingId.set(null);
  }
}
```

(You will need to add `applyChanges` to `TaskStore`. It calls `TasksApi.update` and applies the returned task to the signal, with optimistic revert on failure — very similar to `toggle`.)

Template:

```html
@let e = editing();
@if (e) {
  <app-edit-task
    [task]="e"
    (saved)="onSaved($event)"
    (cancelled)="onCancel()" />
}
```

That is enough plumbing to prove the form works end-to-end. Chapter 13 turns this into a proper edit route.

## What comes next

Part IV. Compass is now a working single-screen app: it fetches, adds, edits, and saves tasks against a real backend. Chapter 13 adds routing — a home screen, a stats page, a task detail view with the edit form — and Chapter 14 promotes `TaskStore` from a single service into a proper signal-based state layer that other stores can follow. Chapter 15 refactors reusable UI into directives and pipes; Chapter 16 makes Compass fast on a phone.

### Exercises

1. Add a `notes` field to `EditTask` — a `<textarea>` with `maxLength(1000)` validation. Show the remaining character count under the field, driven by `toSignal(form.controls.notes.valueChanges)`.

2. Convert the "Add task" form to include an optional due date. When the user submits, the due date should be sent to `TaskStore.add` along with the title. Update `TaskStore.add` to accept and store it.

3. Wire an async validator into the "Add task" form that prevents duplicate titles: if the current tasks array already has a task with the same trimmed title, mark the control invalid with a `{ duplicate: true }` error. You don't need HTTP for this — read the store's `tasks()` signal directly inside the validator using `computed`.
