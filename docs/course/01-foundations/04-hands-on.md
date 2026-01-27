---
sidebar_position: 4
sidebar_label: 'Lesson 4: Building Your First Program'
title: 'Hands-On: Building Your First Program with AI'
description: 'Hands-On: Building Your First Program with AI'
---

> TL;DR: Turn the conversation into running code and make your first edit.

## Key steps
1. Copy the smallest working code into a local project.
2. Run it and confirm the baseline works.
3. Make one small change and re-run to verify.

## Practice
- Add one feature (e.g., a button state) and verify it works in the browser.

In our last post, we had a conversation with an AI to design a to-do list app. Now, let's take the next step: writing, running, and understanding a complete program. We will build a classic number guessing game.


### Step 1: The Prompt

We'll start by asking the AI to generate the entire game for us. We'll be specific about the rules.

**Your Prompt:**
> "I want to build a simple number guessing game in JavaScript. The rules are:
> 1. The computer picks a random number between 1 and 100.
> 2. The user is repeatedly asked to guess the number.
> 3. If the guess is too high, tell the user "Too high!".
> 4. If the guess is too low, tell the user "Too low!".
> 5. When the user guesses correctly, tell them "You got it!" and end the game.
> Please provide the complete JavaScript code for this game."

### Step 2: The Copy-Paste-Run Workflow

The AI will generate a block of JavaScript code. For this exercise, we will run it directly in our browser's developer console.

1.  **Copy the Code:** Copy the entire JavaScript code block provided by the AI.
2.  **Open Your Browser:** Open a new, empty tab in Chrome or Firefox.
3.  **Open the Console:** Right-click anywhere on the page, select "Inspect," and then click on the "Console" tab.
4.  **Paste and Run:** Paste the code into the console and press Enter.

The game should start immediately, prompting you for your first guess.

### Step 3: Understanding the Code

Here is an example of what the AI might generate:

```javascript
// 1. The computer picks a random number between 1 and 100.
const targetNumber = Math.floor(Math.random() * 100) + 1;

let guess = 0;

// 2. The user is repeatedly asked to guess the number.
while (guess !== targetNumber) {
  guess = parseInt(prompt("Guess a number between 1 and 100:"));

  // 3. If the guess is too high, tell the user "Too high!".
  if (guess > targetNumber) {
    alert("Too high!");
  // 4. If the guess is too low, tell the user "Too low!".
  } else if (guess < targetNumber) {
    alert("Too low!");
  }
}

// 5. When the user guesses correctly, tell them "You got it!" and end the game.
alert("You got it! The number was " + targetNumber);
```

Read through the code and the comments. This simple loop is the heart of the game. You are using the `prompt` function to get user input and the `alert` function to give feedback.

### Step 4: When Things Go Wrong

What if you type "hello" instead of a number? The game might break. When an error occurs, you can copy the error message from the console and ask the AI for help.

> "My number guessing game is breaking when I type in text instead of a number. I get this error: `[paste error message]`. How can I fix my code to handle this?"

This is the core loop of AI-assisted development: **prompt -> run -> get feedback -> refine prompt.**

Congratulations! You have now built your first interactive program with the help of an AI.

