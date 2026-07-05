from aiohttp import ClientSession
import asyncio


class post_request:
    def __init__(self):
        self.responses = None
        self.count_test = 0
        self.finish = False
        self.errors = ""
        self.flag_cancel_progress = False
        self.start = False
        self.cancel = False
        self.proxy_lists = None

    async def processing_post_requests(self, url, prompts_json, session, proxy_server, headers):
        """Отправка запроса и получение ответа"""
        try:
            if proxy_server and headers:
                async with session.post(
                        url,
                        json=prompts_json,
                        proxy=proxy_server,
                        headers=headers
                ) as responses:
                    return await self.result_processing(responses, url, proxy_server)

            elif proxy_server:
                async with session.post(
                        url,
                        json=prompts_json,
                        proxy=proxy_server
                ) as responses:
                    return await self.result_processing(responses, url, proxy_server)

            elif headers:
                async with session.post(
                        url,
                        json=prompts_json,
                        headers=headers
                ) as responses:
                    return await self.result_processing(responses, url, proxy_server)

            else:
                async with session.post(
                        url,
                        json=prompts_json
                ) as responses:
                    return await self.result_processing(responses, url, proxy_server)

        except RuntimeError as e:
            if "Session is closed" in str(e):
                self.cancel = True
                return

        except asyncio.CancelledError:
            self.cancel = True

        except Exception:
            self.start = False
            if not self.cancel:
                self.errors = "Ошибка подключения к серверу"

    async def result_processing(self, responses, url, proxy_server):
        """Получение результата в понятном формате"""
        result_data = f"Ошибка: код {responses.status}"
        if responses.status == 200:
            data = await responses.json()
            if 'choices' in data:
                messages = data['choices'][0].get('message', {})
                result_data = messages.get('content', 'Нет ответа')
        self.count_test += 1
        return result_data, url, responses.status, proxy_server

    async def run(self, url, prompts_json, delay_all, num_requests, proxy_list=None, headers=None):
        """Запуск функции и ожидание завершения теста"""
        self.start = True
        self.cancel = False
        self.finish = False
        self.count_test = 0
        self.responses = None
        self.proxy_lists = proxy_list
        self.errors = ""
        tasks = []
        if int(delay_all) > int(num_requests):
            delay = int(delay_all) / int(num_requests)
        else:
            delay = int(num_requests) / int(delay_all)

        async with ClientSession() as session:
            try:
                if proxy_list is None:
                    for prompts in prompts_json:
                        if self.flag_cancel_progress:
                            self.start = False
                            self.cancel = True
                            raise asyncio.CancelledError("Вы остановили процесс!")
                        await asyncio.sleep(delay)
                        task = asyncio.create_task(self.processing_post_requests(url, prompts, session, None, headers))
                        tasks.append(task)
                    self.responses = await asyncio.gather(*tasks)
                    if not self.flag_cancel_progress:
                        self.finish = True
                        self.start = False
                else:
                    for prompts, proxy in zip(prompts_json, proxy_list):
                        if self.flag_cancel_progress:
                            self.start = False
                            self.cancel = True
                            raise asyncio.CancelledError("Вы остановили процесс!")
                        await asyncio.sleep(delay)
                        task = asyncio.create_task(self.processing_post_requests(url, prompts, session, proxy, headers))
                        tasks.append(task)
                    self.responses = await asyncio.gather(*tasks)
                    if not self.flag_cancel_progress:
                        self.finish = True
                        self.start = False

            except asyncio.CancelledError:
                self.cancel = True

            except Exception:
                self.start = False
                if not self.cancel:
                    self.errors = "Ошибка подключения к серверу"

    def result(self):
        """Результат теста"""
        return self.responses

    def error(self):
        """Ошибки теста"""
        return self.errors
