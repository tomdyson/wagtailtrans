from collections import namedtuple

from django import VERSION as django_version
from django.conf import settings
from django.template import Library

from wagtailtrans.models import TranslatablePage

register = Library()

assignment_tag = register.simple_tag
if django_version < (1, 9):
    assignment_tag = register.assignment_tag


@assignment_tag
def get_canonical_pages_for_delete(page):
    """Get the translations made for this page

    :param page: Page instance
    :return: queryset or False

    """
    page = page.specific
    if (
        settings.WAGTAILTRANS_SYNC_TREE and
        getattr(page, 'language', False) and
        not page.canonical_page
    ):
        return TranslatablePage.objects.filter(canonical_page=page)
    return False


@assignment_tag(takes_context=True)
def get_available_language_urls(context):
    """
    """
    request = context.get('request')
    if not request:
        return {}

    page = context.get('page')
    site = request.site
    if not page or not site:
        return {}

    homepages = site.root_page.get_children().specific().live()
    translations = page.get_translations_and_self(only_live=True).specific()

    return {}








# @register.simple_tag(takes_context=True)
# def get_page_translations(context):
#     page = context.get('page')
#     if not page:
#         return {}
#     active_language = page.language.code
#     site = page.get_site()
#     homepages = (
#         site
#         .root_page
#         .get_children()
#         .specific()
#         .prefetch_related('language')
#         .filter(live=True))

#     translations = page.get_translations().prefetch_related('language')
#     data = {t.language.code: t.url for t in translations}

#     languages = Language.objects.live().values_list('code', flat=True)
#     data[active_language] = page.url
#     for lang in languages:
#         if not data.get(lang, False):
#             data[lang] = homepages.filter(slug=lang).first().url

#     result = []
#     for code, url in data.items():
#         result.append([
#             code, url, True if active_language == code else False])
#     return result
