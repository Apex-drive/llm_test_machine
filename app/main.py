import customtkinter as ctk
from shared_file import file_shared_prompt_data, post_request
import threading
import asyncio
import time


class Aplication:
    def __init__(self):
        self.root = ctk.CTk()

        self.root.title("llm test")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        self.label_title = ctk.CTkLabel(
            self.root,
            text="LLM TEST",
            font=("Arial", 40, "bold"),
        )
        self.count_test = 0
        self.num = 0
        self.flag_cancel = False
        self.post_request_server = None
        self.use_proxy = False
        self.start_time = 0
        self.end_time = 0
        self.design_app()

    def design_app(self):
        """Создание дизайна приложения"""
        self.label_title.pack(side="top", fill="none", pady=(30, 0))
        self.url_entry = ctk.CTkEntry(self.root, width=300, height=40, placeholder_text='Введите URL...')
        self.url_entry.pack(side="top", anchor="nw", padx=(100, 0), pady=(110, 0))

        self.show_btn_api_key = ctk.CTkButton(
            self.root,
            text="👁",
            width=28,
            height=40,
            fg_color="#343638",
            hover_color="#343638",
            text_color="#DCE4EE",
            border_width=2,
            border_color="#565B5E",
            command=self.show_btn
        )
        self.show_btn_api_key.place(x=373, y=236)
        self.flag_visible = False

        self.api_entry = ctk.CTkEntry(self.root,
                                      width=268,
                                      height=40,
                                      placeholder_text='Введите API_KEY (опционально)...',
                                      show='•')
        self.api_entry.pack(side="top", anchor="nw", padx=(100, 0), pady=(10, 0))
        validate_command = self.root.register(self.char_label)
        validate_command_second = self.root.register(self.char_label_second)
        self.number_entry = ctk.CTkEntry(
            self.root,
            width=149,
            height=40,
            placeholder_text="Кол-во запросов (шт.)",
            validate="key",
            validatecommand=(validate_command, "%S", "%P")
        )
        self.number_entry.pack(side="top", anchor="nw", padx=(101, 0), pady=(10, 0))

        self.count_number_entry = ctk.CTkLabel(
            self.root,
            font=("Arial", 11, "bold")
        )

        self.time_label = ctk.CTkLabel(
            self.root,
            font=("Arial", 11, "bold")
        )

        self.number_entry_sec = ctk.CTkEntry(
            self.root,
            width=149,
            height=40,
            placeholder_text="Время теста (секунд)",
            validate="key",
            validatecommand=(validate_command_second, "%S", "%P")
        )
        self.number_entry_sec.place(x=254, y=286)

        self.result_file = ctk.CTkButton(
            self.root,
            text='Скачать результаты',
            width=150,
            height=40,
            fg_color=None,
            hover=False,
            border_color=None,
            command=lambda: file_shared_prompt_data.download(post_request.result())
        )

        self.file_input_btn_proxy = ctk.CTkButton(
            self.root,
            text='Файл c proxy',
            width=120,
            height=30,
            command=lambda: file_shared_prompt_data.file_txt_input_proxy(self)
        )
        self.file_input_btn_proxy.place(x=100, y=335)
        self.flag_file_proxy = True
        self.label_proxy = ctk.CTkLabel(self.root, text="Файл не выбран", font=("Arial", 11, "bold"))
        self.label_proxy.place(x=100, y=365)
        self.label_proxy_1 = ctk.CTkLabel(self.root, text="(опционально)", font=("Arial", 11, "bold"))
        self.label_proxy_1.place(x=100, y=385)

        self.file_input_btn_prompt = ctk.CTkButton(
            self.root,
            text='Файл с prompt',
            width=120,
            height=30,
            command=lambda: file_shared_prompt_data.file_txt_input_prompt(self)
        )

        self.btn_new_test = ctk.CTkButton(
            self.root,
            text='Новый тест',
            width=120,
            height=40,
            command=lambda: self.flag_new_test()
        )

        self.file_input_btn_prompt.place(x=280, y=335)
        self.flag_file_prompt = True
        self.label_prompt = ctk.CTkLabel(self.root, text="Файл не выбран", font=("Arial", 11, "bold"))
        self.label_prompt.place(x=280, y=365)
        self.name_label_prompt = ""

        self.progress = ctk.CTkProgressBar(
            self.root,
            width=300,
            height=20,
            corner_radius=5,
            progress_color="white"
        )

        self.file_input_btn_start = ctk.CTkButton(
            self.root,
            text='Начать тестирование',
            width=190,
            height=50,
            command=self.data_check_start_test
        )
        self.count = 0
        self.cancel_btn = ctk.CTkButton(
            self.root,
            text="Отмена",
            width=100,
            height=50,
            command=self.cancel_process,
            fg_color="darkred",
            hover_color="darkred",
            text_color="black"
        )
        self.cancel_btn.place(x=300, y=490)
        self.cancel_btn.configure(state="disabled")
        self.file_input_btn_start.place(x=100, y=490)

        self.root.mainloop()

    def show_btn(self):
        """Кнопка скрытия текста в поле ввода api ключа"""
        if self.flag_visible:
            self.api_entry.configure(show="•")
            self.flag_visible = False
        else:
            self.api_entry.configure(show="")
            self.flag_visible = True

    def char_label_second(self, char, current_value):
        """Проверка на число"""
        if current_value == "" or current_value == "Время теста (секунд)":
            return True
        return char.isdigit()

    def char_label(self, char, current_value):
        """Проверка на число"""
        if current_value == "" or current_value == "Кол-во запросов (шт.)":
            return True
        return char.isdigit()

    def data_check_start_test(self):
        """Проверка информации на корректность"""
        if (self.number_entry.get() and self.number_entry.get() != "Кол-во запросов (шт.)") \
                and (self.url_entry.get() and self.url_entry.get() != "Введите URL...") \
                and (self.number_entry_sec.get() and self.number_entry_sec.get() != "Время теста (секунд)"):
            if int(self.number_entry.get()) > 1000000 or \
                    int(self.number_entry_sec.get()) > 86400 or \
                    ("http://" not in self.url_entry.get() and "https://" not in self.url_entry.get()) or \
                    int(self.number_entry_sec.get()) <= 0 or int(self.number_entry.get()) <= 0:
                self.count_number_entry.configure(text="Ошибка не корректные данные!", text_color="red")
                self.count_number_entry.place(x=100, y=465)
            else:
                if self.label_prompt.cget("text") == "Файл не выбран":
                    self.count_number_entry.configure(text="Выберите файл с prompt!", text_color="red")
                    self.count_number_entry.place(x=100, y=465)
                else:
                    if self.flag_file_prompt:
                        self.count_number_entry.configure(text="Файл с prompt пустой!", text_color="red")
                        self.count_number_entry.place(x=100, y=465)
                    else:
                        if self.label_proxy.cget("text") != "Файл не выбран" and self.flag_file_proxy:
                            self.count_number_entry.configure(text="Файл с proxy пустой!", text_color="red")
                            self.count_number_entry.place(x=100, y=465)
                        else:
                            self.start_test()
        else:
            self.count_number_entry.configure(text="Ошибка заполните все поля!", text_color="red")
            self.count_number_entry.place(x=100, y=465)

    def start_test(self):
        """Начало теста"""
        self.start_time = time.perf_counter()
        api = self.api_entry.get().strip()
        if api != "" and api != "Введите API_KEY (опционально)...":
            api_key = {
                "Authorization": f"Bearer {self.api_entry.get()}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        else:
            api_key = None

        if not post_request.start:
            self.flag_cancel = False
            post_request.flag_cancel_progress = False
        self.num = int(self.number_entry.get())
        asyncio.run(file_shared_prompt_data.data_prompt_processing(
            self.number_entry.get()
        ))
        if self.use_proxy:
            asyncio.run(file_shared_prompt_data.data_proxy_processing(
                self.number_entry.get()
            ))
            self.post_request_server = threading.Thread(
                target=lambda: self._run_async_in_thread(post_request.run, self.url_entry.get(),
                                                         file_shared_prompt_data.lst,
                                                         self.number_entry_sec.get(),
                                                         self.number_entry.get(), file_shared_prompt_data.lst_proxy,
                                                         api_key),
                daemon=True
            )
        else:
            self.post_request_server = threading.Thread(
                target=lambda: self._run_async_in_thread(post_request.run, self.url_entry.get(),
                                                         file_shared_prompt_data.lst,
                                                         self.number_entry_sec.get(),
                                                         self.number_entry.get(), api_key),
                daemon=True
            )
        self.post_request_server.start()
        self.check_error()
        self.cancel_btn.place(x=300, y=490)
        self.file_input_btn_start.configure(state="disabled", text="⏳ Тест выполняется...")
        self.cancel_btn.configure(state="normal", fg_color="red")
        self.file_input_btn_start.place(x=100, y=490)
        self.api_entry.configure(state="disabled")
        self.file_input_btn_prompt.configure(state="disabled")
        self.file_input_btn_proxy.configure(state="disabled")
        self.number_entry.configure(state="disabled")
        self.number_entry_sec.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.count_number_entry.configure(text=f"{post_request.count_test}/{self.num}",
                                          text_color="#DCE4EE")
        self.count_number_entry.place(x=100, y=435)
        self.progress.set(post_request.count_test)
        self.progress.place(x=100, y=418)
        self.check()

    def check_error(self):
        """Проверка ошибок"""
        if post_request.error() != "":
            self.cancel_process()
        else:
            self.root.after(100, self.check_error)

    def _run_async_in_thread(self, async_func, *args):
        """Запуск асинхронной функции в отдельном потоке"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(async_func(*args))
        finally:
            loop.close()

    def flag_new_test(self):
        """Начало нового теста"""
        self.progress.place_forget()
        self.count_number_entry.place_forget()
        self.file_input_btn_start.configure(state="normal", text="Начать тестирование")
        self.result_file.place_forget()
        self.btn_new_test.place_forget()
        self.time_label.place_forget()
        self.number_entry_sec.configure(state="normal")
        self.url_entry.configure(state="normal")
        self.cancel_btn.configure(state="disabled", fg_color="darkred")
        self.api_entry.configure(state="normal")
        self.file_input_btn_prompt.configure(state="normal")
        self.file_input_btn_proxy.configure(state="normal")
        self.number_entry.configure(state="normal")

    def check(self):
        """Проверка флага"""
        if not self.flag_cancel:
            if post_request.error() == "":
                if post_request.finish:
                    self.count_number_entry.configure(text=f"{post_request.count_test}/{self.num}")
                    self.count_number_entry.place(x=100, y=435)
                    self.progress.set(post_request.count_test / int(self.number_entry.get()))
                    self.check_finish()
                else:
                    self.root.after(100, self.check)
                    self.count_number_entry.configure(text=f"{post_request.count_test}/{self.num}")
                    self.count_number_entry.place(x=100, y=435)
                    self.progress.set(post_request.count_test / int(self.number_entry.get()))
            else:
                self.count_number_entry.configure(text=post_request.error(), text_color="red")
                self.count_number_entry.place(x=100, y=465)
                self.progress.place_forget()

    def check_finish(self):
        """Проверка о завершении теста"""
        post_request.finish = False
        self.end_time = time.perf_counter()
        self.time_label.configure(text=f"Время теста: {self.end_time - self.start_time: .1f} сек.")
        self.time_label.place(x=100, y=465)
        self.btn_new_test.place(x=100, y=560)
        self.result_file.place(x=250, y=560)
        self.file_input_btn_start.configure(state="disabled", text="Начать тестирование")
        self.cancel_btn.configure(state="disabled", fg_color="darkred")

    def cancel_process(self):
        """Отмена теста"""
        self.flag_cancel = True
        post_request.flag_cancel_progress = True
        if post_request.error() != "":
            self.count_number_entry.configure(text=post_request.error(), text_color="red")
            self.count_number_entry.place(x=100, y=465)
        else:
            self.count_number_entry.configure(text="Вы остановили процесс!", text_color="red")
            self.count_number_entry.place(x=100, y=465)
        self.progress.place_forget()
        self.cancel_btn.configure(state="disabled", fg_color="darkred")
        self.api_entry.configure(state="normal")
        self.file_input_btn_prompt.configure(state="normal")
        self.file_input_btn_proxy.configure(state="normal")
        self.number_entry.configure(state="normal")
        self.number_entry_sec.configure(state="normal")
        self.url_entry.configure(state="normal")
        self.file_input_btn_start.configure(state="disabled", text="Ожидание...")
        self.root.after(3000, self.start_btn_turn_on)

    def start_btn_turn_on(self):
        """Ожидание между отменой и началом нового теста"""
        self.file_input_btn_start.configure(state="normal", text="Начать тестирование")


if __name__ == "__main__":
    app = Aplication()
