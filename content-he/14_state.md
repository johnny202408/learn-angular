# פרק 14. מצב מעבר לקומפוננטה אחת

`TaskStore` היה צעד ראשון טוב. הוא עובד כי ל-Compass יש סוג אחד של נתונים. יישומים אמיתיים יש להם רבים — משימות, הרגלים, משתמשים, הגדרות, טיוטות, העלאות, התראות — והם מתקשרים. ברגע שכמה חנויות צריכות לחלוק ערכים או להגיב זו לזו, אתה צריך *דפוס*, לא שירות חכם אחד.

הפרק הזה משטח את הדפוס הזה. אנחנו ממירים את שירותי המצב המזדמנים של Compass לצורה קטנה ועקבית. אנחנו גם מכסים מתי לפנות לספריות גדולות יותר — במיוחד NgRx SignalStore ו-NgRx הקלאסי (Redux ל-Angular) — ואיך לזהות.

הפרק הזה הוא על עיצוב, אז יש בו פחות קוד ויותר החלטות מאשר בכמה האחרונים. קרא אותו לאט.

## הצגת הבעיה

עד סוף Compass, יהיו לנו לפחות פיסות המצב האלה:

- **משימות** — מערך, נטען מהשרת, ניתן לשינוי על ידי המשתמש.
- **הרגלים** — אותה צורה.
- **משתמש** — המשתמש המחובר כרגע (פרק 19).
- **מצב UI** — איזו משימה נבחרה, איזה מסנן פעיל, איזה פאנל פתוח, איזו ערכת נושא נבחרה.
- **תור offline** — מוטציות שנכשלו וצריכות ניסיון חוזר כשהחיבור חוזר.

חלק מאלה מגובים על ידי שרת. חלק לגמרי מקומיים. חלק נקראים על ידי שתי קומפוננטות על המסך; חלק נקראים על ידי רבות לרוחב האפליקציה.

אתה רוצה שלשכבת המצב תהיה צורה עקבית כדי שמישהו שקורא את Compass בעוד שישה חודשים לא יצטרך ללמוד מחדש איך כל פיסה עובדת. אתה גם לא רוצה להציג כל כך הרבה מכניקה שפיסה זעירה של מצב תעלה חמישים שורות של טקסים.

## הדפוס: `Store` לכל דאגה

הדפוס שהספר הזה משתמש בו הוא פשוט ומרחיב יותר ממה שמתחילים מצפים. עבור כל דאגת דומיין, יש לך מחלקת Injectable אחת — קרא לה Store — שהיא בעלים של מספר קטן של סיגנלים פרטיים, חושפת סיגנלים לקריאה בלבד לקריאות, וחושפת מתודות למוטציות.

התבנית היא בערך:

```ts
@Injectable({ providedIn: 'root' })
export class SomeStore {
  private readonly _state = signal<State>(initialState);
  readonly state = this._state.asReadonly();

  readonly derivedA = computed(() => /* ... */);
  readonly derivedB = computed(() => /* ... */);

  method1(input): void { this._state.update(s => /* ... */); }
  async method2(input): Promise<void> {
    // עבודה אולי אסינכרונית; עדכונים אופטימיים; טיפול בשגיאות
  }
}
```

זה `TaskStore` מפרק 10, מתואר גנרית. שני מאפיינים גורמים לזה להתרחב:

- **כותב אחד לכל סיגנל.** רק המתודות של החנות עצמה כותבות ל-`_state`. קוראים לעולם לא עוקפים. זה גורם למוטציות להיות ניתנות לחיפוש ולבדיקה.
- **תצוגות לקריאה בלבד.** ה-`state` הציבורי הוא סיגנל לקריאה בלבד. צרכנים לא יכולים לשנות אותו בטעות. ערכי `computed` הם כבר לקריאה בלבד לפי בנייה.

הוסף `HabitStore` עם אותה צורה. הוסף `UserStore`. ל-Compass יש עכשיו שלוש חנויות, כל אחת בערך מאה שורות, כל אחת עוקבת אחר אותה תבנית. קוראים חדשים תופסים אותן מיד.

## מצב מקומי (UI) לעומת מצב משותף

לא כל פיסת מצב שייכת ל-Store. שתי שאלות מחליטות.

**האם יותר מקומפוננטה אחת קוראת את המצב הזה?** אם לא, שמור אותו בקומפוננטה. סיגנלים בתוך קומפוננטה הם ריאקטיביים בדיוק כמו סיגנלים בתוך שירות. העברתם לשירות כדי להיות "נקי" פוגעת בקריאות בלי לעזור לשום דבר.

**האם המצב הזה צריך לשרוד כשהקומפוננטה הזאת מושמדת?** אם לא, שמור אותו בקומפוננטה. טיוטת טופס, UI מקומי של מודאל, דגל טעינה מקומי לקומפוננטה — כולם שייכים לקומפוננטה.

הקו המפריד בדרך כלל ברור. ה-`editingId` של `TaskList` בפרק 12 מקומי לקומפוננטה — הוא לא שורד את הקומפוננטה הנעלמת. ה-`tasks` של `TaskStore` משותף וחיים ארוכים. שניהם סיגנלים; רק אחד בשירות.

## אינטראקציה בין-חנויות

לפעמים חנות אחת צריכה להגיב לאחרת. כשהמשתמש מתנתק, כל מצב המשימות וההרגלים צריך להתנקות. כשהרגל נמחק, המשימות שהתייחסו אליו צריכות שהתגיות שלהן יעודכנו.

הדפוס הנקי לזה: השתמש ב-`effect` בחנות התלויה. הוא קורא סיגנלים מהחנות שהוא תלוי בה, ומגיב.

```ts
@Injectable({ providedIn: 'root' })
export class TaskStore {
  private userStore = inject(UserStore);

  constructor() {
    effect(() => {
      const user = this.userStore.currentUser();
      if (user === null) {
        this._tasks.set([]);
      }
    });
  }
}
```

כללים:

- **תלה למטה, אף פעם לא במעגל.** `TaskStore` שתלוי ב-`UserStore` בסדר. `UserStore` שתלוי ב-`TaskStore` הוא באג מחכה.
- **אף פעם אל תכתוב לסיגנל שאתה גם קורא באותו effect.** Angular תסרב להריץ אותו ותרשום אזהרה.
- **אף פעם אל תקרא סיגנלים של חנות אחת במקום ש-`computed` של חנות אחרת קוראת.** אם `HabitStore.streakDays` קורא `TaskStore.tasks`, עצב מחדש: שים את החישוב איפה שהוא שייך, או חשוף השלכה ייעודית.

Effects הם הקצה החד של ניהול המצב. בשימוש חסכני הם פותרים בעיות אמיתיות. בשימוש יתר הם הופכים את גרף המצב למבוך לא מסומן.

## התמדה: `localStorage` ומעבר

המשימות של Compass מגובות על ידי HTTP, אבל מצב UI — מסננים, ערכת נושא, סרגל צד פתוח/סגור, טיוטות — יותר נחמד להתמיד לרוחב sessions בלי מעבר הלוך ושוב. `localStorage` הוא הכלי הסטנדרטי.

עזר קטן להתמדה:

```ts
export function persistedSignal<T>(key: string, initial: T): WritableSignal<T> {
  const raw = localStorage.getItem(key);
  let start: T = initial;
  if (raw !== null) {
    try { start = JSON.parse(raw); } catch { /* התעלם */ }
  }
  const s = signal<T>(start);
  effect(() => {
    localStorage.setItem(key, JSON.stringify(s()));
  });
  return s;
}
```

השתמש בו בתוך קונסטרוקטור של חנות (או כשדה מחלקה עם `runInInjectionContext` אם אתה חכם):

```ts
@Injectable({ providedIn: 'root' })
export class UIState {
  filter = persistedSignal<'all' | 'open' | 'done'>('compass:filter', 'all');
  theme = persistedSignal<'light' | 'dark' | 'system'>('compass:theme', 'system');
}
```

עכשיו המסנן וערכת הנושא שורדים ריענון, בלי חיווט נוסף. רק זכור: `localStorage` הוא סינכרוני וחוסם את ה-thread הראשי. אל תשמור מגה-בייטים. שמור אותו למצב UI קטן; שמור נתונים מגובי-שרת על השרת.

## תור offline: דפוס מצב עם שיניים אמיתיות

תור offline הוא מקרה בוחן טוב לחנות לא-טריוויאלית.

הרעיון: כשהמשתמש עושה מוטציה (הוסף משימה, העבר done), Compass מנסה לשלוח אותה לשרת. אם הרשת כבויה או שהשרת מחזיר 5xx, המוטציה בתור מקומית עם חותמת זמן ומנסים שוב מאוחר יותר — כשהדפדפן שוב online, או אחרי עיכוב.

סקיצה של החנות:

```ts
type PendingMutation =
  | { kind: 'add'; task: Omit<Task, 'id'>; localId: string }
  | { kind: 'toggle'; taskId: string; done: boolean }
  | { kind: 'remove'; taskId: string };

@Injectable({ providedIn: 'root' })
export class MutationQueue {
  private api = inject(TasksApi);
  private queue = persistedSignal<PendingMutation[]>('compass:queue', []);

  readonly pendingCount = computed(() => this.queue().length);
  readonly online = signal(navigator.onLine);

  constructor() {
    window.addEventListener('online', () => this.online.set(true));
    window.addEventListener('offline', () => this.online.set(false));
    effect(() => {
      if (this.online() && this.queue().length > 0) {
        this.drain();
      }
    });
  }

  enqueue(m: PendingMutation): void {
    this.queue.update(q => [...q, m]);
  }

  private async drain(): Promise<void> { /* ... */ }
}
```

יישום ה-drain המלא ארוך יותר ממה שאנחנו צריכים בפרק הזה (הוא צריך לטפל בסדר, כישלון חלקי, ופיוס עם IDs של השרת). הנקודה המרכזית היא שהתור הוא *רק עוד חנות*. יש לו סיגנלים פרטיים, חושף תצוגות לקריאה בלבד, חושף מתודות, משתמש ב-effect לריאקטיביות. הוא נראה כמו כל חנות אחרת ב-Compass.

כשאתה פונה למשהו גדול יותר — NgRx SignalStore או NgRx הקלאסי — זה בדרך כלל סוג הקוד שמניע את המעבר. לא "יש לנו יותר מסיגנל אחד" אלא "יש לנו עדכוני מצב מתואמים והתנהגויות חוצות-רוחב".

## NgRx SignalStore

`@ngrx/signals` היא ספרייה קלת משקל שמקודדת את הדפוס למעלה ומוסיפה תכונות כמו *ניהול entity* (מערכים מאונדקסים עם חיפושים מהירים לפי id), *עוזרי effect*, ו-*הרחבות ריאקטיביות*. אם אתה מוצא את עצמך כותב הרבה `store.tasks().find(t => t.id === x)`, או בונה חיפושים מאונדקסים ידנית, `withEntities` של SignalStore שווה מבט.

סקיצה:

```ts
import { signalStore, withState, withMethods, withEntities } from '@ngrx/signals';

export const TaskStore = signalStore(
  { providedIn: 'root' },
  withEntities<Task>(),
  withState({ loading: false, error: null as string | null }),
  withMethods((store, api = inject(TasksApi)) => ({
    async load() { /* ... */ },
    async add(title: string) { /* ... */ },
    // ...
  })),
);
```

SignalStore בעל דעה ובגודל צנוע. אתה לא צריך אותו ל-Compass; חנויות שנעשו ידנית עובדות בסדר. כשאתה מגלה שכל החנויות שלך משתמשות בקוד entity-indexing דומה, SignalStore הוא המקום הטבעי לפנות אליו.

## מתי לפנות ל-NgRx הקלאסי (Redux)

NgRx הקלאסי — actions, reducers, effects, selectors — הוא מחויבות הרבה יותר גדולה. הוא מביא:

- **דיבוג עם time-travel.** כל שינוי מצב הוא action; אתה יכול לצעוד דרכם ב-DevTools.
- **מצב שניתן לסידור.** מצב הוא נתונים רגילים, תמיד. זה מקל על שמירה, שידור חוזר, או משלוח דרך הרשת.
- **מוטציות ניתנות לניבוי.** reducer הוא פונקציה טהורה; הדרך היחידה לשנות מצב היא לשגר action.

הוא גם מביא:

- **טקסים.** כל מוטציה הופכת ל-action, מקרה של reducer, effect, selector. שינוי של שורה אחת למצב יכול לגעת בחמישה קבצים.
- **צוק למידה.** חברי צוות חדשים מבלים שבוע לקבל אוריינטציה.

פנה ל-NgRx הקלאסי כשיש לך את כל אלה:

- צוות של חמישה מהנדסים או יותר שיגעו בקוד מצב יומיומית.
- מוטציות מצב שצריכות מסלולי ביקורת, undo/redo, או שידור חוזר.
- זרימות אסינכרוניות מורכבות שנהנות מלהיות מתוארות כ-pipelines של actions.

אל תפנה אליו כי "האפליקציה גדלה". גודל לבד לא הקריטריון; מורכבות של גרף המצב היא. Compass, אפילו במלוא תכונותיו, לא צריך אותו. פלטפורמת תמיכת לקוחות גדולה כנראה כן.

## Selectors, השלכות, ו-joins

כששתי חנויות צריכות לשלב את המצב שלהן, התשובה היא *selector* — `computed` שמושך משתיהן.

```ts
@Injectable({ providedIn: 'root' })
export class TodayDashboard {
  private tasks = inject(TaskStore);
  private habits = inject(HabitStore);

  todayCount = computed(() =>
    this.tasks.tasks().filter(t => !t.done && this.isToday(t.dueDate)).length +
    this.habits.habits().filter(h => !this.doneToday(h)).length
  );

  private isToday(d: string | null) { /* ... */ return false; }
  private doneToday(h: Habit) { /* ... */ return false; }
}
```

`TodayDashboard` היא *חנות תצוגה*: חנות שנבנתה על שתיים אחרות, מספקת תצוגה מוקרנת. דפוס ההרכבה הזה מחליף את רוב הצורך ב-container מצב גלובלי. כל חנות בעלת הדאגה שלה; חנות תצוגה משלבת את מה שהיא צריכה.

## בדיקת חנויות

כי חנויות הן Injectables, הן נבדקות עם אותה מכניקת DI כמו קומפוננטות. פרק 17 מכיל את הסיפור המלא; התצוגה המקדימה:

```ts
describe('TaskStore', () => {
  let store: TaskStore;
  let apiSpy: jasmine.SpyObj<TasksApi>;

  beforeEach(() => {
    apiSpy = jasmine.createSpyObj('TasksApi', ['list', 'create']);
    TestBed.configureTestingModule({
      providers: [{ provide: TasksApi, useValue: apiSpy }],
    });
    store = TestBed.inject(TaskStore);
  });

  it('exposes tasks after load', async () => {
    apiSpy.list.and.resolveTo([{ id: 't1', title: 'a', done: false, /* ... */ }]);
    await store.load();
    expect(store.tasks().length).toBe(1);
  });
});
```

החנות היא Injectable, אז `TestBed.inject` מקבל מופע טרי. התלות שלה, `TasksApi`, מסופקת כ-spy. הבדיקה מניעה את ה-API הציבורי של החנות ומאמתת על הסיגנלים שלה שנחשפו.

## מה שאתה צריך להימנע ממנו

כמה אנטי-דפוסים בצורת מצב תופסים מתחילים.

- **קריאה מסיגנל וכתיבה אליו ב-`computed` אחד.** ערכי computed הם לנגזרות טהורות. אם אתה מוצא את עצמך רוצה לכתוב, השתמש ב-effect (וחשוב היטב אם יש לך מעגל בגרף המצב).
- **הפיכת הכל ל-observable.** קוד Angular ישן יותר התמקד ב-`BehaviorSubject` כפרימיטיב המצב. סיגנלים הם הפרימיטיב הנכון עכשיו. שמור observables לזרמים אמיתיים (HTTP, אירועי DOM, WebSockets).
- **אחסון מצב נגזר.** אם A הוא `B + C`, אל תאחסן את A. אחסן את B ואת C; גזור את A עם `computed`. אז A לא יכול להסחף מסנכרון.
- **גרפי אובייקטים עמוקים.** סיגנלים עוקבים אחרי התייחסויות, לא ערכים עמוקים. עצים גדולים מקוננים קשים לעדכן immutable. העדף מצב שטוח, מנורמל; השתמש במפות entity (`Record<Id, Entity>`) במקום במערכים מקוננים.

## מה בא הלאה

פרק 15 פונה לדירקטיבות ולפייפים — הפרימיטיבים של UI לשימוש חוזר שמאפשרים לך לארוז התנהגות (auto-focus, long-press, tooltip) ועיצוב (זמן יחסי, מטבע, קיצור) בלי לעטוף הכל בקומפוננטות. פרק 16 מבצע פרופיל של Compass ומוסיף `@defer`, `OnPush`, ואופטימיזציית תמונות כדי לגרום לו להיות מהיר בטלפון.

### תרגילים

1. הוסף `SelectionStore` שעוקב אחר אילו משימות נבחרות כרגע (נניח, לפעולות bulk). היא צריכה לחשוף `selected: Signal<Set<string>>`, `isSelected(id)`, `toggle(id)`, `clear()`, ו-`count = computed(...)`. שמור אותה קטנה.

2. חבר את סקיצת ה-`MutationQueue` למעלה לתוך `TaskStore`. כשהרשת offline, שים מוטציות בתור; כשהיא חוזרת, נקז אותן בסדר. בדוק על ידי הריגת `json-server` באמצע session וקריאה של הסיגנל `pendingCount` של התור.

3. עצב מחדש את `UIState` של Compass (מסנן, ערכת נושא, סרגל צד) לשימוש ב-`persistedSignal`. אז פתח שתי טאבים של דפדפן על Compass וראה אם שינויים באחד מתפשטים לאחר (הם לא כברירת מחדל — אירועי `storage` היו, וזו הרחבה קטנה ל-`persistedSignal`).
