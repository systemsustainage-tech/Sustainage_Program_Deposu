@echo off
echo Setting up Git Hooks...

if not exist ".git\hooks" (
    echo Error: .git directory not found. Are you in the project root?
    exit /b 1
)

copy /Y tools\git_hooks\pre-commit .git\hooks\pre-commit
echo Hook installed.

rem Make sure it's not read-only (sometimes happens)
attrib -r .git\hooks\pre-commit

echo Done.
