import json
from datetime import datetime

EXPENSES_FILE = "expenses.json"


def load_expenses():
    """Load expenses from JSON file."""
    try:
        with open(EXPENSES_FILE, "r") as file:
            expenses = json.load(file)
            # Ensure consistency in field names
            for exp in expenses:
                if "desc" in exp:
                    exp["description"] = exp.pop("desc")
            return expenses
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_expenses(expenses):
    """Save expenses to JSON file."""
    with open(EXPENSES_FILE, "w") as file:
        json.dump(expenses, file, indent=4)


def add_expense(amount, category, description="", date=None):
    """Add a new expense."""
    expenses = load_expenses()

    # Ensure amount is stored as a float
    try:
        amount = float(amount)
    except ValueError:
        print("❌ Invalid amount. Please enter a number.")
        return

    # Find the next available unique ID
    expense_id = max((exp["id"] for exp in expenses), default=0) + 1

    date = date or str(datetime.today().date())  # Default to today's date

    new_expense = {
        "id": expense_id,
        "amount": amount,
        "category": category.capitalize(),
        "description": description,
        "date": date
    }

    expenses.append(new_expense)
    save_expenses(expenses)

    print(
        f"✅ Expense added: 💰 {amount} in 📂 {category} ({description if description else '-'}) on 📅 {date}")


def view_expenses():
    """Display all expenses."""
    expenses = load_expenses()
    if not expenses:
        print("📂 No expenses found.")
        return

    print("\n📜 Expense History:\n")
    for exp in expenses:
        print(
            f"{exp['id']}. 💰 {exp['amount']} - 📂 {exp['category']} - 📝 {exp['description'] or '-'} - 📅 {exp['date']}")


def delete_expense(expense_id):
    """Delete an expense by ID."""
    expenses = load_expenses()

    # Convert input to integer
    try:
        expense_id = int(expense_id)
    except ValueError:
        print("❌ Invalid expense ID.")
        return

    # Find the expense to delete
    for exp in expenses:
        if exp["id"] == expense_id:
            expenses.remove(exp)
            save_expenses(expenses)
            print(f"🗑️ Expense {expense_id} deleted successfully!")
            return

    print("❌ Expense ID not found.")


def show_summary():
    """Show expense summary by category."""
    expenses = load_expenses()
    summary = {}

    for exp in expenses:
        category = exp["category"]
        summary[category] = summary.get(category, 0) + float(exp["amount"])

    if not summary:
        print("📭 No expenses to summarize.")
        return

    print("\n📊 Expense Summary:")
    for category, total in summary.items():
        print(f"📂 {category}: 💰 {total:.2f}")
