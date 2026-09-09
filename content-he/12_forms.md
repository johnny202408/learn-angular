# פרק 12. טפסים: תפיסת קלט משתמש באופן אמין

ל-Compass יש input אחד עכשיו: השדה "Add task". הוא עובד כי הוא טריוויאלי. יישומים אמיתיים יש להם טפסים עם שדות מרובים, כללי ולידציה, מגבלות חוצות-שדות, בדיקות אסינכרוניות, והתנהגות submit מסובכת. לנסות לעשות את כל זה ידנית עם קישורי `(input)` בדרך שעשינו בפרק 6 אפשרי; זה גם מפסיד יותר משעה של אחר צהריים לטופס משמה שצריך.

ל-Angular יש שתי מערכות טפסים: *טפסים מונעי-תבנית* ו*טפסים ריאקטיביים*. הם לא שווי ערך. טפסים ריאקטיביים חזקים יותר, ניתנים לבדיקה יותר, ומוקלדים טוב יותר. הספר הזה משתמש בטפסים ריאקטיביים באופן בלעדי. טפסים מונעי-תבנית קיימים ויש להם מעריצים; אם אתה יורש קוד ישן יותר מלא ב-`ngModel`, דע שהוא עובד ושהסיור האקוסיסטמי של פרק 20 יכוון אותך למקורות לסגנון הישן יותר.

בפרק הזה אנחנו מחליפים את ה-input "Add task" של פרק 6 בטופס ריאקטיבי, ואז בונים דיאלוג עריכה למשימות שמאפשר למשתמש לשנות את הכותרת, להגדיר תאריך יעד, ולתייג אותה.

## הכנה

טפסים ריאקטיביים באים מ-`@angular/forms`. רשום את ה-providers הנדרשים על ידי ייבוא הדירקטיבות של `ReactiveFormsModule` בכל קומפוננטה שמשתמשת בהן. כל קומפוננטה עצמאית שמארחת טופס מייבאת מה שהיא צריכה:

```ts
import { FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  imports: [ReactiveFormsModule],
  // ...
})
```

`ReactiveFormsModule` הוא חבילה של דירקטיבות — `formGroup`, `formControl`, `formControlName`, וכן הלאה. תבניות שמתייחסות לדירקטיבות האלה חייבות לייבא את המודול.

## `FormControl`, `FormGroup`, `FormArray`

שלושת הפרימיטיבים של טפסים ריאקטיביים.

**`FormControl<T>`** עוטף ערך יחיד. הוא יודע את הערך הנוכחי שלו, את מצב הולידציה שלו, אם המשתמש נגע בו או הוציא ממנו פוקוס, והוא פולט שינויים.

```ts
const title = new FormControl('', { nonNullable: true, validators: [Validators.required] });

title.value;          // ''
title.setValue('Buy milk');
title.valueChanges;   // Observable<string>
title.valid;          // boolean
title.errors;         // { required: true } או null
```

`nonNullable: true` חשוב. בלעדיו, ל-`title.value` יש טיפוס `string | null`, וקריאה ל-`.reset()` מגדירה את הבקרה בחזרה ל-`null`. עם `nonNullable: true`, הערך הוא תמיד `string`, ו-reset משחזר את הערך ההתחלתי ('' כאן). השתמש בו כמעט על כל בקרה.

**`FormGroup`** היא אוסף של בקרות בשמות.

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

הטופס *מוקלד*: ל-`form.value` יש טיפוס שנגזר מהצורה של הבקרות. זו התכונה של טפסים ריאקטיביים שהכי שינתה את המשחק ב-Angular 14 — לפני, ערכי טופס היו כולם `any`, ושגיאות הקלדה ב-`formControlName` של תבנית היו נשברות בשקט.

**`FormArray`** היא רשימה דינמית של בקרות באותה צורה. שימושי לשורות חוזרות: "הוסף עוד תגית", "הוסף עוד סופר". נשתמש בה מאוחר יותר בפרק הזה עבור תגיות.

## `FormBuilder` הוא יותר נחמד

בניית טפסים עם `new FormControl(...)` היא מפורטת. `FormBuilder` הוא עוזר קטן שירות מוזרק דרך DI:

```ts
private fb = inject(FormBuilder);

form = this.fb.nonNullable.group({
  title: ['', Validators.required],
  dueDate: [null as string | null],
  tag: [''],
});
```

`fb.nonNullable.group(...)` הופך כל בקרה ל-non-nullable כברירת מחדל. `fb.group(...)` (בלי `nonNullable`) משתמש בברירות המחדל הישנות שניתן לנול. העדף את `fb.nonNullable`.

כל רשומה היא `[initialValue, validators]`. Validators יכולים להיות פונקציה יחידה או מערך.

## בנייה מחדש של "Add task" עם טפסים ריאקטיביים

פתח את `src/app/add-task-form/add-task-form.ts`. החלף אותו ב:

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

תבנית:

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

שמור. זה עובד בדיוק כמו קודם, אבל:

- **צורת הטופס נאכפת על ידי TypeScript.** אם תקליד לא נכון `formControlName="titel"`, הקומפיילר של התבנית אומר לך.
- **הולידציה מרוכזת.** אין יותר חישוב `disabled` בתבנית — היא קוראת `form.invalid`.
- **לשגיאות יש שמות.** הודעות שונות למגבלות שונות, בלי לטפל במקרים מיוחדים של אורכים בתבנית.
- **`.reset()` היא קריאה אחת.** אין יותר ניקוי ידני של סיגנל.

`ngSubmit` (בלי סימן דולר לפניו) היא דירקטיבה שתופסת הגשות טפסים וקוראת ל-`submit()`, והיא מונעת את הטעינה מחדש ברירת המחדל של הדפדפן. אתה לא צריך יותר `$event.preventDefault()`.

## Validators מובנים

האובייקט `Validators` מייצא את המקרים הנפוצים:

```ts
Validators.required
Validators.requiredTrue           // עבור תיבות סימון
Validators.min(0)
Validators.max(100)
Validators.minLength(3)
Validators.maxLength(200)
Validators.pattern(/^[a-z0-9-]+$/i)
Validators.email
```

לכל דבר אחר, כתוב validator ידנית. Validator הוא פונקציה `(control) => errors | null`.

```ts
function noWhitespace(control: AbstractControl): ValidationErrors | null {
  const v = (control.value ?? '').trim();
  return v.length === 0 ? { whitespace: true } : null;
}

new FormControl('', [Validators.required, noWhitespace]);
```

המפתחות של אובייקט השגיאה הופכים לרשומות ב-`control.errors`, שהתבנית יכולה לבדוק עם `hasError('whitespace')`.

## דיאלוג עריכה: `FormGroup` ו-`FormArray` יחד

Compass יצטרך לאפשר למשתמש לערוך משימה: לשנות את הכותרת, להגדיר או לנקות את תאריך היעד, ולנהל את רשימת התגיות. זה טופס אמיתי: `FormGroup` עם `FormArray` מקונן.

צור אותו:

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
    // מלא את הטופס כשמשימה משתנה.
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

ותבנית שקושרת `FormArray`:

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

שתי דירקטיבות חדשות:

- `formArrayName="tags"` קושר container ל-`FormArray`.
- בתוכו, `formControlName="0"`, `"1"`, וכן הלאה, קושרים כל ילד לחריץ שלו. השימוש ב-`[formControlName]="i"` עם משתנה תבנית עושה זאת בצורה נקייה.

הטופס עכשיו תומך בהוספה והסרה של תגיות מהזבוב, כשכל תגית מאומתת בנפרד. הטופס המוקלד נותן לנו `form.controls.tags.controls` כ-`FormControl<string>[]`, ו-TypeScript יודעת ש-`raw.tags` היא `string[]`.

## Validators אסינכרוניים, בקצרה

מדי פעם ולידציה צריכה להגיע לשרת: "האם שם המשתמש הזה זמין?" Validators אסינכרוניים הם פונקציות שמחזירות Observable או Promise של `ValidationErrors | null`.

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

// בטופס:
title: ['', {
  validators: [Validators.required],
  asyncValidators: [uniqueTitle(this.api)],
}],
```

ה-`timer(300)` הוא debounce ידני כדי שלא נציף את השרת בכל הקלדה. `form.pending` הוא `true` בזמן שה-validator האסינכרוני רץ — קשור אותו בתבנית כדי להראות spinner.

לא נוסיף ולידציה של כותרת ייחודית ל-Compass — משימות עם שמות כפולים בסדר — אבל אתה עכשיו יודע לאן לפנות.

## `valueChanges` ותגובה לקלט טופס

לכל בקרה וקבוצה יש Observable `valueChanges`:

```ts
this.form.controls.title.valueChanges
  .pipe(takeUntilDestroyed())
  .subscribe(v => console.log('title now:', v));
```

או, מומר לסיגנל:

```ts
titleValue = toSignal(this.form.controls.title.valueChanges, {
  initialValue: this.form.controls.title.value,
});
```

שניהם עובדים. פנה ל-`toSignal` כשאתה רוצה שהמצב החי של הטופס יניע נגזרים של `computed` או אפקטים.

למקרה הנפוץ של "כשהבקרה הזאת משתנה, הרץ את תופעת הלוואי הזאת", השתמש ב-`valueChanges` עם `takeUntilDestroyed` ואל תפנה לסיגנלים אלא אם תופעת הלוואי במקרה שייכת ל-computed.

## ולידציה חוצת שדות

לפעמים תוקף תלוי ביותר מבקרה אחת. תאריך יעד חייב להיות אחרי "תאריך התחלה"; אישור-סיסמה חייב להתאים לסיסמה. הוסף validator לקבוצה, לא לבקרות.

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

קרא אותו בתבנית כ-`form.errors?.['mismatch']`.

## מתי להשתמש בטפסים מונעי-תבנית

התשובה הקצרה: בטפסים זעירים שבהם טפסים ריאקטיביים הם טקסי יתר. input חיפוש יחיד, מתג יחיד, תיבת סימון חד-פעמית: `[(ngModel)]` בסדר. כל דבר עם שדות מרובים, ולידציה ביניהם, או מניפולציה תוכניתית צריך להיות ריאקטיבי.

הספר משתמש בטפסים ריאקטיביים לאורך כי הם מתרחבים מזעיר לענק בלי לשנות פרדיגמה. כשתירש קוד Angular ישן יותר ותראה `ngForm`, `ngModel`, `ngModelGroup`, תוכל לקרוא אותו; כנראה לא תרצה לכתוב פיצ'רים חדשים בסגנון הזה.

## חיווט `EditTask` לתוך `TaskList`

לא נבנה את חוויית המודאל המלאה בפרק הזה — ניתוב לדף פירוט הוא העבודה של פרק 13. לעת עתה, הוסף מצב "עריכה" זמני ל-`TaskList` שמראה את הטופס מתחת לשורה נבחרת.

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

(תצטרך להוסיף `applyChanges` ל-`TaskStore`. הוא קורא ל-`TasksApi.update` ומחיל את המשימה שהוחזרה על הסיגנל, עם חזרה אופטימית על כישלון — מאוד דומה ל-`toggle`.)

תבנית:

```html
@let e = editing();
@if (e) {
  <app-edit-task
    [task]="e"
    (saved)="onSaved($event)"
    (cancelled)="onCancel()" />
}
```

זה מספיק צנרת כדי להוכיח שהטופס עובד מקצה לקצה. פרק 13 הופך את זה למסלול עריכה ראוי.

## מה בא הלאה

חלק רביעי. Compass היא עכשיו אפליקציה עובדת של מסך אחד: היא שולפת, מוסיפה, עורכת, ושומרת משימות מול בקאנד אמיתי. פרק 13 מוסיף ניתוב — מסך בית, עמוד סטטיסטיקות, תצוגת פירוט משימה עם טופס העריכה — ופרק 14 מקדם את `TaskStore` משירות יחיד לשכבת מצב מבוססת סיגנלים ראויה שחנויות אחרות יכולות לעקוב אחריה. פרק 15 מעצב מחדש UI לשימוש חוזר לדירקטיבות ולפייפים; פרק 16 גורם ל-Compass להיות מהיר בטלפון.

### תרגילים

1. הוסף שדה `notes` ל-`EditTask` — `<textarea>` עם ולידציית `maxLength(1000)`. הצג את מספר התווים הנותרים מתחת לשדה, מונע על ידי `toSignal(form.controls.notes.valueChanges)`.

2. המר את הטופס "Add task" לכלול תאריך יעד אופציונלי. כשהמשתמש שולח, תאריך היעד צריך להישלח ל-`TaskStore.add` יחד עם הכותרת. עדכן את `TaskStore.add` לקבל ולשמור אותו.

3. חבר validator אסינכרוני לטופס "Add task" שמונע כותרות כפולות: אם מערך המשימות הנוכחי כבר יש בו משימה עם אותה כותרת מנוקה, סמן את הבקרה כלא תקינה עם שגיאת `{ duplicate: true }`. אתה לא צריך HTTP לזה — קרא את הסיגנל `tasks()` של החנות ישירות בתוך ה-validator באמצעות `computed`.
