# פרק 17. בדיקות: TestBed, component harnesses, Playwright

Compass עובד. ראית אותו עובד: לחצת מסביב, הוספת משימות, ורעננת את הדף. אבל "זה עבד כשניסיתי" זה לא אותו דבר כמו "זה ימשיך לעבוד כשנשנה אותו בחודש הבא". בדיקות הן ההבדל. חבילת בדיקות טובה מאפשרת לך לשנות שם של סיגנל, לחלץ שירות, או להעביר קומפוננטה בביטחון — הבדיקות יגידו לך מה נשבר.

הפרק הזה מכסה שלוש שכבות של בדיקות ב-Angular:

- **בדיקות יחידה** עבור חנויות, שירותים, ופייפים עם `TestBed`.
- **בדיקות קומפוננטה** עבור קומפוננטות בודדות, באמצעות component harnesses של CDK.
- **בדיקות מקצה לקצה** עבור זרימות משתמש לרוחב האפליקציה כולה, עם Playwright.

אתה לא תבדוק הכל. Compass, כמו כל אפליקציה אמיתית, תמיד יהיה בה קוד ניתן-לבדיקה שלא בדקת. המטרה היא לא כיסוי — היא ביטחון. בדוק את מה שיהרוס את היום שלך אם ייחלש, ואת מה שאתה שובר בטעות שוב ושוב.

## ההגדרה של בדיקות ש-Angular נותנת לך

`ng new` בונה תבנית של הגדרת בדיקות מהקופסה: **Jasmine** כפריימוורק ה-assertions ו-**Karma** כמריץ הדפדפן. לכל קובץ שנוצר יש `.spec.ts` תואם לידו.

הרץ את הבדיקות:

```bash
ng test
```

חלון דפדפן נפתח (Karma משיק Chrome אמיתי), מריץ את הבדיקות, ומדווח. בהרצה השנייה, הדפדפן נשאר פתוח; שינויים בקבצי בדיקות מריצים מחדש את ה-specs המושפעים אוטומטית.

אם אתה רוצה חלופה מודרנית וללא head, האקוסיסטם של Angular תומך גם ב-**Vitest** וב-**Web Test Runner**. המעבר הוא שינוי תצורה, לא שכתוב — ה-API של הבדיקה ללא שינוי. Karma יוצא לפנסיה אבל עדיין ברירת המחדל בזמן הכתיבה; Vitest הוא כיוון ההתקדמות.

בלי קשר למריץ, אתה כותב בדיקות באותה דרך: עם Jasmine (`describe`, `it`, `expect`) ו-`TestBed`.

## `TestBed`: DI לבדיקות

`TestBed` הוא ה-container של הבדיקות של Angular. הוא מגדיר injector, מאפשר לך לרשום providers (אמיתיים או מזויפים), ומאפשר לך ליצור מופעים של קומפוננטות ושירותים תחת בדיקה.

הדפוס:

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

המהלך המרכזי: `{ provide: TasksApi, useValue: apiSpy }`. כי `TaskStore` מקבל `TasksApi` דרך DI (`inject(TasksApi)`), הבדיקה מחליפה אותו בספיי. החנות לא יכולה לזהות — היא פשוט קוראת למתודות על מה שהועבר לה.

`jasmine.createSpyObj` בונה אובייקט שהמתודות בעלות השם שלו מוגדרות מראש עם `jasmine.Spy`. לכל מתודת ספיי יש `and.resolveTo(value)`, `and.rejectWith(err)`, `and.returnValue(v)`, `and.callFake(fn)` לשליטה בהתנהגות, ו-`.calls.count()`, `.calls.mostRecent()`, וכן הלאה לאימות איך היא נקראה.

זה מה שגורם ל-Angular להיות ניתן כל כך לבדיקה: כי הכל נכנס דרך DI, הכל יכול להיות מוחלף בבדיקות בלי לגעת בקוד תחת בדיקה.

## בדיקת סיגנלים

סיגנלים הם ערכים, לא אירועים. אתה בודק אותם על ידי קריאה שלהם בזמן הנכון.

```ts
it('remaining ignores done tasks', () => {
  store['_tasks'].set([
    { id: 't1', title: 'a', done: false, /* ... */ } as Task,
    { id: 't2', title: 'b', done: true,  /* ... */ } as Task,
  ]);
  expect(store.remaining()).toBe(1);
});
```

הגישה בסוגריים `store['_tasks']` היא רמאות קלה — היא מושיטה יד לתוך הסיגנל הפרטי כדי להגדיר מצב ישירות. לרוב הבדיקות, העדף להניע מצב דרך ה-API הציבורי (קרא ל-`store.add`, `store.toggle`). פנייה לסיגנל הפרטי בסדר כשבדיקה היא במפורש על ערך נגזר ואתה לא רוצה להגדיר את כל ריקוד ה-API.

לשינויי סיגנל אסינכרוניים, `await` את ה-promise שמניע את השינוי, אז קרא:

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

`effect` בתוך בדיקה צריך לרוץ בהקשר הזרקה, ש-`TestBed.runInInjectionContext` מספק.

## בדיקת פייפים

פייפים הם פונקציות. בדוק אותם כמו פונקציות.

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

לא נדרש `TestBed` — לפייפ אין תלויות שהוזרקו. זה הסוג הכי קל של בדיקה, ופייפים לעתים קרובות מכוסים יתר על המידה בגלל זה. בדוק את המקרים הגבוליים המעניינים; דלג על הטריוויאליים.

## בדיקת קומפוננטות עם `ComponentFixture`

`TestBed.createComponent` יוצר מופע של קומפוננטה ומחזיר `ComponentFixture` — עוטפת עם גישה למופע הקומפוננטה, ל-DOM המרונדר שלה, ולפקדי זיהוי שינויים.

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

שני דברים לשים לב:

- **`fixture.detectChanges()`** מריץ את זיהוי השינויים של Angular עבור העץ של ה-fixture. קרא לו אחרי ששיניתי input או סיגנל כדי לראות את ה-DOM המרונדר מתעדכן.
- **`By.css(selector)`** שולף מה-DOM המרונדר. `fixture.debugElement.query(...)` מחזיר `DebugElement`; `.nativeElement` הוא אלמנט ה-HTML הבסיסי.

הסוג הזה של בדיקה עובד אבל הוא מפורט. לבדיקת קומפוננטות אמיתית, ה-component harnesses של CDK הרבה יותר טובים.

## Component harnesses

**Harness** היא מחלקה שעוטפת קומפוננטה וחושפת את ההתנהגות שלה ברמת משימה — "לחץ על כפתור submit", "קרא את הודעת השגיאה" — במקום ברמת ה-DOM. ספריית ה-CDK של Angular מספקת מחלקת בסיס ו-Angular Material מספקת harnesses לכל קומפוננטת Material מהקופסה. אתה יכול לכתוב harnesses משלך לקומפוננטות שלך.

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

שימוש בה בבדיקה:

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

הבדיקה נקראת כמו הפעולות של המשתמש. אין `dispatchEvent`, אין `detectChanges`, אין `nativeElement`. כל מתודה היא `async` כי harnesses עובדים באופן זהה בבדיקות יחידה (TestBed) ובבדיקות מקצה לקצה (Protractor / Playwright) — האסינכרוניות היא מה שגורם לניידות הזאת להיות אפשרית.

כתיבת harness לכל קומפוננטה של Compass היא יותר קוד מהקומפוננטות עצמן. בפועל, צוותים כותבים harnesses לקומפוננטות שנמצאות בשימוש על ידי מספר בדיקות — "טופס הוספת המשימה" מקבל אחד כי חמש בדיקות מפעילות אותו; קומפוננטה חד-פעמית לא. התאם את ההשקעה שלך לשימוש חוזר.

## בדיקת קומפוננטות שמזריקות שירותים

הדפוס זהה לבדיקת חנויות: ספק זיופים.

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

סיגנלים בזיוף צריכים להיות סיגנלים ממשיים — הקומפוננטה קוראת אותם עם `()`. ערכים רגילים לא יעבדו.

## בדיקות מקצה לקצה עם Playwright

בדיקות יחידה מפעילות חתיכות. בדיקות מקצה לקצה (E2E) מפעילות את כל הדבר: דפדפן אמיתי, שרת אמיתי, זרימת משתמש אמיתית.

Angular כבר לא בונה תבנית של Protractor. Playwright היא הבחירה המודרנית; ל-CLI יש schematic רשמי:

```bash
ng add @angular-eslint/schematics    # אם אין לך את זה
ng add @playwright/test              # או ידנית לפי מסמכי Playwright
```

בדיקת Playwright:

```ts
import { test, expect } from '@playwright/test';

test('adds a task', async ({ page }) => {
  await page.goto('http://localhost:4200/');
  await page.fill('input[type=text]', 'Wash the car');
  await page.click('button[type=submit]');
  await expect(page.locator('li.task').filter({ hasText: 'Wash the car' })).toBeVisible();
});
```

הבדיקה מפעילה דפדפן אמיתי. היא לוחצת, מקלידה, מחכה לאלמנטים, ומאמתת. Playwright מטפלת בהמתנה אוטומטית כך שלעתים רחוקות תצטרך `sleep`.

בדיקות E2E צריכות `ng serve` ו-`json-server` רצים. ב-CI, אתה מסקרפט אותן להעלות לפני שהבדיקות רצות ולהיסגר אחריהן. ל-Playwright יש אפשרות תצורה `webServer` לזה.

בדיקות E2E איטיות ורעועות במהותן (רשת אמיתית, תזמון אמיתי). אל תנסה לבדוק כל מסלול עם E2E. בדוק את *המסעות הקריטיים*: התחבר וראה את המשימות שלך, הוסף משימה ורענן, מחק משימה ואשר שהיא איננה.

## בדיקת ניתוב ו-guards

לראוטר יש כלי בדיקות משלו. `RouterTestingHarness` היא הדרך המודרנית:

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

Guards ו-resolvers הם פונקציות; בדוק אותן עם `TestBed` שמספק את התלויות שלהם, וקרא להם ישירות:

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

## מה לבדוק, בסדר עדיפויות

אתה לא יכול לבדוק הכל. בערך, השקע בסדר הזה:

1. **מעברי מצב בחנויות.** אלה טהורים וקלים לבדיקה, והם מקודדים את רוב הלוגיקה העסקית. `toggle` לפני / אחרי; `add` כשה-API מצליח וכשהוא נכשל.
2. **התנהגות גלויה למשתמש של קומפוננטות קריטיות.** "לחיצה על submit מוסיפה את המשימה". אל תבדוק מתודות פרטיות; בדוק מה שמשתמש או קומפוננטה אחרת מבחין.
3. **Guards ו-resolvers.** הם מכניסים גישה; באג כאן יש לו השלכות אבטחה.
4. **פייפים עם לוגיקה לא-טריוויאלית.** בדוק את הענפים.
5. **חופן מסעות מקצה לקצה.** התחבר, עשה את הפעולה העיקרית, התנתק. לא כל פיצ'ר, רק אלה שהכשל שלהם היה מזמין אותך בשלוש בבוקר.

דלג על הטריוויאלי. אל תבדוק ש-`TaskList` מגדיר `title = 'Tasks'`. אל תבדוק boilerplate שנוצר על ידי CLI.

## אינטגרציה רציפה, בקצרה

כל בדיקה ב-`.spec.ts` רצה עם `ng test`. ב-CI, הרץ אותה ללא head:

```bash
ng test --browsers=ChromeHeadlessNoSandbox --watch=false
```

Playwright:

```bash
npx playwright test
```

pipeline של CI של Compass (פרק 19 חוזר לפריסה):

- Install: `npm ci`
- Lint: `ng lint`
- Type-check + unit test: `ng test --watch=false`
- Build: `ng build --configuration production`
- E2E: `npx playwright test`

אם כולן עוברות, פרוס.

## מה בא הלאה

פרק 18 מכסה רינדור בצד השרת ו-hydration — הטכניקה שנותנת למשתמשים שלך את הצביעה הראשונה שלהם לפני ש-Angular סיימה להתאתחל. אז פרק 19 פורס את Compass לאינטרנט, ופרק 20 שולח אותך עם תכנית להישאר מעודכן.

### תרגילים

1. כתוב spec ל-`TaskStore.toggle` שמכסה את מסלול העדכון האופטימי המוצלח ואת מסלול החזרה על כישלון. וודא עם ה-API spy שהחנות קראה ל-`update` פעם אחת בדיוק, ועל כישלון, שסיגנל המשימות חזר לצורה הקודמת שלו.

2. כתוב component harness ל-`TaskRow`. מתודות: `getTitle`, `isDone`, `clickToggle`, `clickDetails`. השתמש בה בבדיקה שמאמתת שלחיצה על ה-toggle פולטת את הפלט `toggled` עם ה-id של השורה.

3. הקם Playwright עבור Compass. כתוב בדיקה אחת מקצה לקצה שמתחילה בעמוד הבית, מוסיפה משימה חדשה, מרעננת את הדפדפן, ומאמתת שהמשימה עדיין שם. זה מאשר שהערימה המלאה (frontend + json-server) מחווטת נכון.
