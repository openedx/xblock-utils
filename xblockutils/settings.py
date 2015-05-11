# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 OpenCraft
# License: AGPLv3
"""
This module contains a mixins that allows third party XBlocks to access Settings Service in edX LMS.
"""
from xblockutils.resources import ResourceLoader


class XBlockWithSettingsMixin(object):
    """
    This XBlock Mixin provides access to XBlock settings service
    Descendant Xblock must add @XBlock.wants('settings') declaration

    Configuration:
        block_settings_key: string - XBlock settings is essentially a dictionary-like object (key-value storage).
                                     Each XBlock must provide a key to look its settings up in this storage.
                                     Settings Service uses `block_settings_key` attribute to get the XBlock settings key
    """
    block_settings_key = None

    def get_xblock_settings(self, default=None):
        """
        Gets XBlock-specific settigns for current XBlock

        Returns default if settings service is not available.

        Parameters:
            default - default value to be used in two cases:
                      * No settings service is available
                      * As a `default` parameter to `SettingsService.get_settings_bucket`
        """
        settings_service = self.runtime.service(self, "settings")
        if settings_service:
            return settings_service.get_settings_bucket(self, default=default)
        else:
            return default


class ThemableXBlockMixin(object):
    """
    This XBlock Mixin provides configurable theme support via Settings Service.
    This mixin implies XBlockWithSettingsMixin is already mixed in into Descendant XBlock

    Parameters:
        default_theme_config: dict - default theme configuration in case no theme configuration is obtained from
                                     Settings Service
        theme_key: string -          XBlock settings key to look theme up
        block_settings_key: string - (implicit)

    Examples:

        Looks up red.css and small.css in `my_xblock` package:
        default_theme_config = {
            'package': 'my_xblock',
            'locations': ['red.css', 'small.css']
        }

        Looks up public/themes/red.css in my_other_xblock.assets
        default_theme_config = {
            'package': 'my_other_xblock.assets',
            'locations': ['public/themes/red.css']
        }
    """
    default_theme_config = None
    theme_key = "theme"

    def get_theme(self):
        """
        Gets theme settings from settings service. Falls back to default (LMS) theme
        if settings service is not available, xblock theme settings are not set or does
        contain mentoring theme settings.
        """
        xblock_settings = self.get_xblock_settings(default={})
        if xblock_settings and self.theme_key in xblock_settings:
            return xblock_settings[self.theme_key]
        return self.default_theme_config

    def include_theme_files(self, fragment):
        """
        Gets theme configuration and renders theme css into fragment
        """
        theme = self.get_theme()
        theme_package, theme_files = theme['package'], theme['locations']
        for theme_file in theme_files:
            fragment.add_css(ResourceLoader(theme_package).load_unicode(theme_file))
