# פרק 3. JavaScript מודרני שבאמת תשתמש בו

Angular היא TypeScript מבחוץ ו-JavaScript מבפנים. כל מה שהקומפיילר מייצר, הדפדפן מריץ. אם קטע של תחביר JavaScript ייראה לא מוכר בדוגמת Angular בהמשך הספר, הסיכוי הוא שהיא אחת מהתכונות בפרק הזה. יש עוד עשרות שלא נכסה — שפת JavaScript המודרנית גדולה מאוד — אבל תת-הקבוצה כאן היא בערך מאה אחוז ממה שקוד יישום Angular באמת משתמש בו.

אם כתבת JavaScript עדכני קודם, אתה יכול לקרוא את הפרק הזה כרשימת בדיקה ולעבור במהירות מעל מה שאתה כבר יודע. אם לא, תכנן לנסות כל דוגמה בקונסולת הפיתוח של דפדפן (פתח את הדפדפן שלך, לחץ F12, לחץ על "Console") כדי שהתחביר יגיע לאצבעות שלך.

## מודולים: `import` ו-`export`

כל קובץ בפרויקט JavaScript או TypeScript מודרני הוא *מודול*. מודול הוא קובץ שיכול *לייצא* דברים (פונקציות, מחלקות, קבועים, טיפוסים) לקבצים אחרים לשימוש, ו*לייבא* דברים ממודולים אחרים. זה המנגנון שבאמצעותו האפליקציה שלך מפוצלת לקבצים בלי לזהם namespace גלובלי.

יש שני טעמים של ייצוא:

```ts
// tasks.ts

// ייצוא בשם: מייצא סמל תחת שמו שלו.
export interface Task {
  id: string;
  title: string;
}

export function isOverdue(task: Task): boolean { /* ... */ return false; }

// ייצוא ברירת מחדל: אחד לקובץ, מיובא בלי סוגריים מסולסלים.
export default class TaskService {
  // ...
}
```

ובמקביל, שני טעמים של ייבוא:

```ts
// app.ts

import TaskService from "./tasks";          // ברירת מחדל
import { Task, isOverdue } from "./tasks";  // בשם
import * as tasks from "./tasks";           // הכל, עם namespace
```

מדריך הסגנון של Angular, והספר הזה, מעדיפים *ייצוא בשם* כמעט תמיד. ייצוא ברירת מחדל חוסך זוג סוגריים אבל עולה בבהירות: השם של ייצוא ברירת מחדל באתר הייבוא הוא מה שהמייבא מקליד, כך ש-`import Foo from "./bar"` ו-`import Baz from "./bar"` מתייחסים לאותו דבר. ייצוא בשם שומר על השמות ישרים לרוחב הקוד.

נתיבי ייבוא שמתחילים ב-`./` או `../` הם *יחסיים* — הם מצביעים על קובץ אחר בפרויקט שלך. נתיבים שמתחילים בכל דבר אחר הם *מזהים חשופים* ומתייחסים לחבילות מותקנות (`@angular/core`, `rxjs`, וכן הלאה).

> **שים לב.** אל תשים את הסיומת `.ts` בייבואים שלך (`from "./tasks.ts"`). כלי הבנייה של Angular מטפל בסיומת עבורך. בסביבות JavaScript אחרות — בעיקר Node.js במצב ESM — אתה *כן* צריך את הסיומת. Angular הוא המקרה הראשון, לא השני.

## פונקציות חץ

פונקציית חץ היא דרך קצרה יותר לכתוב פונקציה, עם הבדל סמנטי חשוב אחד מפונקציה רגילה: אין לה `this` משלה.

```ts
// טופס ארוך
const isDone = function(task) { return task.done; };

// חץ, גוף בלוק
const isDone = (task) => { return task.done; };

// חץ, גוף ביטוי — בלי סוגריים, בלי מילת מפתח return
const isDone = task => task.done;

// מספר פרמטרים דורש סוגריים
const compare = (a, b) => a.priority - b.priority;
```

היעדר `this` משלה חשוב כשאתה מעביר פונקציית חץ כ-callback:

```ts
class TaskService {
  tasks: Task[] = [];

  loadTasks() {
    fetch("/api/tasks")
      .then(res => res.json())
      .then(data => {
        // `this` כאן עדיין מתייחס למופע של TaskService,
        // כי פונקציית החץ יורשת אותו מ-loadTasks.
        this.tasks = data;
      });
  }
}
```

אם ה-callback הפנימי היה `function` רגיל, `this` בתוכו היה `undefined` (במצב strict) או האובייקט הגלובלי — מקור באגים שהציק ל-JavaScript עשור לפני שחצים הגיעו. בקוד Angular, כמעט תמיד תרצה חצים ל-callbacks.

## Template literals

מחרוזות בגרשי קונטרס-אקצנט יכולות להכיל ביטויים אינטרפולציה ולהתפרש על פני מספר שורות:

```ts
const name = "Anna";
const greeting = `Hello, ${name}. Today is ${new Date().toDateString()}.`;
```

הן טובות באופן מוחלט מקישור מחרוזות לכל דבר ארוך יותר מטריוויאלי. תבניות Angular עצמן הן template literals כשאתה כותב תבניות inline:

```ts
@Component({
  template: `
    <h1>Welcome, {{ user.name }}</h1>
    <p>You have {{ taskCount() }} tasks today.</p>
  `,
})
```

ה-`{{ }}` בפנים הוא תחביר התבנית של Angular, לא של JavaScript `${}`. הם חיים יחד כי הם אף פעם לא חופפים: הליטרל החיצוני הוא JavaScript, מוערך פעם אחת כשמחלקת הקומפוננטה מוגדרת; ה-`{{ }}` הוא של Angular, מוערך מחדש כשהנתונים משתנים.

## Destructuring

Destructuring שולף שדות מאובייקט (או אלמנטים ממערך) לתוך משתנים בשמות בביטוי יחיד.

```ts
const task = { id: "t1", title: "Buy milk", done: false };

// במקום:
const id = task.id;
const title = task.title;

// אתה יכול לכתוב:
const { id, title } = task;
```

אתה יכול לתת שם חדש בדרך החוצה ולספק ברירות מחדל:

```ts
const { id: taskId, title, done = false } = task;
```

Destructuring עובד גם בפרמטרים של פונקציה:

```ts
function label({ title, done }: Task): string {
  return done ? `[x] ${title}` : `[ ] ${title}`;
}

label({ id: "t1", title: "Buy milk", done: false, /* ... */ });
```

Destructuring של מערכים משתמש באותו רעיון עם סוגריים מרובעים:

```ts
const [first, second, ...rest] = [1, 2, 3, 4, 5];
// first = 1, second = 2, rest = [3, 4, 5]
```

ה-`...rest` בשורה האחרונה הוא אופרטור spread/rest, שנסתכל עליו הבא.

## Spread ו-rest

לאופרטור שלוש-הנקודות `...` יש שני שימושים קשורים.

**Spread** מרחיב את האלמנטים של מערך (או את המאפיינים של אובייקט) inline:

```ts
const priorities = [1, 2, 3];
const withZero = [0, ...priorities];        // [0, 1, 2, 3]

const base = { title: "Untitled", done: false };
const withId = { ...base, id: "t1" };       // { title, done, id }
```

Spread של אובייקט הוא איך שאתה יוצר עותק רדוד של אובייקט, ואיך שאתה מייצר עותק ששונה בלי לשנות את המקור:

```ts
const task: Task = { /* ... */ };
const updated = { ...task, done: true };
// task.done עדיין מה שהיה; updated.done הוא true.
```

הדפוס הזה של "אל תשנה; ייצר אובייקט חדש" הוא *ה*דפוס של קוד ריאקטיבי מודרני ב-Angular. כשנגיע לסיגנלים בפרק 7, תראה אותו כל הזמן.

**Rest** אוסף את האלמנטים הנותרים של מערך או את הפרמטרים הנותרים של פונקציה למשתנה יחיד:

```ts
function sum(first: number, ...others: number[]): number {
  return others.reduce((acc, n) => acc + n, first);
}

sum(1, 2, 3, 4);   // 10
```

אותן שלוש נקודות, כיוון הפוך: spread מרחיב, rest אוסף.

## פרמטרים ברירת מחדל

לפרמטרים יכולות להיות ברירות מחדל, וברירות המחדל יכולות להתייחס לפרמטרים קודמים:

```ts
function paginate(items: Task[], page: number, size: number = 20): Task[] {
  return items.slice(page * size, (page + 1) * size);
}

paginate(all, 0);        // משתמש ב-size = 20
paginate(all, 0, 50);    // משתמש ב-size = 50
```

פרמטרי ברירת מחדל נכנסים לפעולה כשהארגומנט הוא `undefined` — העברת `null` *לא* מפעילה את ברירת המחדל. שווה לזכור את זה בפעם הראשונה שזה מפתיע אותך.

## שרשור אופציונלי ו-nullish coalescing

שני אופרטורים שהחליפו בשקט הרבה שרשראות `if` הגנתיות.

**שרשור אופציונלי** — `?.` — מחזיר `undefined` בקצר-מסלול אם הצד השמאלי הוא `null` או `undefined`, במקום לזרוק:

```ts
const city = user?.address?.city;
// שווה ל:
const city2 = user && user.address ? user.address.city : undefined;
```

**Nullish coalescing** — `??` — מחזיר את הצד הימני אם הצד השמאלי הוא `null` או `undefined`, אחרת את הצד השמאלי:

```ts
const display = user.nickname ?? user.name ?? "Anonymous";
```

ההבחנה החשובה מ-`||` (שאולי ראית משמש באופן דומה) היא ש-`??` נופל דרך רק על `null` ו-`undefined`, לא על ערכים falsy אחרים. `0 || 10` נותן לך 10; `0 ?? 10` נותן לך 0. ב-Compass, `task.priority ?? 3` הוא "ברירת מחדל בטוחה של עדיפות ל-3 אם לא מוגדרת", בעוד `task.priority || 3` היה שוגה ומעדכן עדיפות מכוונת של 0.

## Promises

**Promise** הוא ערך שיהיה קיים בעתיד. כל פעולה שלוקחת זמן — בקשת רשת, קריאת קובץ, טיימר — מחזירה Promise. Promise נמצא תמיד באחד משלושה מצבים: *ממתין* (עדיין ממתין), *ממומש* (הפיק ערך), או *נדחה* (הפיק שגיאה).

אתה מצמיד callbacks עם `.then()` ו-`.catch()`:

```ts
fetch("/api/tasks")
  .then(res => res.json())
  .then(tasks => console.log(tasks))
  .catch(err => console.error("Something went wrong:", err));
```

כל `.then` מקבל את הערך שהשלב הקודם החזיר. אם שלב כלשהו זורק או מחזיר Promise שנדחה, השליטה קופצת ל-`.catch` הקרוב ביותר.

סגנון ה"שרשרת של thens" הזה היה פעם הדרך הסטנדרטית לכתוב קוד אסינכרוני. הוא עובד, ומנגנון ה-HTTP הבסיסי של Angular עדיין משתמש ב-Promises במקומות, אבל הארגונומיה מסורבלת ברגע שהשרשרת גדלה. קוד מודרני משתמש ב-`async`/`await` במקום.

## `async` / `await`

`async` מסמן פונקציה כמחזירה Promise, ומאפשר לך להשתמש ב-`await` בתוכה. `await` משהה את הפונקציה בביטוי הזה עד שה-Promise שממתין נפתר, ואז מתחדש עם הערך שלו.

```ts
async function loadTasks(): Promise<Task[]> {
  const res = await fetch("/api/tasks");
  const tasks: Task[] = await res.json();
  return tasks;
}

// בהמשך:
const tasks = await loadTasks();
```

שגיאות ב-Promises שממתינים יוצאות כחריגות שנזרקות, כך שאתה יכול להשתמש ב-`try`/`catch` רגיל:

```ts
try {
  const tasks = await loadTasks();
} catch (err) {
  console.error("Could not load tasks:", err);
}
```

`async`/`await` היא דרך נחמדה יותר לכתוב את אותו החישוב ששרשרת של `.then()`ים מבטאת — אבל זה *אותו החישוב*. שום דבר לא רץ סינכרונית. `await` עדיין מוותר על שליטה לדפדפן בין שלבים. זה תחביר סוכר, וזה טעים.

> **הערה.** Angular משתמשת לפעמים ב-Promises, לפעמים ב-*Observables* (טיפוס RxJS), ויותר ויותר בסיגנלים למצב ריאקטיבי. פרק 11 פורק את ההבדל בין Promises ל-Observables — לעת עתה, החשוב הוא שתבין Promises, כי כל השאר בעולם האסינכרוני בונה עליהם או מחליף אותם.

## שיטות מערך שתשתמש בהן כל הזמן

שיטות המערך של JavaScript המודרני הן ארגז הכלים של קוד יישום יומיומי. תישען עליהן בכל יום.

```ts
const tasks: Task[] = /* ... */;

// map: הפוך כל אלמנט
const titles = tasks.map(t => t.title);

// filter: שמור את האלמנטים שתואמים
const active = tasks.filter(t => !t.done);

// find: קבל את האלמנט הראשון שתואם, או undefined
const buyMilk = tasks.find(t => t.title === "Buy milk");

// some / every: בדוק את המערך כמכלול
const anyOverdue = tasks.some(isOverdue);
const allDone = tasks.every(t => t.done);

// reduce: קפל את המערך לערך יחיד
const total = tasks.reduce((sum, t) => sum + (t.done ? 1 : 0), 0);

// includes: האם המערך מכיל את הערך?
const hasWork = tags.includes("work");

// sort: משנה! בדרך כלל תרצה להעתיק קודם
const byPriority = [...tasks].sort((a, b) => a.priority - b.priority);
```

שלוש אזהרות לגבי `sort` וחבריה:

1. `sort`, `reverse`, ו-`splice` משנים את המערך במקום. אם אתה רוצה מערך חדש ממוין בלי להפריע למקורי, פזר אותו קודם: `[...tasks].sort(...)`.
2. `sort` בלי פונקציית השוואה מכפה אלמנטים למחרוזות, שזה מקור באגים אגדי. מיונים מספריים *דורשים* פונקציית השוואה: `.sort((a, b) => a - b)`.
3. `reduce` חזקה ומופרזת בשימוש. אם אתה מוצא את עצמך כותב `reduce` שיכול להיות לולאת `for` עם שני משתנים, לולאת `for` בדרך כלל בהירה יותר.

## לולאות `for`

יש לך שלוש דרכים עיקריות לעבור באיטרציה:

```ts
// for..of עובר על ערכים במערך או ב-iterable
for (const task of tasks) {
  console.log(task.title);
}

// forEach בסדר לתופעות לוואי; לא ניתן לצאת ממנו
tasks.forEach(task => console.log(task.title));

// for קלאסי עדיין שימושי כשהאינדקס חשוב
for (let i = 0; i < tasks.length; i++) {
  console.log(`${i}: ${tasks[i].title}`);
}
```

`for..in` גם קיים אבל עובר על *מפתחות של אובייקט*, לא על אלמנטים של מערך. מאחר שלמערכים יש מפתחות מחרוזתיים ("0", "1", ...), `for..in` יעשה דברים מפתיעים על מערכים. העדף `for..of` למערכים ו-`Object.keys(obj)` / `Object.entries(obj)` לאובייקטים.

## אובייקטים והעתקות רדודות

העתקת אובייקטים היא מקום שמתחילים נשרפים בו. הקצאה לא מעתיקה; היא יוצרת התייחסות חדשה לאותו אובייקט.

```ts
const original = { title: "Buy milk", done: false };
const alias = original;
alias.done = true;
console.log(original.done);  // true — הפתעה
```

כדי להעתיק, השתמש ב-spread (או ב-`Object.assign`):

```ts
const copy = { ...original };
copy.done = true;
console.log(original.done);  // עדיין false
```

זו העתקה *רדודה*: אובייקטים מקוננים עדיין משותפים. אם באובייקט שלך יש אובייקטים מקוננים ואתה צריך עותק עמוק, השתמש ב-`structuredClone(value)` (מובנה בדפדפנים מודרניים).

## מחלקות, בקצרה

Angular היא class-forward: קומפוננטות, שירותים, דירקטיבות ופייפים הן כולן מחלקות. אתה לא צריך ללמוד הכל על מחלקות היום — פרק 5 יעשה זאת — אבל התחביר לא מפתיע:

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

מילת המפתח `private` היא של TypeScript, לא של JavaScript — בזמן ריצה השדה נגיש, אבל הקומפיילר יסרב לתת לקוד חיצוני לגעת בו. ל-JavaScript המודרני יש גם שדות פרטיים אמיתיים `#`; קוד הבסיס של Angular משתמש ב-`private` של TypeScript לפי מוסכמה, אז גם אנחנו.

## מה דילגנו עליו במכוון

Generators (`function*`), הטיפוס `Symbol`, `Proxy`, `Reflect`, `Map` ו-`Set` (תפגוש את אלה כשהם עוזרים), ביטויים רגולריים בפירוט, ורבות מהעדינויות של `this`. כולם שימושיים; אף אחד מהם לא נדרש כדי לבנות את Compass. כשתפגוש אחד מהם, חפש אותו ב-MDN — Mozilla Developer Network היא הפניה הקנונית ל-JavaScript.

## מה בא הלאה

פרק 4 מכניס אותך לאפליקציית Angular רצה. תתקין את Node.js, תתקין את ה-CLI של Angular, תריץ `ng new compass`, ותעבור סיור איטי על כל קובץ שה-CLI מייצר. עד סוף פרק 4, יהיה לך מסך התחלה של Angular פתוח בדפדפן שלך ותבין מה כל חלק ממה שיצר אותו עושה.

### תרגילים

1. בהינתן `const nums = [3, 1, 4, 1, 5, 9, 2, 6]`, השתמש בשיטות מערך כדי לייצר (א) מערך של ריבועים, (ב) סכום הריבועים, (ג) המספר הגדול ביותר, ו-(ד) האם כל מספר קטן מ-10. כתוב כל אחד כביטוי יחיד.

2. כתוב פונקציה `updateTask(tasks: Task[], id: string, changes: Partial<Task>): Task[]` שמחזירה מערך חדש שבו למשימה עם ה-id התואם `changes` ממוזג לתוכה, וכל משימה אחרת נשארת ללא שינוי. השתמש ב-`map` וב-spread; אל תשנה את הקלט. (הטיפוס `Partial<Task>` פירושו "כל שדות של Task, אבל כל אחד אופציונלי".)

3. המר את שרשרת ה-Promise הזאת ל-`async`/`await`:

```ts
function loadWithAuth(): Promise<Task[]> {
  return fetch("/api/session")
    .then(res => res.json())
    .then(session => fetch("/api/tasks", { headers: { Authorization: session.token } }))
    .then(res => res.json());
}
```

אז חשוב מה קורה אם ה-`fetch` הראשון נכשל. איפה השגיאה עולה על פני השטח בכל גרסה?
