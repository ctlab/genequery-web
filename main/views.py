from utils.mixins import BaseTemplateView


class AboutPageView(BaseTemplateView):
    template_name = 'about.html'
    menu_active = 'about'

about_page_view = AboutPageView.as_view()


class ContactsPageView(BaseTemplateView):
    template_name = 'contacts.html'
    menu_active = 'contacts'

contacts_page_view = ContactsPageView.as_view()