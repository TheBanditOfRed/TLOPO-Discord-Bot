import json
import os
import discord
from bot.core import BotGlobals


class StaticEmbedManager:
    """
    The class StaticEmbedManager is responsible for managing all static embeds
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.debug = bot.settings.getSetting('debug')
        self.storage_file = "bot/commands/BotStaticEmbeds.json"
        self.references = {}
        self.load_references()
        
    def load_references(self):
        """
        Load saved message references from storage
        """

        if self.debug and 'load_references' in BotGlobals.DEBUG_MODULES:
            print('[DEBUG][load_references] Loading static embed references')
        
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    self.references = json.load(f)
            else:
                self.references = {
                    "status": [],
                    "fullstatus": [],
                    "news": [],
                    "releases": []
                }
        except Exception as e:
            print('Error loading static embed references: %s' % e)
            self.references = {
                "status": [],
                "fullstatus": [],
                "news": [],
                "releases": []
            }
        
        if self.debug and 'load_references' in BotGlobals.DEBUG_MODULES:
            print('[DEBUG][load_references] Static embed references loaded')
            print(json.dumps(self.references, indent=4))
    
    def save_references(self):
        """
        Save message references to storage
        """

        if self.debug and 'save_references' in BotGlobals.DEBUG_MODULES:
            print('[DEBUG][save_references] Saving static embed references')

        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.references, f, indent=4)
        except Exception as e:
            print('Error saving static embed references: %s' % e)
            print(json.dumps(self.references, indent=4))
        
        if self.debug and 'save_references' in BotGlobals.DEBUG_MODULES:
            print('[DEBUG][save_references] Static embed references saved')
            print(json.dumps(self.references, indent=4))
    
    async def add_reference(self, module: str, message: discord.Message) -> bool:
        """
        Add a new message reference for a module
        
        Args:
            module (str): The module name
            message (discord.Message): The message object to reference

        Returns:
            bool: True if the reference was added, False if it already exists
        """

        ref = {
            "channel_id": message.channel.id,
            "message_id": message.id
        }
        
        if module in self.references:
            if ref not in self.references[module]:
                self.references[module].append(ref)
                self.save_references()

                if self.debug and 'add_reference' in BotGlobals.DEBUG_MODULES:
                    print('[DEBUG][add_reference] Added reference for module %s' % module)
                    print(json.dumps(ref, indent=4))

                return True
        
        if self.debug and 'add_reference' in BotGlobals.DEBUG_MODULES:
            print('[DEBUG][add_reference] Reference already exists for module %s' % module)

        return False
    
    async def remove_reference(self, module: str, message: discord.Message) -> bool:
        """
        Remove a message reference

        Args:
            module (str): The module name
            message (discord.Message): The message object to remove
        
        Returns:
            bool: True if the reference was removed, False if it didn't exist
        """

        if module in self.references:
            ref = {
                "channel_id": message.channel.id,
                "message_id": message.id
            }

            if ref in self.references[module]:
                self.references[module].remove(ref)
                self.save_references()

                if self.debug and 'remove_reference' in BotGlobals.DEBUG_MODULES:
                    print('[DEBUG][remove_reference] Removed reference for module %s' % module)
                    print(json.dumps(ref, indent=4))
                return True
            
        if self.debug and 'remove_reference' in BotGlobals.DEBUG_MODULES:
            print('[DEBUG][remove_reference] Reference not found for module %s' % module)
        return False
    
    async def update_all_embeds(self, module: str, new_embed: discord.Embed) -> tuple:
        """
        Update all stored embeds for a specific module
        
        Args:
            module (str): The module name
            new_embed (discord.Embed): The new embed to replace the old one

        Returns:
            tuple: (updated, failed) - Number of updated and failed updates
        """

        updated = 0
        failed = 0
        
        if module not in self.references:
            return updated, failed
        
        references = self.references[module].copy()

        if self.debug and 'update_all_embeds' in BotGlobals.DEBUG_MODULES:
            print('[DEBUG][update_all_embeds] Updating all embeds for module %s' % module)
            print(json.dumps(references, indent=4))
        
        for ref in references:
            try:
                channel = self.bot.get_channel(ref["channel_id"])
                if not channel:
                    try:
                        channel = await self.bot.fetch_channel(ref["channel_id"])
                    except:
                        channel = None
                    
                    if self.debug and 'update_all_embeds_channel' in BotGlobals.DEBUG_MODULES:
                            print('[DEBUG][update_all_embeds][channel] Channel not cached, fetching channel %s' % channel)

                if channel:
                    try:
                        message = await channel.fetch_message(ref["message_id"])
                        await message.edit(embed=new_embed)
                        updated += 1

                        if self.debug and 'update_all_embeds_message' in BotGlobals.DEBUG_MODULES:
                            print('[DEBUG][update_all_embeds][message] Updated message %s in channel %s' % (message, channel))
                    
                    except discord.NotFound:
                        if self.debug and 'update_all_embeds_message' in BotGlobals.DEBUG_MODULES:
                            print('[DEBUG][update_all_embeds][message] Message not found %s in channel %s' % (ref["message_id"], channel))
                            print('[DEBUG][update_all_embeds][message] Removing reference %s' % ref)

                        self.references[module].remove(ref)
                        failed += 1
                    except Exception as e:
                        print('Error updating message %s : %s' % (ref['message_id'], e))
                        failed += 1
                else:
                    if self.debug and 'update_all_embeds_channel' in BotGlobals.DEBUG_MODULES:
                        print('[DEBUG][update_all_embeds][channel] Channel not found %s' % ref["channel_id"])
                        print('[DEBUG][update_all_embeds][channel] Removing reference %s' % ref)
                    self.references[module].remove(ref)
                    failed += 1
            except Exception as e:
                print('Error updating embed reference: %s' % e)
                failed += 1
        
        self.save_references()
        return updated, failed