from django import template

from wagtailtrans.models import Language

register = template.Library()


@register.simple_tag(takes_context=True)
def get_page_translations(context):
    page = context.get('page')
    if not page:
        return {}
    active_language = page.language.code
    site = page.get_site()
    homepages = (
        site
        .root_page
        .get_children()
        .specific()
        .prefetch_related('language')
        .filter(live=True))

    translations = page.get_translations().prefetch_related('language')
    data = {t.language.code: t.url for t in translations}

    languages = Language.objects.live().values_list('code', flat=True)
    data[active_language] = page.url
    for lang in languages:
        if not data.get(lang, False):
            data[lang] = homepages.filter(slug=lang).first().url

    result = []
    for code, url in data.items():
        result.append([
            code, url, True if active_language == code else False])
    return result

