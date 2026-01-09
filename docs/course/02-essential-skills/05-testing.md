---
sidebar_position: 5
sidebar_label: 'Testing Fundamentals: How to Know Your Code Works'
title: 'Testing Fundamentals: How to Know Your Code Works'
description: 'Testing Fundamentals: How to Know Your Code Works'
---


How do you know your code actually works? You run it and check. That's testing! But what if you could automate that process? That's automated testing, and it's a cornerstone of modern software development.

### What is Testing?

Testing is the process of verifying that your code does what you expect it to do. Manual testing is when you do this by hand. Automated testing is when you write code to test your code.

### Simple Assertions

The simplest form of a test is an assertion. An assertion is a statement that something must be true. For example, in plain English:

> Assert that the `add(2, 2)` function returns 4.

If it returns 5, the assertion fails, and the test fails.

### Unit Tests vs. Integration Tests

There are many types of tests, but two common ones are:

- **Unit Tests:** These test a small, isolated piece of code (a "unit"), like a single function. They are fast and simple.
- **Integration Tests:** These test how multiple parts of your system work together. For example, does your login form correctly talk to your database?

### AI for Test Generation

AI can be a huge help in writing tests. You can give your AI assistant a function and ask it to write tests for it.

> "Write a set of unit tests for the following JavaScript function. Cover edge cases like empty input and invalid data.
> 
> ```javascript
> function calculateAverage(numbers) {
>   if (numbers.length === 0) {
>     return 0;
>   }
>   const sum = numbers.reduce((a, b) => a + b, 0);
>   return sum / numbers.length;
> }
> ```"

### CRITICAL: Review AI-Generated Tests

AI-generated tests are a great starting point, but they can be superficial. The AI doesn't understand the *business logic* of your application. Always review the tests it generates. Ask yourself:

- What is this test actually checking?
- What important cases is it missing?

### Your Turn: Write Manual Tests

Look back at the number guessing game from a previous post. You can't easily write automated tests for it yet, but you can write down a list of manual tests.

Write down at least 5 test cases. For example:

1.  **Test Case:** Guess a number that is too high.
    **Expected Outcome:** The app should say "Too high!".
2.  **Test Case:** Guess the correct number on the first try.
    **Expected Outcome:** The app should say "You got it!".

This thinking process is the first step toward automated testing.
