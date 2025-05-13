# Filename: BotCore.py
# Author: mfwass
# Date: January 8th, 2017
#
# The Legend of Pirates Online Software
# Copyright (c) The Legend of Pirates Online. All rights reserved.
#
# All use of this software is subject to the terms of the revised BSD
# license.  You should have received a copy of this license along
# with this source code in a file named "LICENSE."

import discord
from discord.ext import commands

from bot.core import BotGlobals, BotSettings
from bot.language import BotLocalizer
from bot.tasks import BotTasks

from bot.commands import Commands

import json
import os

class BotCore():
    """
    The BotCore class will serve as the central location
    for all of the Discord Bot's central functions.

    This class will load the settings for the application
    and house the Bot.

    Ideally, all global calls will reference this class for
    further direction.
    """

    def __init__(self):
        # Initialize the BotSettings class.
        self.settings = BotSettings.BotSettings()

        # Load settings from the settings file.
        self.settings.loadSettings(BotGlobals.SETTINGS_FILENAME)

        # Check if we have a local settings file.
        if os.path.exists(BotGlobals.LOCAL_SETTINGS_FILENAME):
            # Load local settings. If we find a duplicate,
            # the local settings will override the regular.
            self.settings.loadSettings(BotGlobals.LOCAL_SETTINGS_FILENAME, override=True)

        # Get language with default fallback
        language = self.settings.getSetting('language')
        if not language:
            language = 'en-us'

        # Initialize the BotLocalizer class.
        localizer = BotLocalizer.BotLocalizer(self.settings.getSetting('debug'), self.settings.getSetting('autoTranslate'), language)

        # Import language module
        localizer.importLanguageModule()

        # Create the bot using Discord's API.
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        self.bot = commands.Bot(description=BotLocalizer.APP_DESCRIPTION, command_prefix=self.settings.getSetting('commandPrefix'), intents=intents)
        self.bot.remove_command('help')
        
        # Initialize taskMgr.
        self.taskMgr = BotTasks.BotTasks(self.settings.getSetting('maxNewsAricles'), self.settings.getSetting('debug'), self.settings.getSetting('language'), self.settings.getSetting('maxReleaseNotes'))
        self.taskMgr.initializeTasks(BotGlobals.BOT_TASKS)

        self.bot.taskMgr = self.taskMgr
        self.bot.settings = self.settings

        @self.bot.event
        async def on_ready():
            """
            When the bot is connected to the server and is ready to
            process commands, this function will be ran.

            This will give some useful information to Discord
            channel admin who's running this bot.
            """

            print(':BotCore: Connected.')
            print(":BotCore: Logged in as user '%s' with ID '%s'" % (self.bot.user.name, self.bot.user.id))

            try:
                await self.bot.load_extension('bot.commands.Commands')
                print(':BotCore: Loaded commands.')
                await self.bot.tree.sync()
                print(':BotCore: Synced commands.')
            except Exception as e:
                print(f":BotCore: Error loading commands: {e}")

            # This bot is not in any servers yet, let's print the URL that they would use
            # to add the bot to a server.  Just in case they don't know it.
            if len(self.bot.guilds) == 0:
                print(":BotCore: To connect this bot to a server, please use the following url:\n")
                print('    https://discordapp.com/oauth2/authorize?client_id=%s&permissions=580553413979200&integration_type=0&scope=applications.commands+bot' % self.bot.user.id)

            print(':BotCore: %s' % BotLocalizer.APP_DESCRIPTION)
