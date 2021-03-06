from django.conf import settings
from django.conf.urls import include, url
from django.core.urlresolvers import reverse
from wagtail.wagtailadmin import widgets
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailcore import hooks

from wagtailtrans.models import Language
from wagtailtrans.urls import languages, translations


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^language/',
            include(languages, namespace='wagtailtrans_languages')),
        url(r'^translate/',
            include(translations, namespace='wagtailtrans_translations')),
    ]


@hooks.register('register_settings_menu_item')
def register_language_menu_item():
    return MenuItem(
        'Languages',
        reverse('wagtailtrans_languages:index'),
        classnames='icon icon-snippet',
        order=1000,
    )


if not settings.WAGTAILTRANS_SYNC_TREE:
    """Only load hooks when WAGTAILTRANS_SYNC_TREE is disabled"""

    @hooks.register('register_page_listing_buttons')
    def page_translations_menu(page, page_perms, is_parent=False):
        if not hasattr(page, 'language'):
            return

        if hasattr(page, 'canonical_page') and page.canonical_page:
            return

        yield widgets.ButtonWithDropdownFromHook(
            'Translate into',
            hook_name='wagtailtrans_dropdown_hook',
            page=page,
            page_perms=page_perms,
            is_parent=is_parent,
            priority=10)

    @hooks.register('wagtailtrans_dropdown_hook')
    def page_translations_menu_items(page, page_perms, is_parent=False):
        prio = 1
        exclude_lang = None

        if hasattr(page, 'language') and page.language:
            exclude_lang = page.language

        other_languages = set(
            Language.objects
            .live()
            .exclude(pk=exclude_lang.pk)
            .order_by('position'))

        translations = (
            page.get_translations(only_live=False).select_related('language'))
        taken_languages = set(translations.values_list('language', flat=True))

        translation_targets = other_languages - taken_languages
        for language in translation_targets:
            yield widgets.Button(
                language.get_code_display(),
                reverse('wagtailtrans_translations:add', kwargs={
                    'page_pk': page.pk,
                    'language_code': language.code,
                }),
                priority=prio)

            prio += 1
