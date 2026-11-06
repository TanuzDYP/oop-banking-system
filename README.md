# Banking & Ledger Management System

A terminal-based banking and financial ledger application built in Python demonstrating core Object-Oriented Programming (OOP) concepts, custom exception handling, and persistent data storage.

---

## Overview

This project simulates a commercial retail banking engine. It provides support for multiple account types (Savings and Checking), transactional audits, fund transfers between accounts, interest calculations, and automated JSON data persistence.

The project is intentionally developed without external dependencies, relying solely on Python's standard library.

---

## Core Features

- **Multi-Tier Account Support**:
  - **Savings Account**: Implements minimum balance requirements and automated annual interest yields.
  - **Checking Account**: Implements overdraft protection limits with automated penalty service fee deduction.
- **Atomic Fund Transfers**: Safely transfers balances between any two accounts on the platform.
- **Detailed Transaction Statements**: Formatted ledger reports with timestamps, transaction categories, amounts, and post-transaction balances.
- **Custom Exception Handling**: Explicit domain errors prevent unauthorized withdrawals, missing accounts, and invalid inputs without crashing the application.
- **Automatic State Persistence**: Automatically commits and synchronizes all accounts and audit logs to `bank_records.json`.

---

## Object-Oriented Principles Implemented

1. **Inheritance & Reusability**:
   `SavingsAccount` and `CheckingAccount` inherit baseline attributes and behavior from the base `Account` class using `super().__init__()`.

2. **Polymorphism & Method Overriding**:
   The `withdraw()` method is defined on the base `Account` class and overridden by each specialized subclass to enforce distinct business rules (minimum balance threshold vs. overdraft limits and fees).

3. **Encapsulation**:
   Balance state is maintained in protected attributes (`_balance`) accessible only via read-only property getters (`@property def balance(self)`). Balance adjustments require designated `deposit()` or `withdraw()` methods with input validation.

4. **Composition**:
   - The `Bank` class maintains a collection of `Account` instances.
   - Each `Account` instance maintains a collection of `Transaction` audit instances.

---

## Project Structure

```text
.
├── models.py        # Domain entities (Account, SavingsAccount, CheckingAccount, Transaction, Exceptions)
├── bank.py          # Central banking coordinator and JSON persistence controller
├── main.py          # Interactive command-line interface and presentation layer
└── README.md        # Project documentation
```

---

## Getting Started

### Prerequisites
- Python 3.8 or higher installed on your system.

### Running the Application

1. Clone or download the repository to your local machine.
2. Open a terminal and navigate to the project directory:
   ```bash
   cd "Mini Project"
   ```
3. Run the application:
   ```bash
   python main.py
   ```

When launched for the first time without an existing `bank_records.json` file, the system automatically initializes two sample accounts (Alice Smith and Bob Miller) to allow immediate testing.

---

## Tech Stack
- **Language**: Python 3
- **Built-in Modules**: `json`, `datetime`, `os`, `sys`
- **Dependencies**: None (100% Standard Library)
