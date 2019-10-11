import os
import logging
import importlib
from ollo import base
from aiohttp import web
from ollo import OLLOConnect
from ollo.app import Settings
from ollo.urls import Controller


LOG_FORMAT = """[%(asctime)s] \
[FILE: %(pathname)s] %(module)s->%(funcName)s(): [LINE:%(lineno)d]
# %(levelname)-8s %(message)s\n"""


class Application(metaclass=base.__BaseSingleton):
    def __init__(self, settings, app_name):
        kwargs = {}
        for attr in dir(settings):
            if attr.isupper():
                kwargs[attr] = getattr(settings, attr)
        logging_config = {
            "format": LOG_FORMAT,
            "level": logging.DEBUG if kwargs.get("DEBUG") else logging.INFO,
        }
        if kwargs.get("LOG_FILE"):
            logging_config["filename"] = kwargs["LOG_FILE"]
        logging.basicConfig(**logging_config)
        self.settings = Settings(
            **kwargs, LOG=logging.getLogger(app_name)
        )
        self.run()

    def run(self):

        async def on_shutdown(app):
            for ws in app["websockets"]:
                await ws.close(code=1001, message="Server shutdown")

        app = web.Application(
            logger=self.settings.log, middlewares=self.settings.middlewares
        )
        controller = Controller()
        controller.entry_point = self.settings.root_urlconf
        for route in controller.urlpatterns:
            app.router.add_route("*", route.path, route.handler, name=route.name)
        if self.settings.get("STATIC_ROOT") and self.settings.debug:
            app["static_root_url"] = (
                self.settings.get("STATIC_URL")
                if self.settings.get("STATIC_URL")
                else "/static"
            )
            app.router.add_static(
                app["static_root_url"],
                self.settings.get("STATIC_ROOT"),
                name="static",
            )
        try:
            import aiohttp_jinja2
            from jinja2 import FileSystemLoader
        except ImportError:
            self.settings.log.info("Modules 'jinja2, aiohttp_jinja2' not found.")
        else:
            aiohttp_jinja2.setup(
                app,
                loader=FileSystemLoader(
                    [
                        os.path.join(path, "templates")
                        for path in os.listdir(self.settings.base_dir)
                        if os.path.isdir(path) and
                        os.path.isdir(os.path.join(path, "templates"))
                    ]
                ),
            )
        app["websockets"] = []
        app.on_cleanup.append(on_shutdown)
        OLLOConnect.connect(self.settings.databases)
        self.settings.log.info(
            f"Server running on http://{self.settings.host}:{self.settings.port}"
        )
        web.run_app(
            app, host=self.settings.host, port=self.settings.port, print=False
        )
        self.settings.log.info("Server stop.")


def get_application(settings_module, app_name):
    return Application(importlib.import_module(settings_module), app_name)
