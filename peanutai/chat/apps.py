from django.apps import AppConfig


from chat.thread_main import ThreadMain


class ChatConfig(AppConfig):
    name = 'chat'

    def ready(self):
        # https://code.djangoproject.com/ticket/8085#comment:13
        # if os.environ.get('RUN_MAIN', False):
        # start test case launcher on ready
        ThreadMain.get_instance().start()
