import json
import os
from models import (
    Account,
    SavingsAccount,
    CheckingAccount,
    Transaction,
    AccountNotFoundError,
    InvalidAmountError,
)


class Bank:
    def __init__(self, name="Apex Capital Bank", storage_file="bank_records.json"):
        self.name = name
        self.storage_file = storage_file
        self.accounts = {}
        self._account_counter = 1001
        self.load_from_file()
        if not self.accounts:
            self._seed_sample_accounts()

    def _seed_sample_accounts(self):
        self.create_savings_account("Alice Smith", initial_balance=1200.0, interest_rate=0.04, minimum_balance=100.0)
        self.create_checking_account("Bob Miller", initial_balance=450.0, overdraft_limit=250.0, overdraft_fee=20.0)

    def _generate_account_number(self):
        while str(self._account_counter) in self.accounts:
            self._account_counter += 1
        acc_num = str(self._account_counter)
        self._account_counter += 1
        return acc_num

    def create_savings_account(self, holder_name, initial_balance=100.0, interest_rate=0.04, minimum_balance=100.0):
        acc_num = self._generate_account_number()
        account = SavingsAccount(
            account_number=acc_num,
            holder_name=holder_name,
            initial_balance=initial_balance,
            interest_rate=interest_rate,
            minimum_balance=minimum_balance,
        )
        self.accounts[acc_num] = account
        self.save_to_file()
        return account

    def create_checking_account(self, holder_name, initial_balance=50.0, overdraft_limit=250.0, overdraft_fee=20.0):
        acc_num = self._generate_account_number()
        account = CheckingAccount(
            account_number=acc_num,
            holder_name=holder_name,
            initial_balance=initial_balance,
            overdraft_limit=overdraft_limit,
            overdraft_fee=overdraft_fee,
        )
        self.accounts[acc_num] = account
        self.save_to_file()
        return account

    def get_account(self, account_number):
        acc_key = str(account_number).strip()
        if acc_key not in self.accounts:
            raise AccountNotFoundError(f"Account number '{acc_key}' was not found in the records.")
        return self.accounts[acc_key]

    def deposit(self, account_number, amount, description="Deposit"):
        account = self.get_account(account_number)
        account.deposit(amount, description)
        self.save_to_file()
        return account.balance

    def withdraw(self, account_number, amount, description="Withdrawal"):
        account = self.get_account(account_number)
        account.withdraw(amount, description)
        self.save_to_file()
        return account.balance

    def transfer(self, sender_acc_num, receiver_acc_num, amount):
        if str(sender_acc_num).strip() == str(receiver_acc_num).strip():
            raise InvalidAmountError("Source and destination accounts must be different.")
        
        sender = self.get_account(sender_acc_num)
        receiver = self.get_account(receiver_acc_num)
        amount = float(amount)

        if amount <= 0:
            raise InvalidAmountError("Transfer amount must be strictly greater than zero.")

        sender.withdraw(amount, f"Transfer to #{receiver.account_number} ({receiver.holder_name})")
        receiver.deposit(amount, f"Transfer from #{sender.account_number} ({sender.holder_name})")
        self.save_to_file()
        return True

    def apply_interest_all_savings(self):
        applied = []
        for account in self.accounts.values():
            if isinstance(account, SavingsAccount):
                interest = account.apply_interest()
                if interest > 0:
                    applied.append((account.account_number, account.holder_name, interest, account.balance))
        if applied:
            self.save_to_file()
        return applied

    def list_all_accounts(self):
        return sorted(self.accounts.values(), key=lambda a: a.account_number)

    def save_to_file(self):
        payload = {
            "account_counter": self._account_counter,
            "accounts": [acc.to_dict() for acc in self.accounts.values()],
        }
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

    def load_from_file(self):
        if not os.path.exists(self.storage_file):
            return
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._account_counter = data.get("account_counter", 1001)
            raw_accounts = data.get("accounts", [])
            for item in raw_accounts:
                acc_type = item.get("account_type")
                if acc_type == "Savings":
                    acc = SavingsAccount(
                        account_number=item["account_number"],
                        holder_name=item["holder_name"],
                        initial_balance=0.0,
                        interest_rate=item.get("interest_rate", 0.04),
                        minimum_balance=item.get("minimum_balance", 100.0),
                    )
                elif acc_type == "Checking":
                    acc = CheckingAccount(
                        account_number=item["account_number"],
                        holder_name=item["holder_name"],
                        initial_balance=0.0,
                        overdraft_limit=item.get("overdraft_limit", 250.0),
                        overdraft_fee=item.get("overdraft_fee", 20.0),
                    )
                else:
                    acc = Account(
                        account_number=item["account_number"],
                        holder_name=item["holder_name"],
                        initial_balance=0.0,
                    )
                acc._balance = float(item["balance"])
                acc.transactions = [
                    Transaction.from_dict(tx) for tx in item.get("transactions", [])
                ]
                self.accounts[acc.account_number] = acc
        except (json.JSONDecodeError, KeyError):
            pass
