@echo off
git reset d465080
git add gui.py start_app.bat
git commit -m "feat: native windows GUI application"
git add .
git commit -m "chore: final polish and formatting"
git push -u origin main --force
