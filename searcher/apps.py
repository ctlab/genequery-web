from django.apps import AppConfig


class SearcherAppConfig(AppConfig):
    name = "searcher"

    def ready(self):
        # Initialize data on server startup
        # import dataholder
        pass
