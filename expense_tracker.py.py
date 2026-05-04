import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from tkcalendar import DateEntry

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("900x600")
        
        # Файл для хранения данных
        self.data_file = "expenses.json"
        self.expenses = self.load_expenses()
        
        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_table_frame()
        self.create_stats_frame()
        
        # Загрузка данных в таблицу
        self.refresh_table()
    
    def create_input_frame(self):
        """Создание фрейма для ввода данных"""
        input_frame = tk.LabelFrame(self.root, text="Добавить расход", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Сумма
        tk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Категория
        tk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        categories = ["Еда", "Транспорт", "Развлечения", "Коммунальные услуги", "Покупки", "Здоровье", "Другое"]
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=categories, width=20)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set("Еда")
        
        # Дата
        tk.Label(input_frame, text="Дата:").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = DateEntry(input_frame, width=18, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавления
        add_btn = tk.Button(input_frame, text="Добавить расход", command=self.add_expense, bg="#4CAF50", fg="white")
        add_btn.grid(row=0, column=6, padx=10, pady=5)
    
    def create_filter_frame(self):
        """Создание фрейма для фильтрации"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по категории
        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar(value="Все")
        categories = ["Все", "Еда", "Транспорт", "Развлечения", "Коммунальные услуги", "Покупки", "Здоровье", "Другое"]
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, values=categories, width=20)
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Фильтр по дате
        tk.Label(filter_frame, text="Дата от:").grid(row=0, column=2, padx=5, pady=5)
        self.start_date = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(filter_frame, text="Дата до:").grid(row=0, column=4, padx=5, pady=5)
        self.end_date = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка фильтрации
        filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter, bg="#2196F3", fg="white")
        filter_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Кнопка сброса фильтра
        reset_btn = tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter, bg="#FF9800", fg="white")
        reset_btn.grid(row=0, column=7, padx=10, pady=5)
    
    def create_table_frame(self):
        """Создание таблицы для отображения расходов"""
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание Treeview
        columns = ("ID", "Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Сумма", text="Сумма (₽)")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        
        self.tree.column("ID", width=50)
        self.tree.column("Сумма", width=150)
        self.tree.column("Категория", width=150)
        self.tree.column("Дата", width=150)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка удаления
        delete_btn = tk.Button(self.root, text="Удалить выбранную запись", command=self.delete_expense, bg="#f44336", fg="white")
        delete_btn.pack(pady=5)
    
    def create_stats_frame(self):
        """Создание фрейма для статистики"""
        stats_frame = tk.LabelFrame(self.root, text="Статистика", padx=10, pady=10)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(stats_frame, text="Общая сумма за период:", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        self.total_label = tk.Label(stats_frame, text="0.00 ₽", font=("Arial", 12, "bold"), fg="#4CAF50")
        self.total_label.pack(side="left", padx=10)
    
    def validate_amount(self, amount):
        """Проверка корректности суммы"""
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return False, "Сумма должна быть положительным числом"
            return True, amount_float
        except ValueError:
            return False, "Сумма должна быть числом"
    
    def add_expense(self):
        """Добавление нового расхода"""
        # Получение данных
        amount = self.amount_entry.get()
        category = self.category_var.get()
        date = self.date_entry.get()
        
        # Валидация
        is_valid, result = self.validate_amount(amount)
        if not is_valid:
            messagebox.showerror("Ошибка", result)
            return
        
        amount_float = result
        
        # Проверка даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты")
            return
        
        # Создание записи
        expense_id = len(self.expenses) + 1
        expense = {
            "id": expense_id,
            "amount": amount_float,
            "category": category,
            "date": date
        }
        
        self.expenses.append(expense)
        self.save_expenses()
        self.refresh_table()
        
        # Очистка поля суммы
        self.amount_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Расход добавлен!")
    
    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        # Получение ID выбранной записи
        item = self.tree.item(selected[0])
        expense_id = int(item['values'][0])
        
        # Удаление из списка
        self.expenses = [e for e in self.expenses if e['id'] != expense_id]
        
        # Обновление ID
        for i, expense in enumerate(self.expenses):
            expense['id'] = i + 1
        
        self.save_expenses()
        self.refresh_table()
        messagebox.showinfo("Успех", "Запись удалена!")
    
    def apply_filter(self):
        """Применение фильтров"""
        filtered_expenses = self.expenses.copy()
        
        # Фильтр по категории
        category_filter = self.filter_category_var.get()
        if category_filter != "Все":
            filtered_expenses = [e for e in filtered_expenses if e['category'] == category_filter]
        
        # Фильтр по дате
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        
        if start_date:
            filtered_expenses = [e for e in filtered_expenses if e['date'] >= start_date]
        
        if end_date:
            filtered_expenses = [e for e in filtered_expenses if e['date'] <= end_date]
        
        self.update_table(filtered_expenses)
        self.update_total(filtered_expenses)
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_category_var.set("Все")
        self.refresh_table()
    
    def refresh_table(self):
        """Обновление таблицы всеми данными"""
        self.update_table(self.expenses)
        self.update_total(self.expenses)
    
    def update_table(self, expenses):
        """Обновление таблицы данными"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление данных
        for expense in expenses:
            self.tree.insert("", "end", values=(
                expense['id'],
                f"{expense['amount']:.2f}",
                expense['category'],
                expense['date']
            ))
    
    def update_total(self, expenses):
        """Обновление общей суммы"""
        total = sum(expense['amount'] for expense in expenses)
        self.total_label.config(text=f"{total:.2f} ₽")
    
    def save_expenses(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_expenses(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                return []
        return []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()