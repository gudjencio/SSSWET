# SSSWET — Google Sites mirror

The canonical public web application is:

**https://gudjencio.github.io/SSSWET/**

Google Sites should embed this canonical application rather than maintain a
second copy of its HTML, CSS and JavaScript. This avoids version drift: each
GitHub Pages deployment automatically becomes the version shown in the mirror.

## Create the mirror page

1. Open the Google Sites website you control and edit the intended SSSWET site.
2. Create a page named **SSSWET** (or open the existing SSSWET page).
3. Choose **Insert → Embed → By URL**.
4. Paste: https://gudjencio.github.io/SSSWET/
5. Insert the embed, expand it to the available page width and give the embed
   enough vertical space. Publish the Google Site.
6. Test the published Google Sites page in a private browser window and on a
   mobile device. Confirm that the embedded application loads and that the
   language selector works.

Google Sites is a mirror/entry point, not a second application host. The
canonical app remains available directly at GitHub Pages if embedding is
blocked by browser or Google Sites restrictions. Do not embed API credentials
or private configuration in the public page.

## Important browser limitation

The public GitHub Pages build is a static interface. It does not run the
Python research engine or expose a shared public research database. The
Python-backed API is available only when a user runs the local core service.
Some browser capabilities, especially geolocation and device APIs, can also
be restricted inside a Google Sites iframe; users can open the canonical
GitHub Pages URL directly when an embedded capability is unavailable.

## Deployment

The workflow `.github/workflows/pages-deploy.yml` publishes the contents of
`web/` whenever files in that directory change on `main`, and on manual
dispatch. In GitHub repository settings, open **Pages** and select **GitHub
Actions** as the build and deployment source if it is not already selected.
After the first successful deployment, the canonical URL is:

https://gudjencio.github.io/SSSWET/

If the URL initially returns 404, check the Pages setting and the latest
**Deploy SSSWET to GitHub Pages** workflow run before changing application
paths.
