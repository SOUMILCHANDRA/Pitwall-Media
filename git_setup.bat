@echo off
git init
git add requirements.txt loader.py
git commit -m "chore: initial project setup and data loader"

git add analyzer.py narrator.py
git commit -m "feat: heuristic analysis and narrative generation"

git add renderer.py templates/
git commit -m "feat: rendering engine and HTML templates"

git add main.py
git commit -m "feat: CLI orchestrator"

git add gui.py start_app.bat
git commit -m "feat: native windows GUI application"

git add .
git commit -m "chore: final polish and formatting"

git remote add origin https://github.com/SOUMILCHANDRA/Pitwall-Media.git
git branch -M main
git push -u origin main
