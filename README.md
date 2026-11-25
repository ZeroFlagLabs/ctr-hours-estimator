# CTR Hours Estimator

A Python-based engineering utility for estimating total project hours
and determining required full-time equivalent (FTE) personnel over a
defined duration.

The tool supports both breakdown-based estimation and manual total hours
input, with automatic real-time calculation.

------------------------------------------------------------------------

## 📐 Methodology

### Total Hours

Total project hours are calculated as:

Total Hours =\
(New P/Ns Qty × Hrs/Task) +\
(Revised P/Ns Qty × Hrs/Task) +\
(New Dwgs Qty × Hrs/Task) +\
(Revised Dwgs Qty × Hrs/Task) +\
Additional Hours

------------------------------------------------------------------------

### Employees Required

Employees are calculated as:

Employees = Total Hours / (Weeks × 37.5 × 0.8)

Where:

-   37.5 = standard UK working hours per week\
-   0.8 = assumed efficiency factor

If weeks are not provided, employee calculation is not performed.

------------------------------------------------------------------------

## ⚙️ Input Behaviour

### Default Values

-   New P/Ns → 4 hrs/task\
-   Revised P/Ns → 2 hrs/task\
-   New Dwgs → 8 hrs/task\
-   Revised Dwgs → 4 hrs/task\
-   Additional Hours → 8 hrs\
-   Quantities → 0

### Input Rules

-   Quantities → integers only\
-   Hours and duration → decimal values allowed\
-   Weeks → optional

------------------------------------------------------------------------

## 🔄 Modes of Operation

### Breakdown Mode (default)

-   Uses task quantities and hours per task\
-   Automatically calculates total hours

### Manual Mode

-   Enabled via checkbox\
-   User inputs total hours directly\
-   Breakdown inputs are disabled

------------------------------------------------------------------------

## 🖥️ Usage

### GUI Application

python src/main.py

Provides:

-   Real-time calculation\
-   Dual input modes\
-   Automatic validation of numeric inputs\
-   Clean reset to default values

------------------------------------------------------------------------

## 🛠️ Build Executable

Use the standard packaging script:

tools/package_app.sh

You will be prompted for:

-   App Name (e.g. CTR Hours Estimator)\
-   Version (e.g. 1.0)

Output will be:

dist/CTR Hours Estimator v1.0.exe

Notes:

-   Run from project root directory\
-   Requires virtual environment (use dev_shell.sh)\
-   Output executable is fully standalone

------------------------------------------------------------------------

## 📁 Project Structure

-   src/main.py → Application entry point + UI logic\
-   src/calculator.py → Core calculation logic\
-   src/ui/main_window.ui → Qt Designer UI file\
-   src/resources/icons/ → Icon files\
-   src/resources/images/ → Image assets\
-   src/resources/data/ → Data files (if applicable)\
-   tools/dev_shell.sh → Development environment\
-   tools/package_app.sh → Build script

------------------------------------------------------------------------

## 🚀 Status

✔ Breakdown-based estimation\
✔ Manual total hours mode\
✔ Automatic calculation\
✔ Input validation\
✔ Reset functionality\
✔ GUI interface\
✔ Standalone executable build

------------------------------------------------------------------------

## 📌 Notes

This tool is intended for:

-   quick engineering estimates\
-   internal planning and resource assessment\
-   replacing simple spreadsheet-based calculations

It is not intended to replace detailed project planning tools.

------------------------------------------------------------------------

## 🔄 Version History

### v1.0

-   Initial release

### v1.1

-   Remove created by name from main_window.ui