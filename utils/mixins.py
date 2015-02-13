from django.views.generic import TemplateView


class BaseTemplateView(TemplateView):
    menu_active = None

    def get_context_data(self, **kwargs):
        context = super(BaseTemplateView, self).get_context_data()
        context['menu_active'] = self.menu_active
        return context