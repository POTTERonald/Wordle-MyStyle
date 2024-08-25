import tkinter as tk
from tkinter import messagebox
import random
from string import ascii_uppercase

NUM_LETTERS = 5
NUM_GUESSES = 6
THEME_FILES = {
    "Name": r"C:\Users\shrey\Downloads\names.txt",
    "Place": r"C:\Users\shrey\Downloads\places.txt",
    "Animal": r"C:\Users\shrey\Downloads\animal.txt",
    "Thing": r"C:\Users\shrey\Downloads\thing.txt"
}

class WordleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wyrdl - Tkinter Edition")
        self.geometry("400x300")  # Adjusted for theme selection screen
        self.create_theme_selection_widgets()

    def create_theme_selection_widgets(self):
        tk.Label(self, text="Welcome to Wyrdl! Choose a theme:", font=("Helvetica", 16)).pack(pady=20)
        self.theme_var = tk.StringVar(value=list(THEME_FILES.keys())[0])
        for theme in THEME_FILES.keys():
            tk.Radiobutton(self, text=theme, variable=self.theme_var, value=theme).pack(anchor=tk.W)
        tk.Button(self, text="Start Game", command=self.start_game).pack(pady=20)

    def start_game(self):
        theme = self.theme_var.get()
        word_file = THEME_FILES[theme]
        self.destroy()
        app = GameWindow(word_file)
        app.mainloop()

class GameWindow(tk.Tk):
    def __init__(self, word_file):
        super().__init__()
        self.title("Wyrdl - Tkinter Edition")
        self.geometry("600x500")  # Adjusted for better visibility
        self.word_file = word_file
        self.word = self.get_random_word(self.load_words())
        self.max_guesses = NUM_GUESSES
        self.current_guess = 0
        self.hints_remaining = 3
        self.letter_status = {letter: "lightgrey" for letter in ascii_uppercase}  # Track letter status
        self.create_widgets()
        self.update_header()

    def get_random_word(self, word_list):
        words = [word.upper() for word in word_list if len(word) == NUM_LETTERS]
        return random.choice(words) if words else None

    def load_words(self):
        with open(self.word_file, "r") as file:
            return file.read().splitlines()

    def give_hint(self):
        if self.hints_remaining > 0 and self.current_guess < self.max_guesses:
            for idx in range(NUM_LETTERS):
                if self.labels[self.current_guess][idx].cget("text") == "_":
                    self.labels[self.current_guess][idx].config(text=self.word[idx], bg="lightblue", fg="black")
                    break
            self.hints_remaining -= 1
            self.max_guesses -= 1
            self.hint_button.config(text=f"Hint ({self.hints_remaining})")
            if self.hints_remaining == 0:
                self.hint_button.config(state=tk.DISABLED)
            self.update_header()
            self.check_game_status()

    def create_widgets(self):
        self.header_label = tk.Label(self, text=f"Guess {self.current_guess + 1}", font=("Helvetica", 16))
        self.header_label.pack(pady=10)
        self.guess_frame = tk.Frame(self)
        self.guess_frame.pack(pady=5)
        self.labels = [[tk.Label(self.guess_frame, text="_", width=2, font=("Helvetica", 24), borderwidth=1, relief="solid") for _ in range(NUM_LETTERS)] for _ in range(NUM_GUESSES)]
        for r, row in enumerate(self.labels):
            for c, label in enumerate(row):
                label.grid(row=r, column=c, padx=2, pady=2)
        self.entry = tk.Entry(self, width=10, font=("Helvetica", 24))
        self.entry.pack(pady=10)
        self.submit_button = tk.Button(self, text="Submit", command=self.check_guess)
        self.submit_button.pack(pady=5)
        self.alphabet_frame = tk.Frame(self)
        self.alphabet_frame.pack(pady=5)
        self.alphabet_labels = {}
        for letter in ascii_uppercase:
            label = tk.Label(self.alphabet_frame, text=letter, width=2, font=("Helvetica", 10), bg="lightgrey", relief="solid")
            label.pack(side=tk.LEFT, padx=1, pady=1)
            self.alphabet_labels[letter] = label
        self.hint_button = tk.Button(self, text=f"Hint ({self.hints_remaining})", command=self.give_hint)
        self.hint_button.pack(pady=5)

    def update_header(self):
        self.header_label.config(text=f"Guess {self.current_guess + 1}")

    def update_grid(self, guess):
        word_unmatched = list(self.word)
        current_letter_status = self.letter_status.copy()
        for idx, letter in enumerate(guess):
            if letter == self.word[idx]:
                self.labels[self.current_guess][idx].config(text=letter, bg="green", fg="white")
                word_unmatched[idx] = None
                current_letter_status[letter] = "green"
        for idx, letter in enumerate(guess):
            if self.labels[self.current_guess][idx].cget("bg") != "green":
                if letter in word_unmatched:
                    self.labels[self.current_guess][idx].config(text=letter, bg="yellow", fg="white")
                    word_unmatched[word_unmatched.index(letter)] = None
                    current_letter_status[letter] = "yellow"
                else:
                    self.labels[self.current_guess][idx].config(text=letter, bg="gray", fg="white")
                    current_letter_status[letter] = "gray"
        for letter, color in current_letter_status.items():
            if color != self.letter_status[letter]:
                self.alphabet_labels[letter].config(bg=color, fg="black")
                self.letter_status[letter] = color

    def check_guess(self):
        guess = self.entry.get().upper()
        if len(guess) != NUM_LETTERS:
            messagebox.showwarning("Invalid Guess", f"Your guess must be {NUM_LETTERS} letters.")
            return
        self.update_grid(guess)
        if guess == self.word:
            self.end_game(won=True)
        else:
            self.current_guess += 1
            self.update_header()
            self.entry.delete(0, tk.END)
            self.check_game_status()

    def check_game_status(self):
        if self.current_guess >= self.max_guesses:
            self.end_game(won=False)

    def end_game(self, won):
        if won:
            messagebox.showinfo("Congratulations!", f"Correct, the word is {self.word}!")
        else:
            messagebox.showinfo("Game Over", f"Sorry, the word was {self.word}.")
        self.show_end_game_menu()

    def show_end_game_menu(self):
        menu = tk.Toplevel(self)
        menu.title("Game Over")
        menu.geometry("200x150")
        tk.Label(menu, text="Would you like to play again?").pack(pady=10)
        tk.Button(menu, text="New Game", command=self.new_game).pack(pady=5)
        tk.Button(menu, text="Exit", command=self.quit).pack(pady=5)

    def new_game(self):
        self.destroy()
        app = WordleApp()
        app.mainloop()

    def quit(self):
        self.destroy()
        self.quit()

if __name__ == "__main__":
    app = WordleApp()
    app.mainloop()
