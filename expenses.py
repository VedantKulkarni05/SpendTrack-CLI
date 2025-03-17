import typer
import speech_recognition as sr
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
import json
import os
import keyboard  # For arrow key selection

app = typer.Typer()
console = Console()

EXPENSES_FILE = "expenses.json"

# Function to load expenses


def load_expenses():
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, "r") as f:
            return json.load(f)
    return []

# Function to save expenses


def save_expenses(expenses):
    with open(EXPENSES_FILE, "w") as f:
        json.dump(expenses, f, indent=4)

# Function to get user selection using arrow keys


def get_choice(prompt, choices):
    index = 0
    console.clear()

    while True:
        console.print(f"{prompt} [{'/'.join(choices)}]", style="bold magenta")
        for i, choice in enumerate(choices):
            if i == index:
                console.print(f"👉 [bold cyan]{choice} 👈[/bold cyan]")
            else:
                console.print(f"   {choice}")

        event = keyboard.read_event(suppress=True)

        if event.event_type == keyboard.KEY_DOWN:
            if event.name == "right" or event.name == "down":
                index = (index + 1) % len(choices)
            elif event.name == "left" or event.name == "up":
                index = (index - 1) % len(choices)
            elif event.name == "enter":
                console.print(f"\n✔ Selected: {choices[index]}", style="green")
                return choices[index]
        console.clear()  # Prevents screen clutter

# Function to add expense


@app.command()
def add():
    input_method = get_choice("Choose input method", [
                              "Interactive", "Voice"]).capitalize()

    amount = None
    category = None
    description = ""
    date = ""

    if input_method == "Voice":
        try:
            import pyaudio  # Ensure PyAudio is installed
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                console.print(
                    "🎤 Speak your expense (e.g., '500 Food Lunch today')", style="yellow")
                recognizer.adjust_for_ambient_noise(
                    source)  # Improve recognition
                audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                console.print(f"🎙 Recognized: {text}", style="cyan")
                parts = text.split()
                if len(parts) >= 2:
                    amount = parts[0]
                    category = parts[1].capitalize()
                else:
                    console.print(
                        "❌ Could not extract details. Please use Interactive mode.", style="red")
                    return
            except sr.UnknownValueError:
                console.print(
                    "❌ Could not understand audio. Try again.", style="red")
                return
            except sr.RequestError:
                console.print(
                    "❌ Error connecting to speech recognition service.", style="red")
                return
        except ImportError:
            console.print(
                "❌ PyAudio is missing. Install it using `pip install pyaudio`.", style="red")
            return
    else:
        amount = Prompt.ask("💰 Enter amount")
        category = get_choice("📂 Choose category", [
                              "Food", "Transport", "Shopping", "Bills", "Health", "Entertainment", "Other"]).capitalize()
        description = Prompt.ask("📝 Enter description (optional)", default="")
        date = Prompt.ask("📅 Enter date (YYYY-MM-DD) (optional)", default="")

    if not amount or not category:
        console.print(
            "❌ Missing required fields. Expense not added.", style="red")
        return

    expenses = load_expenses()
    expenses.append({"amount": amount, "category": category,
                    "description": description, "date": date})
    save_expenses(expenses)

    console.print("\n✅ Expense added:", style="green")
    console.print(f"💰 {amount}")
    console.print(f"📂 {category}")
    console.print(f"📝 {description if description else '-'}")
    console.print(f"📅 {date if date else '-'}")

# Function to view expenses


@app.command()
def view():
    expenses = load_expenses()
    if not expenses:
        console.print("📭 No expenses recorded.", style="yellow")
        return

    console.print("\n📜 Expense History:\n", style="bold green")
    for idx, exp in enumerate(expenses, 1):
        console.print(f"{idx}.")
        console.print(f"   💰 {exp['amount']}")
        console.print(f"   📂 {exp['category']}")
        console.print(
            f"   📝 {exp['description'] if exp['description'] else '-'}")
        console.print(f"   📅 {exp['date'] if exp['date'] else '-'}\n")

# Function to delete an expense


@app.command()
def delete():
    expenses = load_expenses()
    if not expenses:
        console.print(
            "📭 No expenses recorded. Nothing to delete.", style="yellow")
        return

    console.print("\n🗑 Select an expense to delete:\n", style="bold red")
    choices = [f"{idx+1}. {exp['category']} - {exp['amount']}" for idx,
               exp in enumerate(expenses)]
    choices.append("Cancel")

    selected = get_choice("Select an expense to delete", choices)

    if selected == "Cancel":
        console.print("🚫 Deletion canceled.", style="yellow")
        return

    index = int(selected.split(".")[0]) - 1

    deleted_expense = expenses.pop(index)
    save_expenses(expenses)

    # Safe access using .get()
    console.print("\n✅ Expense deleted:", style="green")
    console.print(f"💰 {deleted_expense['amount']}")
    console.print(f"📂 {deleted_expense['category']}")
    console.print(f"📝 {deleted_expense.get('description', '-')}")
    console.print(f"📅 {deleted_expense.get('date', '-')}")

# Function to show summary


@app.command()
def summary():
    expenses = load_expenses()
    if not expenses:
        console.print("📭 No expenses recorded.", style="yellow")
        return

    category_totals = {}
    for exp in expenses:
        category_totals[exp["category"]] = category_totals.get(
            exp["category"], 0) + int(exp["amount"])

    table = Table(title="💰 Expense Summary", show_header=True,
                  header_style="bold magenta")
    table.add_column("Category", style="cyan")
    table.add_column("Total Amount", style="green")

    for category, total in category_totals.items():
        table.add_row(category, str(total))

    console.print(table)


if __name__ == "__main__":
    app()
