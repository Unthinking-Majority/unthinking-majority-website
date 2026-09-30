# theme app

The **django-tailwind** theme app (`TAILWIND_APP_NAME = "theme"`). It owns the Tailwind CSS build, the root HTML template, the fonts, and a few reusable form component template tags. It has no models.

## Layout

```
theme/
  static_src/                 # Node project for the Tailwind build (node_modules gitignored)
    package.json              # scripts: dev (watch), build (minified)
    tailwind.config.js        # content globs, custom fonts/colours, safelist, plugins
    postcss.config.js         # postcss-nested
    src/styles.css            # @tailwind layers, @font-face defs, custom utilities
  static/css/dist/styles.css  # BUILD OUTPUT (gitignored); loaded via {% tailwind_css %}
  static/fonts/               # Kumbh Sans (all weights), RuneScape chat, SanAndreas, HorseSaguaro, CastIron
  templates/base.html         # root <html> template
  templates/theme/footer.html
  templates/theme/components/ # page_header, simple_input, textarea_input, file_input
  templatetags/um_components.py
```

## Tailwind

- This is **Tailwind CSS v3** (`tailwindcss ^3.4`), configured through `tailwind.config.js` (not v4 CSS-first config). Plugin: `@tailwindcss/typography` (used for the `prose` class on Wagtail rich text). `line-clamp-*` is built into Tailwind core.
- Commands, run from the repo root:
  - `./manage.py tailwind install`: `npm install` in `static_src`.
  - `./manage.py tailwind start`: dev watcher.
  - `./manage.py tailwind build`: production build.
  - On Heroku, the root `package.json` runs `npm ci` and `npm run build` in `theme/static_src` before `collectstatic`.
- **Content globs** scan every `templates/**/*.html`, every `*.js` and every `*.py` in the project. So Tailwind classes written in Python strings, such as widget attrs or form code, are picked up.
- **Dynamic classes must be safelisted.** Templates build class names from the Wagtail `theme` choice, e.g. `bg-um-{{ page.theme }}` and `shadow-um-{{ self.theme }}/30`. The `safelist` covers `bg-`, `text-` and `shadow-um-(brown|purple|green)` with `hover`. If you add a new theme colour to `main.THEME_CHOICES`, add it to `theme.extend.colors` and to the safelist regexes.

Custom theme values (`theme.extend`):

- Colours: `um-brown #372D1F`, `um-purple #371F35`, `um-green #1F3721`.
- Font families:
  - `font-sans`: Kumbh Sans (the site default).
  - `font-runescape`: OSRS chat font, used for in-game flavour text.
  - `font-western`: HorseSaguaro (bounty).
  - `font-cast-iron`: bounty.
  - `font-san-andreas`.

Custom utilities in `src/styles.css`:

- `text-border` (1px black outline) and `text-shadow`.
- `text-yellow-runescape` (#ffff00, the OSRS chat yellow).
- `scroll-bar` (thin hover scrollbar).
- A `prose` override that makes iframes full-width at 16:9.

`@font-face` URLs are relative to the built CSS location (`../../fonts/...`), so don't move the output directory without updating them.

## Templates

- `base.html` loads `{% tailwind_css %}` and defines the blocks `title`, `extra_head`, `main` and `footer`. The body uses `bg-slate-700 font-sans`. Every page should extend `main/site_base.html`, which extends this file and adds the navbar, toasts and the content card. Only extend `base.html` directly for a page with no navbar.
- Visual conventions: `slate` greys throughout, white or slate-100 rounded-lg cards with `shadow-xl shadow-black/40`, and `container mx-auto`. Layouts are mobile-first with `md:` breakpoints, and the navbar has separate desktop and mobile templates in `main/templates/main/navbar/`.
- Templates are formatted with **djlint** (dev dependency), which puts one attribute per line on long tags and uses 4-space indents. Class lists mostly follow Tailwind's recommended class order. Match both.

## Component template tags (`{% load um_components %}`)

- `{% page_header "Text" icon %}`: the standard page title, in RuneScape-font yellow text on a dark bar. The optional `icon` is an ImageField, such as `content.icon`.
- `{% simple_input form.field "Label" prefix %}`, `{% textarea_input ... %}` and `{% file_input ... %}`: hand-rendered, styled inputs that show field errors and a `*` on required fields.
  - They render the `<input>` manually, so the `name` must be built as `<prefix>-<field>`.
  - Inside a formtools wizard, **pass `prefix` as the step's form prefix** (e.g. `wizard.form.prefix`), or the POST data won't bind.

Autocomplete select widgets are in `main/widgets.py`, not here.
