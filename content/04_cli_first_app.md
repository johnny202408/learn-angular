# Chapter 4. The CLI, your first app, and the anatomy of an Angular project

This chapter is different from the previous three. It is the first chapter you should read *with your laptop open*. By the end of it, Compass will exist as a project on your disk, its dev server will be running, and its starter page will be open in your browser. Then we will go through every file the Angular CLI produced, so nothing in your new project looks mysterious the first time you open it in an editor.

If you get stuck installing Node.js, jump to Appendix A for platform-specific notes. Come back when you have a working `node --version` and `npm --version` in your terminal.

## What we're installing, and why

You need three things to work on Angular:

1. **Node.js** — a runtime that lets JavaScript run outside a browser. Angular's development tools (the compiler, the dev server, the test runner) are JavaScript programs; they run on Node.js. You will barely interact with Node.js directly, but everything depends on it.

2. **npm** — Node.js's package manager. It comes bundled with Node.js. It downloads libraries — including Angular itself — into a folder called `node_modules` inside your project.

3. **The Angular CLI** — the `ng` command. This is a tool that scaffolds new projects, generates new files, runs your app, runs your tests, and builds for production. Everything you do with Angular for the rest of this book goes through `ng`.

## Installing Node.js

Go to `nodejs.org` and download the **LTS** (long-term support) version. At the time of writing this is Node.js 20; when you read this it will likely be Node.js 22 or later. Either is fine as long as it is 20 or above; Angular refuses to install on older Node versions.

Follow the installer for your platform. On macOS and Windows, the installer places `node` and `npm` on your `PATH` automatically; on Linux, use your distribution's package manager or the tarball on the Node.js website (see Appendix A).

Open a terminal — the *Terminal* app on macOS, *Windows Terminal* or *PowerShell* on Windows, your favorite terminal emulator on Linux — and verify:

```bash
node --version    # v20.x.x or higher
npm --version     # 10.x.x or higher
```

Both should print a version number. If either says "command not found," see Appendix A.

## Installing the Angular CLI

With Node.js in place, install the CLI globally with npm:

```bash
npm install --global @angular/cli
```

The `--global` flag makes `ng` available anywhere on your machine, rather than only in one project's folder. Confirm:

```bash
ng version
```

You should see the Angular CLI version, plus a header listing the packages it will install. If you get "command not found," open a new terminal window — the shell needs to notice the newly-installed binary.

> **Note.** Some people prefer never to install anything globally. If that is you, you can use `npx @angular/cli` in place of `ng` anywhere in this book. It downloads a temporary copy each time. It is slower but keeps your global environment clean.

## Creating Compass

Pick a folder to keep your projects in. In this book I will use `~/dev`. Substitute your own if you prefer.

```bash
cd ~/dev
ng new compass
```

The CLI asks you a few questions. Answer them as follows:

- **Which stylesheet format would you like to use?** → `CSS`. We will not use Sass in this book. If you already know Sass, you can pick it; the code will still work.
- **Do you want to enable Server-Side Rendering (SSR)...?** → `No`. We will add SSR in Chapter 18, once the app is worth prerendering.
- **Which type of routes would you like to configure?** — if this appears, choose the default (server routes with data prefetching if offered; otherwise leave routing enabled). Newer CLIs default this without asking.

The CLI creates a `compass` folder next to wherever you ran the command, downloads roughly two hundred packages into `node_modules` (this will take a minute or two the first time), and stops. It then leaves you at your prompt with a small hint about `ng serve`.

Take that hint:

```bash
cd compass
ng serve --open
```

A few seconds later, your browser will open at `http://localhost:4200` and you will see Angular's default starter page. Congratulations — you are running an Angular application.

`ng serve` also stays open in your terminal, watching your source files. Save a change, and the browser reloads automatically. Leave `ng serve` running in one terminal window; open a second terminal for the rest of this chapter.

## A tour of every file the CLI produced

Open `~/dev/compass` in your editor of choice. If you don't have a preferred editor, install **Visual Studio Code** from `code.visualstudio.com` and open the folder with `File → Open Folder`. VS Code has the best out-of-the-box Angular support of any free editor; when we start writing components in Chapter 5, its inline error messages will save you a lot of time.

We are going to walk through every top-level file and folder now. It is a long walk. Do not try to memorize; just get a mental map of what each thing is for. You will meet each of these files again, in context, later in the book.

### `package.json`

This is the description of your project as far as npm is concerned. Two sections are worth inspecting.

`scripts` lists the commands you can run via `npm run <name>`:

```json
"scripts": {
  "ng": "ng",
  "start": "ng serve",
  "build": "ng build",
  "watch": "ng build --watch --configuration development",
  "test": "ng test"
}
```

`npm run start` and `ng serve` are equivalent. Some conventions prefer `npm run` because it keeps the same commands working in projects that use different underlying tools; in an Angular project you can use either.

`dependencies` lists the libraries your app needs at runtime; `devDependencies` lists the tools it needs during development. When a new Angular version comes out and you want to update, you edit these version numbers or run `ng update` — a topic for another day.

### `angular.json`

The CLI's configuration file. It tells Angular how to build, serve, and test the project. You will rarely edit it by hand in the early chapters; we will visit it in Chapter 16 (performance) and Chapter 19 (deployment). For now, know that it exists.

### `tsconfig.json` and its friends

Three TypeScript configuration files:

- `tsconfig.json` — the base configuration.
- `tsconfig.app.json` — the configuration used when building the app itself.
- `tsconfig.spec.json` — the configuration used when running tests.

You will not touch these until you start writing tests in Chapter 17. The main file enables *strict mode* by default in modern Angular projects, which means TypeScript will be strict about `null` checks, implicit `any`, and other footguns. Do not turn strict mode off. It is the reason your app will remain refactorable a year from now.

### `.editorconfig`

A tiny file that tells your editor about indentation, line endings, and other basics. If your editor understands it (most modern ones do, sometimes with a plugin), your formatting will match the CLI's defaults automatically.

### `.gitignore`

A file listing what git should not track. Notably it excludes `node_modules/` (which is huge and reproducible from `package.json`) and `dist/` (build output). We will initialize a git repository shortly.

### `node_modules/`

The installed packages. Angular itself lives here, along with everything Angular depends on and everything you install later. Do not check this folder into git; it is often gigabytes in size and is fully reproducible with `npm install`. If you delete it, you can recreate it with `npm install`.

### `public/`

Static files served as-is at the root of your app. If you drop `robots.txt` or `favicon.ico` here, they appear at `/robots.txt` and `/favicon.ico` in the running app. The CLI drops a default `favicon.ico` here.

### `src/index.html`

Open it. It is very short:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Compass</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
</head>
<body>
  <app-root></app-root>
</body>
</html>
```

That `<app-root>` element is the single anchor point for the entire application. When the browser loads the page, Angular boots up, finds this element, and takes it over. Everything you see on `http://localhost:4200` is rendered inside `<app-root>`.

You will rarely edit `index.html`. You edit its title, occasionally add a `<link>` for a font, and otherwise leave it alone.

### `src/styles.css`

Global CSS. Anything in here applies to the whole application. Font imports, CSS resets, and root-level custom properties (CSS variables) live here. Per-component styles — the styles for a task row, say — live in the component file, which we meet in Chapter 5.

### `src/main.ts`

The bootstrap file. Very short:

```ts
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';

bootstrapApplication(App, appConfig)
  .catch(err => console.error(err));
```

`bootstrapApplication` says: "start the Angular application, whose root component is `App` and whose configuration is `appConfig`, in whatever element in the HTML has the tag defined by `App`'s selector." The result is that `<app-root>` in `index.html` gets populated with the rendered root component.

You will edit `main.ts` almost never — perhaps once in Chapter 18 to enable server-side rendering.

### `src/app/`

This is where your application lives. Everything you write from Chapter 5 onward goes into `src/app/` or its subfolders. The CLI has already put three files here:

**`app.ts`** (or `app.component.ts` in some CLI versions) — the root component. Roughly:

```ts
import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly title = signal('compass');
}
```

The four things to notice, none of which you need to *understand* yet:

- The `@Component` decorator. It tells Angular that this class is a component, and it configures the component with a selector (`<app-root>`), a template file, a style file, and any other components or directives this component uses in its template.
- The class body. Anything the component wants to expose to its template goes here — fields, methods, signals.
- The `signal(...)` call. That is Angular's modern reactive state primitive. The template can read `title()` and it will re-render if the signal ever changes.
- `imports: [RouterOutlet]`. Standalone components declare what other components and directives they use. `RouterOutlet` is the placeholder where the router will render pages.

Every chapter from Chapter 5 onward spends time inside components like this one. Do not worry about parsing it now.

**`app.html`** — the template for the root component. The CLI fills this with a Angular-branded starter page. You will delete most of it in Chapter 5.

**`app.css`** — styles scoped to the root component. Anything you write here applies to `<app-root>` and nothing else — even if you have a `.container` class in this file and another `.container` class somewhere else, they will not collide. This is called *view encapsulation*, and it is one of the quietly good things about writing Angular.

**`app.config.ts`** — the app-level configuration.

```ts
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
  ],
};
```

`providers` is the list of services and configuration your app makes available everywhere. In modern Angular, most cross-cutting concerns are set up by calling `provideX()` functions here — routing, HTTP, animations, and so on. We will add several of them in later chapters.

**`app.routes.ts`** — an initially-empty list of route definitions:

```ts
import { Routes } from '@angular/router';

export const routes: Routes = [];
```

Chapter 13 fills this in and makes Compass a multi-page app.

## What the CLI can do besides `new` and `serve`

Get a habit of using `ng generate` for scaffolding. It saves typing and, more importantly, it puts new files in the right place with the right imports.

```bash
ng generate component task-row      # creates src/app/task-row/*
ng generate service tasks           # creates src/app/tasks.service.ts
ng generate pipe date-friendly      # creates src/app/date-friendly.pipe.ts
```

You can abbreviate to `ng g c task-row`. In this book we will always type the long form so you know what you are doing; in daily practice you will abbreviate.

Other commands worth knowing:

```bash
ng serve          # dev server; watches files, reloads on save
ng build          # production build into dist/
ng test           # runs the unit tests
ng lint           # runs the linter, if configured
ng update         # updates Angular and related packages
```

## Git, right now

Before you write a single line of code, initialize a git repository. Your future self will thank you the first time you break something and want to see what you had five minutes ago.

```bash
git init
git add .
git commit -m "Initial commit from ng new"
```

If you have never used git, spend twenty minutes with the first two chapters of any git primer (`git-scm.com/book` is free). You will use `git status`, `git add`, `git commit`, and `git diff` about fifty times each in this book.

## Making sure it all works

With `ng serve` still running from earlier, open `src/app/app.html` in your editor. Find the first `<h1>` (or a place with visible text) and change some text to `Hello, Compass.`. Save the file.

Your browser tab should refresh within a second, and the new text should appear. If it does, you have a working Angular development environment.

If it does not — the page does not update, or the terminal prints an error — see Appendix A's troubleshooting section, or Appendix B, which is a guide to reading Angular error messages.

## What comes next

Part II. In Chapter 5 we will delete most of the CLI's starter content and build Compass's first real component: a list of tasks. You will meet templates, data binding, and the new control flow syntax. By the end of Chapter 5, Compass will be a to-do list — a very simple one, running entirely in the browser, without any of the persistence, routing, or authentication of the finished product. Every subsequent chapter adds one more real capability.

### Exercises

1. Run `ng generate component about --skip-tests --dry-run` and read the output. The `--dry-run` flag tells the CLI to print what it would do without actually doing it. What files would be created? Do the same for `ng generate service auth --dry-run`. This is a useful habit for previewing what the CLI wants to do before it does it.

2. Open the browser's developer tools (F12 in most browsers) and click the "Elements" or "Inspector" tab. Find the `<app-root>` element in the DOM. Note that it is a real element in the page, and the app's content is rendered inside it. This is worth seeing once so you know Angular is not doing anything magical to the HTML.

3. In `src/app/app.html`, put `{{ title() }}` somewhere the text will be visible, and save. Notice the parentheses after `title` — that is not a typo. Signals are functions you call to get their current value. In Chapter 7 we will explore why. For now, just observe that it works.
