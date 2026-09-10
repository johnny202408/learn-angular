# נספח א'. הגדרת המחשב שלך

הנספח הזה אוסף את ההגדרה הספציפית לפלטפורמה שפרק 4 הצביע עליה. קרא רק את הסעיפים שרלוונטיים למערכת ההפעלה שלך. חזור לצורך פתרון בעיות.

## מה אתה צריך, במבט מהיר

- **Node.js 20 או מאוחר יותר.** Angular מסרבת להתקין על גרסאות ישנות יותר.
- **npm 10 או מאוחר יותר.** מגיע עם Node.js.
- **ה-CLI של Angular.** מותקן גלובלית דרך npm.
- **עורך קוד.** Visual Studio Code מומלץ ובחינם.
- **Git.** לבקרת גרסאות; לעתים קרובות מותקן מראש.
- **מסוף.** כל אפליקציית מסוף מודרנית.

## macOS

**Node.js.** שתי אפשרויות טובות:

1. הורד את מתקין ה-LTS מ-`nodejs.org` והרץ אותו. זה מתקין את `node` ו-`npm` ב-`/usr/local/bin` (Intel) או `/opt/homebrew/bin` (Apple Silicon).
2. השתמש ב-Homebrew: `brew install node`. ההתקנה של Homebrew תואמת לארכיטקטורה שלך אוטומטית.

וודא:

```bash
node --version
npm --version
```

**Angular CLI.**

```bash
npm install --global @angular/cli
ng version
```

**עורך.** התקן את Visual Studio Code מ-`code.visualstudio.com`. אחרי ההתקנה, פתח את Terminal והרץ `code --version` — אם זה לא נמצא, פתח את VS Code והשתמש ב-Command Palette → "Shell Command: Install 'code' command in PATH".

**Git.** `xcode-select --install` מתקין את Command Line Tools, שכוללים את git. או `brew install git`.

## Windows

**Node.js.** הורד את מתקין ה-`.msi` של LTS מ-`nodejs.org` והרץ אותו. קבל את אפשרויות ברירת המחדל. זה מתקין את Node.js ו-npm ומוסיף אותם ל-PATH שלך.

פתח חלון PowerShell או Windows Terminal חדש (לא אחד מלפני ההתקנה — עדכוני PATH משפיעים רק על sessions חדשים). וודא:

```powershell
node --version
npm --version
```

**Angular CLI.**

```powershell
npm install --global @angular/cli
ng version
```

אם אתה מקבל שגיאת מדיניות ביצוע בעת הרצת `ng`, הרץ את PowerShell כמנהל והגדר:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**עורך.** התקן את Visual Studio Code מ-`code.visualstudio.com`. המתקין מציע תיבת סימון "Add to PATH" — השאר אותה מסומנת.

**Git.** התקן את Git for Windows מ-`git-scm.com`. קבל את ברירות המחדל, אבל במסך "Adjusting your PATH environment", בחר "Git from the command line and also from 3rd-party software".

**מסוף.** התקן את Windows Terminal מחנות Microsoft אם הוא לא שם כבר. הוא מטפל ב-PowerShell, cmd, ו-Git Bash בחן.

## Linux (Ubuntu / Debian / דומה)

**Node.js.** ה-Node.js של ההפצה לעתים קרובות ישן מדי. השתמש ב-NodeSource:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs
node --version
npm --version
```

או השתמש ב-nvm (Node Version Manager):

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# פתח מחדש את המסוף שלך
nvm install 20
nvm use 20
```

nvm היא הבחירה הטובה יותר לטווח ארוך כי היא מאפשרת לך להחליף גרסאות Node לפי פרויקט.

**Angular CLI.**

```bash
npm install --global @angular/cli
ng version
```

אם התקנת Node גלובלית בלי nvm, אולי תצטרך `sudo`:

```bash
sudo npm install --global @angular/cli
```

עדיף: הגדר את npm להתקין globals בתיקיית הבית שלך:

```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
# אז הוסף ~/.npm-global/bin ל-PATH שלך
```

**עורך.** ל-VS Code יש חבילות `.deb` ו-`.rpm` ב-`code.visualstudio.com`, או התקן דרך Snap: `sudo snap install code --classic`.

**Git.** כמעט תמיד מותקן מראש. אם לא: `sudo apt install git`.

## הרחבות VS Code מומלצות

אף אחת לא נדרשת בהחלט, אבל אלה הופכות את העבודה עם Angular להרבה יותר נחמדה:

- **Angular Language Service** (של צוות Angular הרשמי) — שגיאות inline והשלמה אוטומטית בתבניות.
- **ESLint** — מציג בעיות lint בעורך.
- **Prettier** — מפרמט קוד אוטומטית בשמירה.
- **GitLens** — git blame ברמת שורה והיסטוריה.
- **Path Intellisense** — משלים אוטומטית נתיבי ייבוא.

התקן דרך פאנל Extensions או `code --install-extension <id>`.

## פתרון בעיות

**"`ng` is not recognized" / "command not found."**

npm התקין את ה-CLI אבל ה-PATH שלך לא כולל את תיקיית ה-bin הגלובלית של npm. פתח מחדש את המסוף שלך קודם. אם עדיין נכשל:

```bash
npm config get prefix
```

הוסף את תיקיית ה-`bin` של הנתיב שהוחזר ל-PATH שלך (ב-`~/.zshrc`, `~/.bashrc`, או תצורת ה-shell שלך).

**גרסת Node ישנה מדי.**

התקנת Node לפני עידנים ו-Angular עכשיו צריכה חדשה יותר. ב-Windows/macOS הרץ את מתקין ה-LTS שוב; הוא משדרג. ב-Linux, השתמש ב-nvm כפי שתואר למעלה.

**זמני התקנה ארוכים.**

`ng new` מוריד הרבה חבילות בפעם הראשונה. בחיבורים איטיים זה יכול לקחת חמש דקות. פרויקטים עוקבים חולקים את מטמון ה-npm ומהירים יותר.

**שגיאות "EACCES" מ-npm.**

אתה מנסה להתקין חבילה גלובלית בלי הרשאה. השתמש ב-`sudo` (Linux; macOS עם Node של המערכת), הגדר את prefix של npm לתיקיית הבית שלך (טוב יותר), או השתמש ב-nvm (הטוב ביותר).

**Proxy או firewall של תאגיד.**

`npm` מכבד את משתני הסביבה `HTTP_PROXY` ו-`HTTPS_PROXY`. אם מקום העבודה שלך דורש אותם, הגדר אותם בתצורת ה-shell שלך. חלק מ-firewalls של תאגידים חוסמים חיפושי אישור של Node; בקש מצוות ה-IT שלך את חבילת הסרט הפנימית והגדר `NODE_EXTRA_CA_CERTS`.

**HMR / שרת פיתוח לא נטען מחדש.**

חלק ממערכות הקבצים (כונני שיתוף של Windows, חלק מ-mounts של Docker) לא מודיעות ל-Node על שינויים. נסה `ng serve --poll=1000` (סוקר כל שנייה). איטי יותר אבל אמין.

**Antivirus מאט כל בנייה לזחילה (Windows).**

הוסף את תיקיית הפרויקט שלך ו-`%APPDATA%\npm-cache` להחרגות ה-antivirus שלך. אל תשבית antivirus.

**"Cannot find module" אחרי `git pull`.**

מישהו אחר הוסיף תלות. הרץ `npm install` כדי לקלוט אותה.

**פורט 4200 כבר בשימוש.**

`ng serve` אחר רץ, או תהליך אחר לקח את הפורט. `ng serve --port 4201`. מצא והרוג את התהליך: ב-macOS/Linux `lsof -i :4200`; ב-Windows `netstat -ano | findstr 4200` ו-`taskkill /PID <id>`.

## הגדרת איכות-חיים מינימלית

אם אתה חדש בסביבות shell, בלה חמש-עשרה דקות על אלה פעם:

- השתמש בעורך עם סימון תחביר עבור TypeScript. (ל-VS Code יש את זה מהקופסה.)
- הפעל "format on save" כך שהקוד שלך יהיה מוזח ומצוטט אחיד.
- השתמש במסוף עם צבעים יפים (Windows Terminal, iTerm2, GNOME Terminal). קריאת traces ארוכות של stack במונוכרום היא לא נעימה.
- למד את קיצור הניווט בקבצים של העורך שלך. ב-VS Code: Cmd/Ctrl+P → הקלד קטע של שם קובץ. זה לבד מכפיל את המהירות שלך בפרויקט גדול.

## גרסאות Node לרוחב פרויקטים

ברגע שיהיו לך שני פרויקטי Angular במחשב שלך, הם עשויים לכוון לגרסאות Node שונות. `nvm` הוא הפתרון הנקי ביותר: שים קובץ `.nvmrc` בכל פרויקט (`echo 20 > .nvmrc`), ו-`nvm use` יקלוט את הגרסה הנכונה אוטומטית.

ל-Windows יש `nvm-windows`. macOS/Linux משתמשים ב-`nvm-sh`. שניהם עובדים; שניהם משתלבים היטב עם VS Code.
