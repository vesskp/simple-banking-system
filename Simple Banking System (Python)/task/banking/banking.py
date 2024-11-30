import sqlite3
import random

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS card (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0
)
''')
conn.commit()


def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10


def generate_card_number():
    iin = "400000"
    account_number = str(random.randint(0, 999999999)).zfill(9)
    partial_card_number = iin + account_number
    checksum = luhn_checksum(int(partial_card_number + "0"))
    if checksum != 0:
        checksum = 10 - checksum
    return partial_card_number + str(checksum)


def create_account():
    card_number = generate_card_number()
    pin = str(random.randint(0, 9999)).zfill(4)

    cur.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (card_number, pin))
    conn.commit()

    print("Your card has been created")
    print("Your card number:")
    print(card_number)
    print("Your card PIN:")
    print(pin)


def log_into_account():
    print("Enter your card number:")
    card_number = input()
    print("Enter your PIN:")
    pin = input()

    cur.execute('SELECT balance FROM card WHERE number = ? AND pin = ?', (card_number, pin))
    account = cur.fetchone()

    if account:
        print("You have successfully logged in!")
        while True:
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            choice = input()
            if choice == "1":
                check_balance(card_number)
            elif choice == "2":
                add_income(card_number)
            elif choice == "3":
                do_transfer(card_number)
            elif choice == "4":
                close_account(card_number)
                break
            elif choice == "5":
                print("You have successfully logged out!")
                break
            elif choice == "0":
                exit()
    else:
        print("Wrong card number or PIN!")


def check_balance(card_number):
    cur.execute('SELECT balance FROM card WHERE number = ?', (card_number,))
    balance = cur.fetchone()

    if balance:
        print("Balance:", balance[0])
    else:
        print("Account not found!")


def add_income(card_number):
    print("Enter income:")
    income = int(input())

    cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (income, card_number))
    conn.commit()

    print("Income was added!")


def do_transfer(card_number):
    print("Transfer")
    print("Enter card number:")
    target_card_number = input("Enter card number:")

    if target_card_number == card_number:
        print("You can't transfer money to the same account!")
        return

    if luhn_checksum(int(target_card_number)) != 0:
        print("Probably you made a mistake in the card number. Please try again!")
        return

    cur.execute('SELECT balance FROM card WHERE number = ?', (target_card_number,))
    target_account = cur.fetchone()

    if not target_account:
        print("Such a card does not exist.")
        return

    print("Enter how much money you want to transfer:")
    amount = int(input())

    cur.execute('SELECT balance FROM card WHERE number = ?', (card_number,))
    current_balance = cur.fetchone()[0]

    if amount > current_balance:
        print("Not enough money!")
        return

    cur.execute('UPDATE card SET balance = balance - ? WHERE number = ?', (amount, card_number))
    cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (amount, target_card_number))
    conn.commit()

    print("Success!")


def close_account(card_number):
    cur.execute('DELETE FROM card WHERE number = ?', (card_number,))
    conn.commit()

    print("The account has been closed!")


def main():
    while True:
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        choice = input()
        if choice == "1":
            create_account()
        elif choice == "2":
            log_into_account()
        elif choice == "0":
            print("Bye!")
            break


if __name__ == "__main__":
    main()

conn.close()
