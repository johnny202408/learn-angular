# פרק 8. הרכבת קומפוננטות

אפליקציית Angular אמיתית היא לא קומפוננטה גדולה אחת; היא עץ של קטנות. לכל אחת יש עבודה צרה, ויחד הן מתחברות למסך. הרכבה היא מה שגורם לאפליקציה להיות ניתנת לתחזוקה — אתה יכול לשנות שם, להחליף, או להשתמש שוב בכל קומפוננטה בלי לגעת בשאר — והיא מה שמאפשר לקוד לגדול מעבר לכמה אלפי שורות בלי להפוך לביצה.

בפרק הזה אנחנו מפצלים את הקומפוננטה `TaskList` של Compass לשלוש: רשימה, שורות משימה בודדות, וטופס להוספת משימה. תוך כדי כך אנחנו מכסים את כלי ההרכבה: `input()` להעברת נתונים למטה, `output()` לשליחת אירועים למעלה, `model()` ל-two-way binding, והזרקת תוכן להכנסת תוכן שרירותי בתוך קומפוננטת container.

עד הסוף, Compass ייראה ויתנהג בדיוק כמו עכשיו — אבל הוא יהיה מובנה כמו אפליקציות Angular ששורדות מגע עם צוותים אמיתיים.

## איך הרכבה נראית

כרגע, `TaskList` הוא הבעלים של הכל: המערך של המשימות, מצב ה-draft של ה-input, ההיגיון של add ו-toggle, וכל התבנית שמרנדרת טופס ושורות. זה בסדר למאה שורות. זה נכשל בעשרת אלפים.

אנחנו הולכים לפצל אותו:

- **`TaskRow`** — מרנדר משימה אחת. הוא מקבל `task` כ-input ופולט אירוע כשהמשתמש מעביר אותה.
- **`AddTaskForm`** — מרנדר את ה-input ואת כפתור Add. הוא פולט אירוע כשהמשתמש שולח כותרת חדשה.
- **`TaskList`** — בעלים של מערך המשימות ומתאם בין שני החלקים. הוא הופך קצר וקריא.

החלוקה הזאת של "container / הצגה" היא הדרך הכי נפוצה להבנות קומפוננטות Angular. ה-container יודע על מצב ומתאם את החלקים; קומפוננטות ההצגה יודעות רק על מה שהן מרנדרות ואילו אירועים הן פולטות. קומפוננטות הצגה נוטות להיות קטנות, טהורות, קלות לבדיקה, וקלות לשימוש חוזר.

## העברת נתונים למטה: `input()`

פגשנו בקצרה את `input()` בפרק 7. כאן אנחנו משתמשים בו ברצינות.

צור את `TaskRow` עם ה-CLI:

```bash
ng generate component task-row
```

ערוך את `src/app/task-row/task-row.ts`:

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

שלושה דברים לשים לב:

- **`task = input.required<Task>()`** מכריז שהקומפוננטה הזאת מקבלת input נדרש מסוג `Task`. אם הורה שוכח להעביר אחד, הקומפיילר של התבנית מתלונן.
- **`toggled = output<string>()`** מכריז על אירוע שהקומפוננטה הזאת יכולה לפלוט. פרמטר הטיפוס הוא הטיפוס של ה-payload — אנחנו פולטים את ה-id של המשימה.
- **`isOverdue` הוא סיגנל computed** שתלוי ב-`task()`. כי `task` הוא סיגנל בעצמו, בכל פעם שההורה מעביר ערך חדש, `isOverdue` מחושב מחדש.

התבנית, ב-`task-row.html`:

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

שים לב ל-`task().title` — אתה קורא signal input בדיוק כמו כל סיגנל אחר, עם `()`. התבנית חוזרת על `task()` כמה פעמים; זו קריאה זולה (סיגנלים במטמון), ויותר נקייה מלהקצות למשתנה מקומי קודם.

וגם `task-row.css`:

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

השורה עכשיו היא דבר עצמאי שאתה יכול להשליט לכל מקום.

## שליחת אירועים למעלה: `output()`

`output()` מייצר משהו עם מתודת `emit(value)`. קריאה לה יורה את האירוע על הקומפוננטה; ההורה מקשיב עם התחביר `(name)="handler($event)"`.

כבר כתבנו את `this.toggled.emit(this.task().id)` בתוך `TaskRow`. הורה ירשם עם:

```html
<app-task-row [task]="t" (toggled)="toggle($event)" />
```

`$event` ב-handler הוא מה שהועבר ל-`emit(...)` — כאן, מחרוזת ה-id של המשימה. TypeScript זורם דרך הטיפוס, כך שהמתודה `toggle` של ההורה תקבל `string` מוקלד.

`output()` מחליף את הדפוס הישן יותר של `@Output() eventEmitter = new EventEmitter<T>()`. שניהם עדיין עובדים; קוד חדש משתמש ב-`output()`.

## הוספת הטופס: `AddTaskForm`

צור אותו:

```bash
ng generate component add-task-form
```

ערוך את `src/app/add-task-form/add-task-form.ts`:

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

תבנית `add-task-form.html`:

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

סגנון, `add-task-form.css`:

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

`AddTaskForm` בעלים של מצב ה-draft שלו (הקלדת המשתמש בתהליך). הוא פולט אירוע `add` עם הכותרת הסופית כשהמשתמש שולח. ההורה לא צריך לדעת או להיות אכפת לו איך הטופס עובד — הוא מתחבר לשני חוזים: הפלט `add`, והתג `<app-add-task-form>`.

## `TaskList` המעוצב מחדש

עכשיו `TaskList` הופך קצר. החלף את המחלקה שלו ב:

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
    /* משימות התחלתיות ללא שינוי מפרק 7 */
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

והתבנית `task-list.html`:

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

שמור. האפליקציה נראית זהה. כל פיסת התנהגות ללא שינוי. אבל עכשיו:

- ניתן להשתמש שוב ב-`TaskRow` בכל מקום שמשימה צריכה לרנדר.
- ניתן להשתמש שוב ב-`AddTaskForm` בכל מקום שאתה צריך לאסוף כותרת.
- `TaskList` הוא חמש-עשרה שורות של תיאום.

זו הצורה של אפליקציית Angular.

## Two-way עם `model()`

`model()` נותן לך זוג input-output עם קישור `[(name)]`, ארוזים כסיגנל אחד. הוא שימושי כשילד הוא בעלים של *חלק* מפיסת מצב משותפת — המקרה הקלאסי הוא input טקסט כמו זה שרק בנינו.

נניח שרצינו ש-`AddTaskForm` יחשוף את ה-`draft` שלו להורה לתצוגה חיצונית. יכולנו לעשות את זה ידנית עם output; `model()` עושה את זה בשורה אחת.

שכתב את `add-task-form.ts`:

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

עכשיו הורה יכול לעשות:

```html
<app-add-task-form [(draft)]="currentDraft" (add)="onAdd($event)" />
```

כל שינוי מכל צד משתקף בשני. אם ההורה לא אכפת לו מה-draft, הוא יכול פשוט להעביר handler של `(add)` ולדלג על `[(draft)]`. `model()` נותן לך אופציונליות שזוג input/output שנעשה ידנית לא נותן.

לעת עתה, `TaskList` לא צריך לראות את ה-draft — התבנית הנוכחית משמיטה `[(draft)]` והכל עובד. שקול `model()` כשאתה מוצא את עצמך כותב זוגות של inputs ו-outputs ששמותיהם רק היו מוסיפים "Change" אחד לשני.

## הזרקת תוכן: `<ng-content>`

חלק מהקומפוננטות לא מוגדרות על ידי הנתונים שהן מקבלות, אלא על ידי *התוכן שהן עוטפות*. חלון מודאלי, כרטיס, סעיף מתקפל — כל אחד הוא מכל שהפנים שלו ממולא על ידי המזמין שלו. הכלי של Angular לזה הוא *הזרקת תוכן*, דרך האלמנט `<ng-content>`.

הנה קומפוננטת `Card`:

```ts
@Component({
  selector: 'app-card',
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

הורה משתמש בו כך:

```html
<app-card title="Today">
  <p>Three tasks remaining.</p>
  <button>Refresh</button>
</app-card>
```

מה שיופיע בין `<app-card>` ו-`</app-card>` בתבנית של ההורה מסתיים איפה ש-`<ng-content>` יושב בתבנית של הילד. זה מאפשר לקומפוננטה אחת להגדיר פריסה בזמן שהמזמינים ממלאים תוכן.

### חריצים בשמות

אם ל-container יש מספר נקודות הכנסה, השתמש ב-attribute `select`:

```html
<!-- בתוך SplitCard -->
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

ההורה מתייג כל פיסה של תוכן כדי לנתב אותה לחריץ:

```html
<app-split-card>
  <p left>Left column content.</p>
  <p right>Right column content.</p>
  <footer>Footer content.</footer>
</app-split-card>
```

תוכן שלא תואם לאף `select` הולך ל-`<ng-content>` רגיל אם יש אחד, או נזרק אחרת.

הזרקת תוכן היא איך שאתה בונה מערכות עיצוב: כרטיסים, דיאלוגים, טאבים, wrappers של טבלאות. Compass ישתמש בה בפרק 15 כשנציג קומפוננטת "מצב ריק" משותפת.

## גישה לילדים: `viewChild` ו-`viewChildren`

לפעמים הורה צריך להושיט יד *לתוך* ילד — למקד input, להפעיל מתודה, לקרוא פיסת מצב שלא נחשפת דרך output. Angular מציעה `viewChild()` ו-`viewChildren()` לזה.

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

`viewChild('searchInput')` מחזיר סיגנל שהערך שלו הוא כל אלמנט או קומפוננטה שתאם ל-reference התבנית `#searchInput`. אתה קורא אותו עם `()` כמו כל סיגנל; הוא עשוי להיות `undefined` אם האלמנט עדיין לא מרונדר.

`viewChild` הוא מוצא אחרון. אם אתה מוצא את עצמך פונה אליו, שאל קודם: האם זה יכול להיעשות עם input, output, או סיגנל? תשע פעמים מתוך עשר, זה יכול. המקרה של אחת מתוך עשר בדרך כלל כולל APIs אימפרטיביים של דפדפן (focus, scroll, נגינת `<video>`).

## הנחיות לפיצול קומפוננטות

מתי לפצל קומפוננטה אחת לשתיים? סימנים:

- התבנית ארוכה יותר ממסך. אם אתה גולל כדי לקרוא אותה, יהיה לך קושי לתחזק אותה.
- שני סעיפים ויזואליים נבדלים אין להם מה לעשות אחד עם השני. "כותרת" ו"רשימה" באותה קומפוננטה כמעט תמיד צריכים להיות קומפוננטות נפרדות.
- אתה עומד להעתיק-להדביק חתיכה של מרקאפ לשימוש שני. חלץ קודם.
- למחלקה יש יותר מכעשרה שדות. חלקם כנראה על תת-דאגה.

מתי *לא* לפצל? כשהחלקים חסרי משמעות בפני עצמם. "כותרת של שורת משימה" היא לא קומפוננטה; היא `<span>`. "שורת משימה שיש לה גם כפתור מחיקה ותג באיחור" היא קומפוננטה. המבחן: האם אתה יכול לדמיין שימוש בקומפוננטה הזאת במקום אחר, או בדיקה שלה בבידוד? אם כן, חלץ. אם לא, השאר.

## מה בא הלאה

חלק שלישי מתחיל בפרק 9 על *הזרקת תלויות* — המנגנון שיאפשר לנו למשוך את נתוני המשימות מ-`TaskList` לתוך שירות שקומפוננטות אחרות יכולות לשתף. פרק 10 מחבר את השירות הזה לבקאנד HTTP; פרק 11 מציג RxJS לחלקים של האפליקציה שבהם סיגנלים לא מספיקים; פרק 12 מחליף את הטופס שנעשה ידנית בטפסים ריאקטיביים.

עד סוף חלק שלישי, Compass ידבר עם שרת אמיתי, ישמור את המשימות שאתה מוסיף, ויפסיק לאבד את העבודה שלך כשאתה מרענן.

### תרגילים

1. חלץ קומפוננטה `TaskCount` שמציגה "3 tasks left" ומקבלת `total` ו-`done` כ-inputs. חשב את המספר "left" בתוך הקומפוננטה עם `computed`. השתמש בה ב-`TaskList` במקום הטקסט הנוכחי של הכותרת.

2. הוסף כפתור מחיקה ל-`TaskRow`. הוא צריך לפלוט output `deleted` עם ה-id של המשימה. חבר את `TaskList` להסיר משימות באירוע הזה. אל תיתן ללחיצה על כפתור המחיקה גם לירות את ה-toggle; השתמש ב-`$event.stopPropagation()` ב-handler הלחיצה.

3. בנה קומפוננטה `Panel` עם הזרקת תוכן: container עם כותרת, חריץ body, וחריץ actions אופציונלי. התבנית שלו צריכה להיות בערך `<div class="panel">` `<header>{{ title() }} <ng-content select="[actions]"/></header>` `<div class="body"><ng-content/></div>` `</div>`. השתמש בה כדי לעטוף את רשימת המשימות — העבר "Today" ככותרת וכפתור "Clear completed" בחריץ ה-actions.
