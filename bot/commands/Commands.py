# Filename: Commands.py
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
from discord import app_commands
from discord.ext import commands, tasks
from bot.language import BotLocalizer, BotTranslate
from bot.core import BotGlobals
from bot.commands import Buttons
from bot.commands import BotStaticEmbedManager

class Commands(commands.Cog):
    """
    The Commands class will house all commands provided by the
    TLOPO Discord Bot.

    This will hopefully make it easier for any developers to add
    further commands to this bot.
    """

    # TODO: Rewrite to be cleaner.
    # TODO: Add new strings to BotLocalizer files

    def __init__(self, bot):
        self.bot = bot
        self.taskMgr = bot.taskMgr
        self.settings = bot.settings
        self.staticEmbedMgr = BotStaticEmbedManager.StaticEmbedManager(bot)
        self.check_for_updates.start()

    @commands.hybrid_command(
            name='help',
            description= 'Returns a list of all commands'
    )
    async def help(self, ctx):
        """
        Returns a list of all commands.
        """

        embed = discord.Embed(title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[0], color=BotGlobals.EMBED_COLOR.get('help'))
        for command in self.bot.commands:
            name = command.name
            if command.help:
                if BotLocalizer.AUTOTRANSLATE_IN_USE == True:

                    debug = 'help_translate' in BotGlobals.DEBUG_MODULES
                    translator = BotTranslate.BotTranslate(debug, self.settings.getSetting('language'))

                    desc = translator.translate_string(command.help)

                    if debug:
                        print('[DEBUG] Translated help string: %s' % desc)

                    embed.set_footer(
                        text= BotLocalizer.AUTO_TRANSLATE_WARNING
                    )
                else:
                    desc = command.help
            else:
                desc = BotLocalizer.STATUS_MESSAGES[0]

            usage = "`%s%s`" % (ctx.prefix, name)

            # Add field for each command
            discord.Embed.add_field(
                embed,
                name= BotGlobals.FORMAT_STRINGS.get('bold') % usage,
                value=desc,
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.hybrid_command(
            name='about',
            description= 'Returns information about bot'
    )
    async def about(self, ctx):
        """
        Returns information about bot.
        """

        embed = discord.Embed(
            title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[1],
            description= BotLocalizer.APP_DESCRIPTION,
            color=BotGlobals.EMBED_COLOR.get('about'))
        
        try:
            with open(BotGlobals.AUTHORS_FILENAME, 'r') as f:
                authors = f.read()

                if authors == "":
                    authors = BotLocalizer.STATUS_MESSAGES[1]

        except FileNotFoundError:
            authors = BotLocalizer.STATUS_MESSAGES[1]
        
        discord.Embed.add_field(
            embed,
            name=BotLocalizer.FIELD_NAMES[0],
            value=authors,
            inline=False
        )

        if self.settings.getSetting('showLink') == True:
            discord.Embed.add_field(
                embed,
                name=BotLocalizer.STATUS_MESSAGES[12],
                value=self.settings.getSetting('link'),
                inline=False
            )
        else:
            discord.Embed.add_field(
                embed,
                name=BotLocalizer.STATUS_MESSAGES[12],
                value=BotLocalizer.STATUS_MESSAGES[0],
                inline=False
            )

        if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
            discord.Embed.set_footer(
                embed,
                text= BotLocalizer.AUTO_TRANSLATE_WARNING,
            )

        await ctx.send(embed=embed)

    @commands.hybrid_command(
            name='oceans',
            description= 'Returns server populations'
    )
    async def oceans(self, ctx):
        """
        Returns server populations.
        """

        system_status = self.taskMgr.getSystemStatus()

        if system_status.get('status', 0) == 3:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[11],
                description=BotLocalizer.STATUS_MESSAGES[8],
                color=BotGlobals.EMBED_COLOR.get('offline')
            )

        else:
            oceans = self.taskMgr.getOceanPopulations()
            total = 0

            embed = discord.Embed(title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[2], color=BotGlobals.EMBED_COLOR.get('oceans'))

            # Loop through each ocean and add it to the embed.
            for i, k in sorted(oceans.items()):
                discord.Embed.add_field(
                    embed,
                    name=i,
                    value=k,
                    inline=False
                )
                total += k

            # Add total population to the embed.
            discord.Embed.add_field(
                embed,
                name=BotLocalizer.FIELD_NAMES[1],
                value=BotGlobals.FORMAT_STRINGS.get('bold') % total,
                inline=False
            )

        if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
            discord.Embed.set_footer(
                embed,
                text= BotLocalizer.AUTO_TRANSLATE_WARNING,
            )
            
        # Response.
        await ctx.send(embed=embed)

    @commands.hybrid_command(
            name='fleets',
            description= 'Returns active fleets'
    )
    async def fleets(self, ctx):

        """
        Returns active fleets.
        """

        system_status = self.taskMgr.getSystemStatus()
        fleets = self.taskMgr.getActiveFleets()
        activeFleetCount = 0
        
        if system_status.get('status', 0) == 3:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[11],
                description=BotLocalizer.STATUS_MESSAGES[8],
                color=BotGlobals.EMBED_COLOR.get('offline')
            )

        elif fleets:
            embed = discord.Embed(title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[3], color=BotGlobals.EMBED_COLOR.get('fleets'))

            # Loop through each fleet and add it to the embed.
            for i, k in sorted(fleets.items()):
                if k.get('type') == '':
                    discord.Embed.add_field(
                        embed,
                        name=BotGlobals.FORMAT_STRINGS.get('bold') % i,
                        value=BotLocalizer.STATUS_MESSAGES[2],
                        inline=False
                    )
                    activeFleetCount += 1

                else:
                    discord.Embed.add_field(
                        embed,
                        name=BotGlobals.FORMAT_STRINGS.get('bold') % i,
                        value=BotLocalizer.FLEET_ITEM_INFO % (
                            k.get('type'),
                            k.get('state'),
                            k.get('shipsRemaining')
                        ),
                        inline=False
                    )

            if activeFleetCount != len(fleets.items()):
                embed = discord.Embed(title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[4], color=BotGlobals.EMBED_COLOR.get('fleets'))

        if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
            discord.Embed.set_footer(
                embed,
                text= BotLocalizer.AUTO_TRANSLATE_WARNING,
            )

        # Response.
        await ctx.send(embed=embed)

    @commands.hybrid_command(
            name='invasions',
            description= 'Returns active invasions'
    )
    async def invasions(self, ctx):

        """
        Returns active invasions.
        """

        invasions = self.taskMgr.getActiveInvasions()
        system_status = self.taskMgr.getSystemStatus()
        activeInvasionCount = 0

        if system_status.get('status', 0) == 3:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[11],
                description=BotLocalizer.STATUS_MESSAGES[8],
                color=BotGlobals.EMBED_COLOR.get('offline')
            )

        else:
            embed = discord.Embed(title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[5], color=BotGlobals.EMBED_COLOR.get('invasions'))
            
            # Loop through each invasion and add it to the embed.
            for i, k in sorted(invasions.items()):
                if k.get('state') == '':
                    discord.Embed.add_field(
                        embed,
                        name=BotGlobals.FORMAT_STRINGS.get('bold') % i,
                        value = BotLocalizer.STATUS_MESSAGES[3],
                        inline=False
                    )
                    activeInvasionCount += 1
                else:
                    discord.Embed.add_field(
                        embed,
                        name=BotGlobals.FORMAT_STRINGS.get('bold') % i,
                        value=BotLocalizer.INVASION_ITEM_INFO % (
                            k.get('state'),
                            k.get('phase'),
                            k.get('numPlayers')
                        ),
                        inline=False
                    )

            if activeInvasionCount == len(invasions.items()):
                embed = discord.Embed(title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[6], color=BotGlobals.EMBED_COLOR.get('invasions'))

        if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
            discord.Embed.set_footer(
                embed,
                text= BotLocalizer.AUTO_TRANSLATE_WARNING,
            )

        # Response.
        await ctx.send(embed=embed)

    @commands.hybrid_command(
            name='notices',
            description= 'Returns any server notices'
    )
    async def notices(self, ctx):
        """
        Returns any server notices.
        """

        system_status = self.taskMgr.getSystemStatus()
        
        if system_status:
            notices = system_status.get('notices')
            status = BotLocalizer.GLOB_CODE_TO_STATUS.get(int(system_status.get('status')), BotLocalizer.STATUS_MESSAGES[10])
            outages = system_status.get('outages')

            embed = discord.Embed(title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[7], color=BotGlobals.EMBED_COLOR.get('notices'))

            if notices:
                tmp = ""
                for i in notices.keys():
                    notice = notices[i]
                    msg = notice.get('text')
                    flag = BotLocalizer.SRV_CODE_TO_STATUS.get(int(notice.get('flag')))
                    tmp += BotGlobals.FORMAT_STRINGS.get('notice_format') % (flag, BotLocalizer.MISC[0], i, msg)

            elif system_status.get('status', 0) == 3:
                embed = discord.Embed(
                    title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[12],
                    description=BotLocalizer.STATUS_MESSAGES[8],
                    color=BotGlobals.EMBED_COLOR.get('offline')
                )
                return
            
            else:
                tmp = BotLocalizer.STATUS_MESSAGES[4]

            discord.Embed.add_field(
                embed,
                name=BotLocalizer.OVER_ALL_STATUS % status,
                value=BotLocalizer.SYSTEM_STATUS_INFO % (tmp, outages),
                inline=False
            )
            
            # Autotranslate warning.
            # User warning that api isnt reading prod-gs-1.tlopo.com correctly. Remove when fixed.
            if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
                discord.Embed.set_footer(
                    embed,
                    text= "%s\n%s" % (BotLocalizer.STATUS_MESSAGES[9], BotLocalizer.AUTO_TRANSLATE_WARNING)
                )
            else:
                discord.Embed.set_footer(
                    embed,
                    text= BotLocalizer.STATUS_MESSAGES[9]
                )

        else:
            embed = discord.Embed(title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[10], color=BotGlobals.EMBED_COLOR.get('error'))

            if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
                discord.Embed.set_footer(
                    embed,
                    text= BotLocalizer.AUTO_TRANSLATE_WARNING,
                )

        await ctx.send(embed=embed)

    @commands.hybrid_command(
            name='status',
            description= 'Returns current server status',
    )
    async def status(self, ctx):
        """
        Returns current server status.
        """

        await self.status_embed(ctx)
    
    @commands.hybrid_command(
            name='status-detailed',
            description= 'Returns current server status with more details'
    )
    async def fullstatus(self, ctx):
        """
        Returns current server status with more details.
        """

        await self.fullstatus_embed(ctx)

    @commands.hybrid_command(
            name='news',
            description= 'Returns latest news articles'
    )
    async def news(self, ctx):
        """
        Returns latest news articles.
        """

        await self.news_embed(ctx)
    
    @commands.hybrid_command(
            name='releases',
            description= 'Returns latest releases'
    )
    async def releases(self, ctx):
        """
        Returns latest releases.
        """

        await self.releases_embed(ctx)

    @commands.hybrid_command(
            name='notification',
            description= 'Returns the current news banner on the TLOPO website'
    )
    async def notification(self, ctx):
        """
        Returns the current news banner on the TLOPO website.
        """

        system_status = self.taskMgr.getSystemStatus()
        notification = self.taskMgr.getNewsNotifications()

        if system_status.get('status', 0) == 3:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[11],
                description=BotLocalizer.STATUS_MESSAGES[8],
                color=BotGlobals.EMBED_COLOR.get('offline')
            )
        elif notification:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % notification.get('title'),
                description=notification.get('datetime'),
                url=BotGlobals.TLOPO_URL,
                color=BotGlobals.EMBED_COLOR.get('notices')
            )
        else:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[12],
                url=BotGlobals.TLOPO_URL,
                color=BotGlobals.EMBED_COLOR.get('status')
            )

        await ctx.send(embed=embed)
    
    
    @commands.hybrid_command(
        name='static',
        description= 'Create a static embed.'
    )
    @app_commands.choices(module=[
        app_commands.Choice(name='status', value='status'),
        app_commands.Choice(name='status-detailed', value='status-detailed'),
        app_commands.Choice(name='news', value='news'),
        app_commands.Choice(name='releases', value='releases'),
        app_commands.Choice(name='help', value='help')
    ])
    async def static(self, ctx, module: str):
        """
        Create a static embed of one of the following modules:
        - status
        - status-detailed
        - news
        - releases
        """

        if module is None or module.lower() == 'help':
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % "Static Embed Modules",
                description="Here are the available modules for the static command:",
                color=BotGlobals.EMBED_COLOR.get('help')
            )
            
            embed.add_field(
                name="status",
                value="Shows the current server status with emoji indicators",
                inline=False
            )
            embed.add_field(
                name="status-detailed",
                value="Shows detailed server status information",
                inline=False
            )
            embed.add_field(
                name="news",
                value="Shows the latest news articles",
                inline=False
            )
            embed.add_field(
                name="releases",
                value="Shows the latest release notes",
                inline=False
            )
            
            embed.set_footer(text="Usage: %sstatic <module>" % ctx.prefix)
            return await ctx.send(embed=embed)
    
        module = module.lower()

        returnMsg = "Static embed created for %s in channel %s" % (module, ctx.channel.mention)

        if module == 'status':
            message = await self.status_embed(ctx)
            await self.staticEmbedMgr.add_reference('status', message)
            await ctx.send(returnMsg, ephemeral=True, delete_after=5)
        elif module == 'status-detailed':
            message = await self.fullstatus_embed(ctx)
            await self.staticEmbedMgr.add_reference('status-detailed', message)
            await ctx.send(returnMsg, ephemeral=True, delete_after=5)
        elif module == 'news':
            message = await self.news_embed(ctx)
            await self.staticEmbedMgr.add_reference('news', message)
            await ctx.send(returnMsg, ephemeral=True, delete_after=5)
        elif module == 'releases':
            message = await self.releases_embed(ctx)
            await self.staticEmbedMgr.add_reference('releases', message)
            await ctx.send(returnMsg, ephemeral=True, delete_after=5)
        else:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % 'Invalid Module',
                description='%s is not a valid module. Use `%sstatic help` to see available modules.' % (module, ctx.prefix),
                color=BotGlobals.EMBED_COLOR.get('error')
            )
            await ctx.send(embed=embed)
    
    # TBH this should be in BotTasks.py but for importing and innitialization it's easier to keep it here.
    @tasks.loop(minutes=5)
    async def check_for_updates(self):
        """
        Periodically check if data has changed and update static embeds
        """

        try:
            if self.taskMgr.hasStatusChanged():
                status_embed = await self._create_status_embed()
                updated, failed = await self.staticEmbedMgr.update_all_embeds('status', status_embed)
                print('Updated %s status embeds, %s failed' % (updated, failed))
                
                fullstatus_embed = await self._create_fullstatus_embed()
                updated, failed = await self.staticEmbedMgr.update_all_embeds('status-detailed', fullstatus_embed)
                print('Updated %s detailed status embeds, %s failed' % (updated, failed))
            
            if self.taskMgr.hasNewsChanged():
                news_embed = await self._create_news_embed()
                updated, failed = await self.staticEmbedMgr.update_all_embeds('news', news_embed)
                print('Updated %s news embeds, %s failed' % (updated, failed))
            
            if self.taskMgr.hasReleasesChanged():
                releases_embed = await self._create_releases_embed() 
                updated, failed = await self.staticEmbedMgr.update_all_embeds('releases', releases_embed)
                print('Updated %s release embeds, %s failed' % (updated, failed))
    
        except Exception as e:
            print('Error in update task: %s' % e)

    # On rare occasions the bot innitilizes the commands before the bot is even ready and bugs out, no clue why but this fixes it.
    @check_for_updates.before_loop
    async def before_check_updates(self):
        """
        Wait until the bot is ready before starting the update task
        """

        await self.bot.wait_until_ready()

    async def status_embed(self, ctx):
        """
        Creates the status embed.
        """

        system_status = self.taskMgr.getSystemStatus()
        servers = system_status.get('servers')
        webs = servers.get('web', [])
        cas = servers.get('client_agents', [])
        ais = servers.get('oceans', [])
        uds = servers.get('gameserver_functions', [])

        embed = discord.Embed(
            title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[8],
            color=BotGlobals.EMBED_COLOR.get('status')
        )

        if not system_status.get('status', 0) == 3:
            # Loop through each server and add it to the embed.

            # Add web server status to the embed.
            tmp = ""
            for server in webs:
                flag = BotGlobals.GLOB_CODE_TO_EMOJI.get(server.get('status', 0))
                tmp += BotGlobals.FORMAT_STRINGS.get('server_status') % (server.get('name', BotLocalizer.STATUS_MESSAGES[10]), flag)
            discord.Embed.add_field(
                embed,
                name=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.FIELD_NAMES[2],
                value=tmp,
                inline=False
            )

            # Add client agent status to the embed.
            tmp = ""
            for server in cas:
                flag = BotGlobals.GLOB_CODE_TO_EMOJI.get(server.get('status', 0))
                tmp += BotGlobals.FORMAT_STRINGS.get('server_status') % (server.get('name', BotLocalizer.STATUS_MESSAGES[10]), flag)
            discord.Embed.add_field(
                embed,
                name=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.FIELD_NAMES[3],
                value=tmp,
                inline=False
            )

            # Add ocean status to the embed.
            tmp = ""
            for server in ais:
                flag = BotGlobals.GLOB_CODE_TO_EMOJI.get(server.get('status', 0))
                tmp += BotGlobals.FORMAT_STRINGS.get('server_status') % (server.get('name', BotLocalizer.STATUS_MESSAGES[10]), flag)
            discord.Embed.add_field(
                embed,
                name=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.FIELD_NAMES[4],
                value=tmp,
                inline=False
            )

            # Add gameserver functions status to the embed.
            tmp = ""
            for server in uds:
                flag = BotGlobals.GLOB_CODE_TO_EMOJI.get(server.get('status', 0))
                tmp += BotGlobals.FORMAT_STRINGS.get('server_status') % (server.get('name', BotLocalizer.STATUS_MESSAGES[10]), flag)
            discord.Embed.add_field(
                embed,
                name=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.FIELD_NAMES[5],
                value=tmp,
                inline=False
            )

            # Autotranslate warning.
            # User warning that api isnt reading prod-gs-1.tlopo.com correctly. Remove when fixed.
            if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
                discord.Embed.set_footer(
                    embed,
                    text= "%s\n%s" % (BotLocalizer.STATUS_MESSAGES[9], BotLocalizer.AUTO_TRANSLATE_WARNING)
                )
            else:
                discord.Embed.set_footer(
                    embed,
                    text= BotLocalizer.STATUS_MESSAGES[9]
                )
        
        elif system_status.get('status', 0) == 3:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[11],
                description=BotLocalizer.STATUS_MESSAGES[8],
                color=BotGlobals.EMBED_COLOR.get('offline')
            )

            if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
                discord.Embed.set_footer(
                    embed,
                    text= BotLocalizer.AUTO_TRANSLATE_WARNING,
                )

        else:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[9],
                color=BotGlobals.EMBED_COLOR.get('error')
            )

            if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
                discord.Embed.set_footer(
                    embed,
                    text= BotLocalizer.AUTO_TRANSLATE_WARNING,
                )

        return await ctx.send(embed=embed)

    async def fullstatus_embed(self, ctx):
        """
        Creates the full status embed.
        """

        system_status = self.taskMgr.getSystemStatus()

        servers = system_status.get('servers')
        webs = servers.get('web', [])
        cas = servers.get('client_agents', [])
        ais = servers.get('oceans', [])
        uds = servers.get('gameserver_functions', [])

        embed = discord.Embed(
            title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[8],
            color=BotGlobals.EMBED_COLOR.get('fullstatus')
        )

        if not system_status.get('status', 0) == 3:
            # Loop through each server and add it to the embed.

            # Add web server status to the embed.
            tmp = ""
            for server in webs:
                flag = BotLocalizer.GLOB_CODE_TO_STATUS.get(server.get('status', 0))
                tmp += BotGlobals.FORMAT_STRINGS.get('server_status') % (server.get('name', BotLocalizer.STATUS_MESSAGES[10]), flag)
            discord.Embed.add_field(
                embed,
                name=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.FIELD_NAMES[2],
                value=tmp,
                inline=False
            )

            # Add client agent status to the embed.
            tmp = ""
            for server in cas:
                flag = BotLocalizer.GLOB_CODE_TO_STATUS.get(server.get('status', 0))
                tmp += BotGlobals.FORMAT_STRINGS.get('server_status') % (server.get('name', BotLocalizer.STATUS_MESSAGES[10]), flag)
            discord.Embed.add_field(
                embed,
                name=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.FIELD_NAMES[3],
                value=tmp,
                inline=False
            )

            # Add ocean status to the embed.
            tmp = ""
            for server in ais:
                flag = BotLocalizer.GLOB_CODE_TO_STATUS.get(server.get('status', 0))
                tmp += BotGlobals.FORMAT_STRINGS.get('server_status') % (server.get('name', BotLocalizer.STATUS_MESSAGES[10]), flag)
            discord.Embed.add_field(
                embed,
                name=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.FIELD_NAMES[4],
                value=tmp,
                inline=False
            )

            # Add gameserver functions status to the embed.
            tmp = ""
            for server in uds:
                flag = BotLocalizer.GLOB_CODE_TO_STATUS.get(server.get('status', 0))
                tmp += BotGlobals.FORMAT_STRINGS.get('server_status') % (server.get('name', BotLocalizer.STATUS_MESSAGES[10]), flag)
            discord.Embed.add_field(
                embed,
                name=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.FIELD_NAMES[5],
                value=tmp,
                inline=False
            )

            # Autotranslate warning.
            # User warning that api isnt reading prod-gs-1.tlopo.com correctly. Remove when fixed.
            if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
                discord.Embed.set_footer(
                    embed,
                    text= "%s\n%s" % (BotLocalizer.STATUS_MESSAGES[9], BotLocalizer.AUTO_TRANSLATE_WARNING)
                )
            else:
                discord.Embed.set_footer(
                    embed,
                    text= BotLocalizer.STATUS_MESSAGES[9]
                )
        
        elif system_status.get('status', 0) == 3:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[11],
                description=BotLocalizer.STATUS_MESSAGES[8],
                color=BotGlobals.EMBED_COLOR.get('offline')
            )

            if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
                discord.Embed.set_footer(
                    embed,
                    text= BotLocalizer.AUTO_TRANSLATE_WARNING,
                )

        else:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[9],
                color=BotGlobals.EMBED_COLOR.get('error')
            )

            if BotLocalizer.AUTOTRANSLATE_IN_USE == True:
                discord.Embed.set_footer(
                    embed,
                    text= BotLocalizer.AUTO_TRANSLATE_WARNING,
                )

        return await ctx.send(embed=embed)

    async def news_embed(self, ctx):
        """
        Creates the news embed.
        """

        news = self.taskMgr.getNewsFeed()
        system_status = self.taskMgr.getSystemStatus()
        
        if system_status.get('status', 0) == 3:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[11],
                description=BotLocalizer.STATUS_MESSAGES[8],
                color=BotGlobals.EMBED_COLOR.get('offline')
            )
            return await ctx.send(embed=embed)
        
        else:
            view = Buttons.NewsButtons(news)
            embed = view.create_news_embed()

            return await ctx.send(embed=embed, view=view)
    
    async def releases_embed(self, ctx):
        """
        Creates the releases embed.
        """

        releases = self.taskMgr.getReleaseFeed()
        system_status = self.taskMgr.getSystemStatus()
        
        if system_status.get('status', 0) == 3:
            embed = discord.Embed(
                title=BotGlobals.FORMAT_STRINGS.get('bold') % BotLocalizer.EMBED_TITLES[11],
                description=BotLocalizer.STATUS_MESSAGES[8],
                color=BotGlobals.EMBED_COLOR.get('offline')
            )
            return await ctx.send(embed=embed)
        
        else:
            view = Buttons.ReleaseButtons(releases)

            embed = view.create_release_embed()

            return await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Commands(bot))