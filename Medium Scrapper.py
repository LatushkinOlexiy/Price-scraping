import tkinter as tk
import tksheet
import functions_for_scraping as fn

#print(fn.scrape_cycle("кальцій фосфат").head())

class DynamicInputApp:
    def __init__(self, root):
        # window itself
        self.root = root
        self.root.title("Media researcher")
        
        # frames for widgets
        self.text_frame = tk.Frame(root)
        self.text_frame.pack(pady=10)

        self.entries_frame = tk.Frame(root)
        self.entries_frame.pack(pady=10)

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(pady=10)

        # Text to indicate fields
        self.text_expl = tk.Label(self.text_frame, text="        Компонент середовища:      концентрація (г/л): ", font=("Arial", 10))
        self.text_expl.pack(side=tk.LEFT,padx=5)

        # Buttons to add/remove inputs
        self.add_button = tk.Button(self.buttons_frame, text="Add Field", command=self.add_field)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = tk.Button(self.buttons_frame, text="Remove Field", command=self.remove_field)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        # Button to run script
        run_button = tk.Button(self.buttons_frame, text="Run Fields", command=self.run_fields)
        run_button.pack(side=tk.LEFT, padx=5)

        # Output sheet
        global sheet
        sheet = tksheet.Sheet(root,
                      data=[["Your data will appear here", 0,0,0,"www.google.com"]],
                      headers=(["name", "concentration","price per kg","total price","url"]))
        sheet.enable_bindings(("all"))
        sheet.pack(fill="both", expand=True)

        # Track all entry widgets
        self.entries = []

        # Start with one input field
        self.add_field()
    # Add field
    def add_field(self):
        row_frame = tk.Frame(self.entries_frame)
        row_frame.pack(pady=2)

        main_entry = tk.Entry(row_frame, width=30)
        main_entry.pack(side=tk.LEFT, padx=5)

        sub_entry = tk.Entry(row_frame, width=10)
        sub_entry.pack(side=tk.LEFT)

        self.entries.append((main_entry, sub_entry))
        
    # Remove Field
    def remove_field(self):
        if self.entries:
            main_entry, sub_entry = self.entries.pop()
            main_entry.master.destroy()  
    # Get all field requests and run the program
    def run_fields(self):
        values = [main.get() for main, sub in self.entries]
        conc_values = [sub.get() for main, sub in self.entries]
        data_for_table = []
        print("User inputs:", values)
        for value, conc_value in zip(values,conc_values):
            conc_value = float(conc_value)
            new_df = fn.scrape_cycle(value)
            try:
                best_fit = new_df.iloc[0]
            except:
                print("no items retained")
                pass
            print(f"best fit is: {best_fit}")
            new_link = f"{best_fit['link']}"
            new_data_entry = [best_fit['name'],conc_value,best_fit['price per kg'],conc_value*0.001*best_fit['price per kg'],new_link]
            data_for_table.append(new_data_entry)
        print(data_for_table)
        global sheet
        sheet.data = data_for_table
if __name__ == "__main__":
    root = tk.Tk()
    app = DynamicInputApp(root)
    root.mainloop()