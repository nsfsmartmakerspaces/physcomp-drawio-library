## Video Sources

1. Videos recorded using OBS with a 400x400 canvas, MKV H.264, window capture of KMag 400x400 window at varying zooms
2. Videos converted to webm with `ffmpeg -i input.mkv -lossless 1 output.webm`
3. Videos uploaded to [ezgif.com](https://ezgif.com/video-to-gif), trimmed, converted with FFMPEG at 10fps, downloaded as GIF. Start time, stop time, and fps added to filename.
4. Copy video into a folder in `static/` and add a version to the filename. Versioned files ensure that older templates work fine and forces draw.io to refresh its caches (new URL). A new template revision should be created for each new URL change.

TODO: Use FFMPEG instead of ezgif for reproducibility
