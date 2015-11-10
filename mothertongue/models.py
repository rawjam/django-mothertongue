# import stuff we need from django
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import get_language, ugettext, ugettext_lazy as _
from django.utils import translation

from threadlocals.threadlocals import get_current_request

# import package specific stuff
from django.conf import settings

# class to handle translated models
class MothertongueModelTranslate(models.Model):
    """
    Models that extend this class will have the ability to define:
    - translation_set, e.g: 'contenttranslation_set', the many to many
      manager name for the translation models for this model.
    - translated_fields = e.g: ['content',] - the fields that may be
      translated. A match is found if a translation exists with a 'language'
      the same as the current language, e.g: 'es' and a matching name.
    """
    _translation_cache = None
    _allow_translate = True

    class Meta(object):
        abstract = True

    def __init__(self, *args, **kwargs):
        super(MothertongueModelTranslate, self).__init__(*args, **kwargs)
        self._translation_cache = {}

        # Added by Raw Jam 06/11/2015 to prevent issues when editing these models in
        # the admin, with the non default language in use.
        request = get_current_request()
        if request.user.is_staff and "PATH_INFO" in request.META and "/admin/" in request.META['PATH_INFO']:
            self._allow_translate = False

    def __getattribute__(self, name):
        """
        Specialise to look for translated content, note we use super's
        __getattribute__ within this function to avoid a recursion error.
        """
        if name == "_allow_translate":
            return super(MothertongueModelTranslate, self).__getattribute__(name)
        else:
            if self._allow_translate:
                get = lambda p:super(MothertongueModelTranslate, self).__getattribute__(p)
                translated_fields = get('translated_fields')
                if name in translated_fields:
                    try:
                        translation_set = get('translation_set')
                        code = translation.get_language()
                        translated_manager = get(translation_set)
                        try:
                            translated_object = None
                            translated_object = self._translation_cache[code]
                        except KeyError:
                            translated_object = translated_manager.get(language=code)
                        finally:
                            self._translation_cache[code] = translated_object
                        if translated_object:
                            return getattr(translated_object, name)
                    except (ObjectDoesNotExist, AttributeError):
                        pass
                return get(name)
            else:
                return super(MothertongueModelTranslate, self).__getattribute__(name)
