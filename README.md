# Maths with Raman

How-to guides for teachers by Radha Raman Tiwari. Live at https://maths-with-raman.pages.dev

Cloudflare Pages serves the repository root. `index.html`, `assets/` and one folder per guide are **generated**: edit `source/`, run the build, commit both.

## Add a guide

1. Create `source/guides/<slug>/` containing:
   - `guide.json`: `title`, `subtitle`, `date` (YYYY-MM-DD, newest first on the home page), `substack` (URL), `thumb` (a file in `shots/`), `thumb_alt`, `hero` (`area-model` or a file in `shots/`), `hero_caption`, `footer`, `cta_head`, `cta_text`
   - `body.html`: the article. Use `<h2 id="...">` for sections (they become the sidebar contents). Images: `<p>[IMG:file-name-without-ext]</p>` followed by `<p><em>caption</em></p>`
   - `shots/`: the `.jpg` images
2. Run `python3 source/build.py`
3. Check `index.html` and `<slug>/index.html` in a browser (desktop and phone width)
4. Commit and push to `main`; Cloudflare redeploys in about a minute.

The About text and the home page hero are in `source/build.py` (`render_home`).
