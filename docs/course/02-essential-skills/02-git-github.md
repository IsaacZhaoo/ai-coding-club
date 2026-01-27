---
sidebar_position: 2
sidebar_label: 'Git & GitHub 101: Saving Your Work Like a Pro'
title: 'Git & GitHub 101: Saving Your Work Like a Pro'
description: 'Git & GitHub 101: Saving Your Work Like a Pro'
---

> TL;DR: Use Git safely: small commits, clear diffs, and reversible changes.

## Key steps
1. Create a branch and make a small change.
2. Review diffs before committing.
3. Push and open a PR with clear notes.

## Practice
- Make a tiny docs change on a branch and write a good commit message.

Have you ever been afraid to change your code because you might break it? Version control is the answer. Think of it like a "save game" system for your code. Git is the most popular version control system, and GitHub is a website to store your Git projects online.

### What is Version Control?

Version control tracks changes to your files over time. This means you can:

- See who changed what and when.
- Go back to a previous version if you make a mistake.
- Collaborate with others on the same project without overwriting each other's work.

### Git Basics: Your Local Repository

Git works on your local machine. Here are the most common commands:

- **`git init`**: Initializes a new Git repository in your project folder.
- **`git status`**: Shows the status of your changes.
- **`git add <file>`**: Adds a file to the "staging area," which is a list of changes you want to save. Use `git add .` to add all files.
- **`git commit -m "Your message"`**: Saves the staged changes with a descriptive message.
- **`git log`**: Shows a history of all your commits.

### GitHub: Your Remote Repository

GitHub is a platform for hosting your Git repositories in the cloud. This allows you to back up your code and collaborate with others.

1.  **Create a GitHub Account:** Go to [https://github.com](https://github.com) and sign up.
2.  **Create a New Repository:** Click the "New" button on your GitHub dashboard.
3.  **Push Your Code:** Follow the instructions on GitHub to connect your local Git repository to the remote GitHub repository and "push" your commits.

### AI for Commit Messages

Writing good commit messages is important. If you're stuck, your AI can help!

> "Write a short, imperative git commit message for the following changes: [paste output of `git diff`]"

### Your Turn: Push to GitHub

1.  Go to the `my-first-project` directory you created in the last lesson.
2.  Run `git init`.
3.  Create a `README.md` file and write a short description of your project.
4.  Run `git status` to see your new file.
5.  Run `git add README.md`.
6.  Run `git commit -m "Add initial README file"`.
7.  Create a new repository on GitHub and push your first commit!

This is a fundamental workflow for all modern developers.
