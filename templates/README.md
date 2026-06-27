# xLights Template

The starting point for every show is Tesla's official blank xLights project,
`tesla_xlights_show_folder.zip`. It contains the car model (all channels mapped)
and a sample audio track.

## Get it

Download from the official repo:
<https://github.com/teslamotors/light-show>

Look for `tesla_xlights_show_folder.zip` in the file list, download, and unzip.

## Why it isn't committed here

The template is a binary zip owned by Tesla and updated upstream periodically.
Rather than vendor a stale copy, grab the current version from the source above.
If you want a frozen copy versioned with this repo, drop the unzipped project into
a new `shows/<name>/` folder and commit it there.

## Using it

1. Unzip into `shows/<your-show-name>/`.
2. Open the `.xsq` in xLights.
3. Replace the sample audio with your track (44.1 kHz).
4. Sequence, then export `lightshow.fseq` as **FSEQ V2 Uncompressed**.

See [../docs/getting-started.md](../docs/getting-started.md) for the full flow.
