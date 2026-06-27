# Channel Reference

Tesla light shows use a fixed channel map. Your xLights export must contain
either **48** channels (closures only) or **200** channels (full lights + closures).
The Tesla template wires these up for you — this page is just a reference for what
the groups control.

## Two channel modes

| Channels | Meaning |
|----------|---------|
| **48**   | Closures / motion only (windows, mirrors, charge port, doors, liftgate) |
| **200**  | Full show — all individually addressable lights **plus** the 48 closures |

The [validator](../tools/validator.py) rejects anything that isn't exactly 48 or 200.

## Light groups (the "200" set)

These are the exterior light elements you can choreograph (on/off only):

- Headlights (left/right, high/low)
- Daytime running / signature lights
- Front turn signals
- Front fog lights
- Side marker / side repeater lights
- Tail lights & brake lights
- Rear turn signals
- Reverse lights
- License plate lights
- Aux/spot lights (where equipped)

> Exact element names and left/right split depend on the model. Use the model
> elements exactly as they appear in the Tesla xLights template.

## Closures (the "48" set — motion, not lights)

These actuate physically, so sequence them slowly:

- Driver/passenger front & rear **windows** (up/down)
- **Side mirrors** (fold/unfold)
- **Charge port** door (open/close)
- **Liftgate / trunk** (open/close — supported models)
- **Falcon doors** (Model X)
- **Frunk** (where supported)

## Practical limits

- **No dimming** — lights are binary on/off.
- **Closures are slow** — a window takes a couple of seconds to travel; don't
  schedule rapid open/close cycles.
- **Step time ≥ 15 ms** (validator minimum); 20 ms is the practical standard.
- **Duration < 4 hours** (validator maximum).

For the authoritative, model-specific channel diagrams, see the README and images
in the official repo: <https://github.com/teslamotors/light-show>.
