from django.utils.translation import ugettext as _
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from pages.plugins.jsonexport.utils import (pages_to_json,
    monkeypatch_remove_pages_site_restrictions)
from pages.models import Page

import sys

class Command(BaseCommand):
    args = '<user>'

    def handle(self, user, **options):
        """
        Import pages in JSON format.  When creating a page and the original
        author does not exist, use user as the new author.  User may be
        specified by username, id or email address.
        """
        monkeypatch_remove_pages_site_restrictions()
        for match in ('username', 'pk', 'email'):
            try:
                u = User.objects.get(**{match:user})
                break
            except (User.DoesNotExist, ValueError):
                continue
        else:
            raise CommandError(_("User with username/id/email = '%s' not found")
                % user)

        json = sys.stdin.read()
        errors, pages_created = json_to_pages(json, u)
        if errors:
            for e in errors:
                sys.stderr.write(e + '\n')
            raise CommandError(_("Errors encountered while importing JSON"))
        for page, created, messages in pages_created:
            print (_("%s created.") if created else _("%s modified.")) % (
                page.get_complete_slug())
            for m in messages:
                print " - " + m

