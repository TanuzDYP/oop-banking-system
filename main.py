import sys
from bank import Bank
from models import BankingError, SavingsAccount, CheckingAccount


def prompt_text(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def prompt_float(message, min_value=0.0):
    while True:
        raw_val = input(message).strip()
        try:
            val = float(raw_val)
            if val < min_value:
                print(f"Value must be at least {min_value:.2f}.")
                continue
            return val
        except ValueError:
            print("Invalid input. Please enter a valid numerical value.")


def display_account_card(account):
    line = "-" * 50
    print("\n" + line)
    print(f"ACCOUNT DETAILS: #{account.account_number}")
    print(line)
    print(f"Holder Name      : {account.holder_name}")
    print(f"Account Type     : {account.account_type}")
    print(f"Current Balance  : ${account.balance:.2f}")

    if isinstance(account, SavingsAccount):
        print(f"Annual Interest  : {account.interest_rate * 100:.1f}%")
        print(f"Minimum Balance  : ${account.minimum_balance:.2f}")
    elif isinstance(account, CheckingAccount):
        print(f"Overdraft Limit  : ${account.overdraft_limit:.2f}")
        print(f"Overdraft Fee    : ${account.overdraft_fee:.2f}")
        available = account.balance + account.overdraft_limit
        print(f"Available Credit : ${available:.2f}")
    print(line)


def display_statement(account):
    line = "=" * 80
    print("\n" + line)
    print(f"OFFICIAL STATEMENT: #{account.account_number} ({account.holder_name})")
    print(f"Type: {account.account_type} | Balance: ${account.balance:.2f}")
    print(line)
    print(f"{'Date & Time':<20} | {'Type':<12} | {'Amount ($)':<12} | {'Balance ($)':<12} | {'Description'}")
    print("-" * 80)
    if not account.transactions:
        print("No transactions on record.")
    else:
        for tx in account.transactions:
            print(
                f"{tx.timestamp:<20} | "
                f"{tx.tx_type:<12} | "
                f"{tx.amount:>10.2f}   | "
                f"{tx.balance_after:>10.2f}   | "
                f"{tx.description}"
            )
    print(line + "\n")


def print_accounts_table(bank):
    accounts = bank.list_all_accounts()
    line = "-" * 75
    print("\n" + line)
    print(f"{'Acc #':<8} | {'Holder Name':<20} | {'Type':<10} | {'Balance ($)':<12} | {'Status/Note'}")
    print(line)
    if not accounts:
        print("No registered accounts in system.")
    else:
        for acc in accounts:
            note = ""
            if isinstance(acc, SavingsAccount):
                note = f"Min ${acc.minimum_balance:.0f}"
            elif isinstance(acc, CheckingAccount):
                if acc.balance < 0:
                    note = "OVERDRAWN"
                else:
                    note = f"OD Limit ${acc.overdraft_limit:.0f}"
            print(f"{acc.account_number:<8} | {acc.holder_name:<20} | {acc.account_type:<10} | {acc.balance:>11.2f}  | {note}")
    print(line + "\n")


def menu_open_account(bank):
    print("\n--- OPEN NEW ACCOUNT ---")
    print("1. Savings Account (Earns Interest, Minimum Balance Rule)")
    print("2. Checking Account (Overdraft Protection, Zero Minimum)")
    choice = input("Select account category (1 or 2): ").strip()

    if choice not in ("1", "2"):
        print("Invalid choice. Returning to main menu.")
        return

    name = prompt_text("Enter primary account holder full name: ")

    if choice == "1":
        initial = prompt_float("Enter initial opening deposit (minimum $100): ", min_value=100.0)
        account = bank.create_savings_account(name, initial_balance=initial)
    else:
        initial = prompt_float("Enter initial opening deposit (minimum $25): ", min_value=25.0)
        account = bank.create_checking_account(name, initial_balance=initial)

    print("\nAccount successfully created!")
    display_account_card(account)


def menu_view_account(bank):
    acc_num = prompt_text("Enter account number: ")
    try:
        acc = bank.get_account(acc_num)
        display_account_card(acc)
    except BankingError as err:
        print(f"Error: {err}")


def menu_deposit(bank):
    acc_num = prompt_text("Enter account number: ")
    try:
        acc = bank.get_account(acc_num)
        amount = prompt_float(f"Enter deposit amount for {acc.holder_name}: ", min_value=0.01)
        note = input("Enter optional transaction note (press Enter for default): ").strip()
        description = note if note else "Counter Deposit"
        new_balance = bank.deposit(acc_num, amount, description)
        print(f"Deposit successful. New balance for #{acc_num}: ${new_balance:.2f}")
    except BankingError as err:
        print(f"Transaction failed: {err}")


def menu_withdraw(bank):
    acc_num = prompt_text("Enter account number: ")
    try:
        acc = bank.get_account(acc_num)
        amount = prompt_float(f"Enter withdrawal amount for {acc.holder_name}: ", min_value=0.01)
        note = input("Enter optional transaction note (press Enter for default): ").strip()
        description = note if note else "Counter Withdrawal"
        new_balance = bank.withdraw(acc_num, amount, description)
        print(f"Withdrawal processed successfully. New balance for #{acc_num}: ${new_balance:.2f}")
    except BankingError as err:
        print(f"Transaction rejected: {err}")


def menu_transfer(bank):
    print("\n--- FUND TRANSFER ---")
    sender_num = prompt_text("Enter source (sender) account number: ")
    receiver_num = prompt_text("Enter destination (receiver) account number: ")
    amount = prompt_float("Enter amount to transfer: ", min_value=0.01)

    try:
        bank.transfer(sender_num, receiver_num, amount)
        print(f"Successfully transferred ${amount:.2f} from #{sender_num} to #{receiver_num}.")
    except BankingError as err:
        print(f"Transfer halted: {err}")


def menu_statement(bank):
    acc_num = prompt_text("Enter account number: ")
    try:
        acc = bank.get_account(acc_num)
        display_statement(acc)
    except BankingError as err:
        print(f"Error: {err}")


def menu_apply_interest(bank):
    print("\nCalculating and posting annual interest across all active savings accounts...")
    results = bank.apply_interest_all_savings()
    if not results:
        print("No eligible savings accounts with positive balance found.")
        return
    print(f"Interest credited to {len(results)} account(s):")
    for acc_num, name, interest, balance in results:
        print(f" - #{acc_num} ({name}): +${interest:.2f} | New Balance: ${balance:.2f}")


def run():
    bank = Bank()

    while True:
        print("\n" + "=" * 50)
        print(f"     {bank.name.upper()} MANAGEMENT SYSTEM")
        print("=" * 50)
        print("1. Open New Account")
        print("2. Search & View Account")
        print("3. Deposit Funds")
        print("4. Withdraw Funds")
        print("5. Transfer Between Accounts")
        print("6. View Detailed Account Statement")
        print("7. Post Interest to All Savings Accounts")
        print("8. View All Accounts Directory")
        print("9. Exit")
        print("-" * 50)

        choice = input("Enter choice (1-9): ").strip()

        if choice == "1":
            menu_open_account(bank)
        elif choice == "2":
            menu_view_account(bank)
        elif choice == "3":
            menu_deposit(bank)
        elif choice == "4":
            menu_withdraw(bank)
        elif choice == "5":
            menu_transfer(bank)
        elif choice == "6":
            menu_statement(bank)
        elif choice == "7":
            menu_apply_interest(bank)
        elif choice == "8":
            print_accounts_table(bank)
        elif choice == "9":
            bank.save_to_file()
            print("All records safely committed to storage. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid selection. Please choose an option from 1 to 9.")


if __name__ == "__main__":
    run()
