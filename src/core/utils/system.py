from uvicorn.main import Server


original_handler = Server.handle_exit

class AppStatus:
    should_exit = False
    
    @staticmethod
    def handle_exit(*args, **kwargs):
        AppStatus.should_exit = True
        original_handler(*args, **kwargs)

Server.handle_exit = AppStatus.handle_exit
