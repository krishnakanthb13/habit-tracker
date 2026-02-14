# Contributing to Habit Tracker

We love contributions! Since this is a local-first project, here is how you can help.

## Bug Reporting

If you find a bug, please open an issue on GitHub with:
1. Steps to reproduce the bug.
2. Expected behavior vs. actual behavior.
3. Your OS and Python version.

## Feature Suggestions

Have a cool idea? Open an issue to discuss it first. We prioritize features that align with our **Privacy** and **Local-First** principles.

## Development Setup

1. **Fork** the repository.
2. **Clone** your fork locally.
3. **Environment**:
    - Ensure Python 3.10+ is installed.
    - Run `launch.bat` (Windows) or `./launch.sh` (Linux/Mac) to automatically set up the virtual environment and launch the app.
4. **Code Structure**:
    - Backend logic is in `app/services`.
    - Routing is in `app/routes`.
    - Frontend logic is in `app/static/js`.

## Pull Request Process

1. Create a new branch for your fix/feature: `git checkout -b my-feature`.
2. Ensure your code follows the existing style (formatted with Black/Ruff for Python).
3. Test your changes manually in the browser.
4. Export your data to ensure the CSV engine still works.
5. Submit a PR with a clear description of the changes.

## Pre-submission Checklist
- [ ] Code is formatted.
- [ ] No hardcoded personal paths.
- [ ] No sensitive keys in `config.py`.
- [ ] `requirements.txt` is updated if new packages were added.
- [ ] Documentation reflects changes.

Thank you for helping make Habit Tracker better!
```
