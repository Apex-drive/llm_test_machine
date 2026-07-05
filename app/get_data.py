from tkinter import filedialog
from itertools import cycle
import aiofiles
import os


class file_get:
    def __init__(self):
        self.proxy_servers = ""
        self.prompt_data = ""
        self.file_path_prompt = ""
        self.file_path_proxy = ""
        self.file_path_download = ""
        self.prompts_json = {"messages": ""}
        self.count = 0
        self.count_proxy = 0
        self.lst = []
        self.lst_proxy = []
        self.finish = False

    def file_txt_input_prompt(self, app_instance):
        """Получение файла с промтами для запросов"""
        old_path_prompt = self.file_path_prompt

        new_file_path = filedialog.askopenfilename(
            title="Выберите файл",
            initialdir="/",
            filetypes=[("Text files", "*.txt")],
        )
        if not new_file_path:
            if old_path_prompt:
                return
            return

        self.file_path_prompt = new_file_path

        if self.file_path_prompt:
            name_label_prompt = self.file_path_prompt.split('/')[-1]
            if len(name_label_prompt) >= 17:
                name_label_prompt = f'{name_label_prompt[0:12].strip()}... (.txt)'
            else:
                name_label_prompt = f'{name_label_prompt[:-4].strip()} (.txt)'
            app_instance.label_prompt.configure(text=f"Выбрано: {name_label_prompt}")
            if os.path.getsize(self.file_path_prompt) == 0:
                app_instance.flag_file_prompt = True
            else:
                app_instance.flag_file_prompt = False

    async def data_prompt_processing(self, num):
        """Получение промпта в виде json"""
        self.count = 0
        self.lst = []
        async with aiofiles.open(self.file_path_prompt, 'r', encoding='utf-8') as file:
            prompts = await file.readlines()
            for msg in cycle(prompts):
                self.prompts_json = {
                    "messages": [
                        {"role": "user", "content": msg.replace('\n', '')}
                    ]
                }
                self.lst.append(self.prompts_json)
                self.count += 1
                if self.count >= int(num):
                    break

    async def data_proxy_processing(self, num):
        """Получение proxy"""
        self.count_proxy = 0
        self.lst_proxy = []
        async with aiofiles.open(self.file_path_proxy, 'r', encoding='utf-8') as file:
            proxy = await file.readlines()
            for prox in cycle(proxy):
                self.lst_proxy.append(prox)
                self.count_proxy += 1
                if self.count_proxy >= int(num):
                    break

    def file_txt_input_proxy(self, app_instance):
        """Получение файла с прокси серверами"""

        old_path_prompt = self.file_path_proxy

        new_file_path = filedialog.askopenfilename(
            title="Выберите файл",
            initialdir="/",
            filetypes=[("Text files", "*.txt")],
        )

        if not new_file_path:
            if old_path_prompt:
                return
            return

        self.file_path_proxy = new_file_path

        if self.file_path_proxy:
            name = self.file_path_proxy.split('/')[-1]
            if len(name) >= 17:
                name = f'{name[0:12].strip()}... (.txt)'
            else:
                name = f'{name[:-4].strip()} (.txt)'
            app_instance.label_proxy.configure(text=f"Выбрано: {name}")

            if os.path.getsize(self.file_path_proxy) == 0:
                app_instance.flag_file_proxy = True
                app_instance.use_proxy = False
            else:
                app_instance.flag_file_proxy = False
                app_instance.use_proxy = True

    def download(self, result):
        """Скачивание результата теста"""
        self.file_path_download = filedialog.asksaveasfilename(
            title="Сохранить файл как...",
            initialfile="result",
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt")
            ]
        )

        if self.file_path_download:
            with open(self.file_path_download, 'w', encoding='utf-8') as file_add:
                for count, item in enumerate(result, 1):
                    file_add.write(
                        f"Запрос №{count}: ответ: {item[0]}, адрес: {item[1]}, статус: {item[2]}, proxy: {item[3]}\n")
            os.startfile(self.file_path_download)
