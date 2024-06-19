from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['home', 'signin', 'find_user_report_data', 'find_user_all_report_data']

    def location(self, item):
        return reverse(item)
