---
sidebar_position: 2
sidebar_label: 'Building Your First Real Project: A Task Manage...'
title: 'Building Your First Real Project: A Task Manager App'
description: 'Building Your First Real Project: A Task Manager App'
---

> TL;DR: Build your first project end-to-end with AI as a copilot.

## Key steps
1. Pick a small project with clear inputs/outputs.
2. Build in small steps and verify each step.
3. Ship a working version before polishing.

## Practice
- Ship a tiny project (even ugly) that runs locally and has one core feature.

It's time to combine everything we've learned and build a complete project from scratch. In this tutorial, we will build a simple but functional Task Manager application. This is a classic "CRUD" (Create, Read, Update, Delete) app, a cornerstone of web development.

**Project Repository:** You can find the complete code for this project on GitHub [here](https://github.com/your-username/task-manager-app). (Note: This is a placeholder link. You will create your own repository).

### Step 1: Planning with AI

We'll start by asking our AI to create a plan, just like in our last post.

> "I want to build a simple task manager app using HTML, CSS, and JavaScript. The tasks should be saved in the browser's local storage. Please create a plan for the HTML structure, CSS styling, and JavaScript logic."

### Step 2: The HTML Structure

Based on the AI's plan, we'll create the `index.html` file. It will have an input field for new tasks, a button to add them, and a list to display them.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Task Manager</title>
    <link rel="stylesheet" type="text/css" href="css/style.css">
</head>
<body>
    <div class="container">
        <h1>Task Manager</h1>
        <input type="text" id="task-input" placeholder="Add a new task...">
        <button id="add-task-btn">Add Task</button>
        <ul id="task-list"></ul>
    </div>
    <script src="js/main.js"></script>
</body>
</html>
```

### Step 3: The CSS Styling

Next, we'll ask the AI to generate some simple CSS to make our app look clean. Create a `css/style.css` file.

> "Generate some simple CSS for the task manager HTML. Make it look clean and modern."

### Step 4: The JavaScript Logic (The Core)

This is where the magic happens. In `js/main.js`, we will write the code to handle the CRUD operations. We can ask the AI to help us with each part.

1.  **Create:** Get the value from the input field and add it to an array of tasks.
2.  **Read:** Display the tasks in the `<ul>` element. Save the tasks to `localStorage` so they persist on page refresh.
3.  **Update:** Add a button to mark tasks as complete (e.g., by adding a `completed` class).
4.  **Delete:** Add a delete button to remove tasks from the list.

Here is a prompt to get you started:

> "Write the JavaScript for the task manager. It should be able to add tasks, display them, and save them to local storage. When the page loads, it should load the tasks from local storage."

### Step 5: Putting It All Together and Testing

Open your `index.html` file in a web browser. Test all the features:

- Can you add a task?
- If you refresh the page, does the task reappear?
- Can you mark a task as complete?
- Can you delete a task?

If you encounter any bugs, use the debugging techniques we learned in previous posts. Ask your AI for help!

### Your Turn

Follow these steps and build the task manager app. This is your first full-stack (albeit client-side) application. Once you're done, push the code to a new repository on your GitHub. Congratulations, you've built and shipped your first real project!
