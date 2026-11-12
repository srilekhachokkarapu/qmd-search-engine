
# Python Functions

## Introduction

A function is a reusable block of code that performs a specific task.

Functions help organize code, reduce repetition, and improve readability.

## Defining a Function

In Python, we define a function using the def keyword.

Example:

    def greet():
        print("Hello, World!")

## Function Parameters

Parameters allow functions to receive input values.

Example:

    def add(a, b):
        return a + b

## Return Statement

The return statement sends a result back to the function caller.

Example:

    result = add(10, 20)
    print(result)

The output is 30.

## Types of Functions

Python supports built-in functions, user-defined functions,
lambda functions, and recursive functions.

## Default Arguments

Python functions can have default parameter values.

Example:

    def greet(name="User"):
        print("Hello", name)

If no argument is provided, the default value is used.