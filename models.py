import datetime


class BankingError(Exception):
    pass


class InsufficientFundsError(BankingError):
    pass


class AccountNotFoundError(BankingError):
    pass


class InvalidAmountError(BankingError):
    pass


class Transaction:
    def __init__(self, tx_type, amount, balance_after, description=""):
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.tx_type = tx_type
        self.amount = float(amount)
        self.balance_after = float(balance_after)
        self.description = description

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "tx_type": self.tx_type,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        tx = cls(
            tx_type=data["tx_type"],
            amount=data["amount"],
            balance_after=data["balance_after"],
            description=data.get("description", ""),
        )
        tx.timestamp = data["timestamp"]
        return tx


class Account:
    def __init__(self, account_number, holder_name, initial_balance=0.0):
        if initial_balance < 0:
            raise InvalidAmountError("Initial balance cannot be negative.")
        self.account_number = str(account_number)
        self.holder_name = holder_name.strip()
        self._balance = float(initial_balance)
        self.transactions = []
        if initial_balance > 0:
            self._record_transaction("DEPOSIT", initial_balance, "Initial Opening Balance")

    @property
    def balance(self):
        return self._balance

    @property
    def account_type(self):
        return "Standard"

    def _record_transaction(self, tx_type, amount, description=""):
        record = Transaction(tx_type, amount, self._balance, description)
        self.transactions.append(record)

    def deposit(self, amount, description="Deposit"):
        amount = float(amount)
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be greater than zero.")
        self._balance += amount
        self._record_transaction("DEPOSIT", amount, description)
        return self._balance

    def withdraw(self, amount, description="Withdrawal"):
        amount = float(amount)
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be greater than zero.")
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Cannot withdraw ${amount:.2f}. Available balance: ${self._balance:.2f}."
            )
        self._balance -= amount
        self._record_transaction("WITHDRAWAL", amount, description)
        return self._balance

    def to_dict(self):
        return {
            "account_type": self.account_type,
            "account_number": self.account_number,
            "holder_name": self.holder_name,
            "balance": self._balance,
            "transactions": [tx.to_dict() for tx in self.transactions],
        }


class SavingsAccount(Account):
    def __init__(self, account_number, holder_name, initial_balance=0.0, interest_rate=0.04, minimum_balance=100.0):
        super().__init__(account_number, holder_name, initial_balance)
        self.interest_rate = float(interest_rate)
        self.minimum_balance = float(minimum_balance)

    @property
    def account_type(self):
        return "Savings"

    def withdraw(self, amount, description="Withdrawal"):
        amount = float(amount)
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be greater than zero.")
        if self._balance - amount < self.minimum_balance:
            raise InsufficientFundsError(
                f"Withdrawal denied. Minimum balance requirement is ${self.minimum_balance:.2f}. Current balance: ${self._balance:.2f}."
            )
        self._balance -= amount
        self._record_transaction("WITHDRAWAL", amount, description)
        return self._balance

    def apply_interest(self):
        interest_amount = round(self._balance * self.interest_rate, 2)
        if interest_amount > 0:
            self._balance += interest_amount
            self._record_transaction("INTEREST", interest_amount, f"Annual interest yield ({self.interest_rate * 100:.1f}%)")
        return interest_amount

    def to_dict(self):
        data = super().to_dict()
        data["interest_rate"] = self.interest_rate
        data["minimum_balance"] = self.minimum_balance
        return data


class CheckingAccount(Account):
    def __init__(self, account_number, holder_name, initial_balance=0.0, overdraft_limit=250.0, overdraft_fee=20.0):
        super().__init__(account_number, holder_name, initial_balance)
        self.overdraft_limit = float(overdraft_limit)
        self.overdraft_fee = float(overdraft_fee)

    @property
    def account_type(self):
        return "Checking"

    def withdraw(self, amount, description="Withdrawal"):
        amount = float(amount)
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be greater than zero.")
        available_funds = self._balance + self.overdraft_limit
        if amount > available_funds:
            raise InsufficientFundsError(
                f"Withdrawal exceeds overdraft limit. Available limit: ${available_funds:.2f}."
            )
        started_positive = self._balance >= 0
        self._balance -= amount
        self._record_transaction("WITHDRAWAL", amount, description)
        if started_positive and self._balance < 0:
            self._balance -= self.overdraft_fee
            self._record_transaction("FEE", self.overdraft_fee, "Overdraft protection service fee")
        return self._balance

    def to_dict(self):
        data = super().to_dict()
        data["overdraft_limit"] = self.overdraft_limit
        data["overdraft_fee"] = self.overdraft_fee
        return data
