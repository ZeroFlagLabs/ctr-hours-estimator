# CTR Hours Estimator

ZeroFlagLabs | Windows desktop application | v2.0.2

Estimate project engineering hours and full-time equivalent (FTE) headcount using task quantities, hours per task and other hours. Version 2.0.0 modernises the original v1.0–v1.1 application without changing its calculation equations.

## v2.0.2 status bar centring

Vertically centred status text with a stable baseline; standard font, colours, height and message behaviour retained. Calculation engine unchanged.

## v2.0.1

Standardised action and Settings input dimensions; linked the FTE heading to its efficiency footnote. Calculation and saved defaults unchanged.

## Download

Download the [latest Windows portable ZIP](https://github.com/ZeroFlagLabs/ctr-hours-estimator/releases/latest), extract the single unsigned EXE and run it. No installer or separate Python runtime is required. Verify the ZIP SHA-256 in the release notes. Preferences are saved per Windows user, not beside the executable.

## Calculation basis

Total hours = sum of (task quantity × hours per task) + other hours.

FTE headcount = total hours / (duration in weeks × 37.5 hours/week × 0.80).

The assumed UK working week of 37.5 hours and 80% efficiency give 30 effective hours per FTE per week. A positive duration is required to calculate FTEs. Estimates support resource planning, not detailed scheduling.

## Using the calculator

- Enter integer quantities (0–999) for new/revised P/Ns and drawings; hours per task and other hours accept 0–9999.99, up to two decimal places.
- Use Other hours for supplementary hours or a known total when quantities are blank or zero. Results update automatically.
- Settings → Defaults saves your preferred task rates and other hours and applies them immediately, retaining quantities and duration. Factory values are 4, 2, 8, 4 and 0 hours. Restore defaults stages these values; Save defaults confirms them. Closing without saving discards edits.
- Reset clears quantities, restores all five saved hours defaults and sets duration to zero.
- Settings → Updates checks stable GitHub releases; no automatic downloads or installation.

## Development and licences

See [development](docs/DEVELOPMENT.md), [third-party notices](docs/THIRD_PARTY_NOTICES.md) and [LGPL rebuild instructions](docs/ONEFILE_REBUILD_AND_LGPL.md). Original application code is MIT licensed; third-party components retain their licences.
