# -*- coding: utf-8 -*-
# THIS IS THE FULL CODE YOU PROVIDED, WITH THE NEW /sendmsg COMMAND ADDED. NO LINES REMOVED.
import os
import discord
from discord.ext import commands
from discord import ui
import asyncio
import random

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WELCOME_CHANNEL_NAME = "welcome"
AUTO_ROLE_NAME = "Fastmice Member"
SERVER_OWNER_ID = os.environ.get("SERVER_OWNER_ID")
SERVER_OWNER_USERNAME = "a.64_"
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@Amr_GamingX1"

# --- SETUP ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- SECURITY CHECK DECORATOR ---
def is_owner():
    def predicate(interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) == SERVER_OWNER_ID
    return discord.app_commands.check(predicate)

# --- MODAL CLASS FOR SENDING MESSAGE WITH PICTURE (CORRECTED) ---
class MessageWithPicModal(ui.Modal, title='Message Content for Picture'):
    message_content = ui.TextInput(label='Message (multi-line supported)', style=discord.TextStyle.paragraph, placeholder='Write your message here...', required=True)
    def __init__(self, target_channel: discord.TextChannel, attachment: discord.Attachment):
        super().__init__()
        self.target_channel = target_channel
        self.attachment = attachment
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        file = await self.attachment.to_file()
        await self.target_channel.send(content=self.message_content.value, file=file)
        await interaction.followup.send(f'Message with picture sent to {self.target_channel.mention}!', ephemeral=True)

# --- MODAL CLASS FOR SENDING MESSAGE WITH VIDEO/GIF (CORRECTED) ---
class MessageWithVidModal(ui.Modal, title='Message Content for Video/GIF'):
    message_content = ui.TextInput(label='Message (multi-line supported)', style=discord.TextStyle.paragraph, placeholder='Write your message here...', required=True)
    def __init__(self, target_channel: discord.TextChannel, attachment: discord.Attachment):
        super().__init__()
        self.target_channel = target_channel
        self.attachment = attachment
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        file = await self.attachment.to_file()
        await self.target_channel.send(content=self.message_content.value, file=file)
        await interaction.followup.send(f'Message with video/gif sent to {self.target_channel.mention}!', ephemeral=True)

# --- NEW MODAL CLASS FOR SENDING TEXT-ONLY MESSAGES ---
class TextMessageModal(ui.Modal, title='Send a Text Message'):
    message_content = ui.TextInput(label='Message (multi-line supported)', style=discord.TextStyle.paragraph, placeholder='Write your message here...', required=True)
    def __init__(self, target_channel: discord.TextChannel):
        super().__init__()
        self.target_channel = target_channel
    async def on_submit(self, interaction: discord.Interaction):
        await self.target_channel.send(self.message_content.value)
        await interaction.response.send_message(f'Text message sent to {self.target_channel.mention}!', ephemeral=True)

# --- EVENTS ---
@bot.event
async def on_ready():
    print("--------------------------------------")
    print(f"Bot logged in as: {bot.user}")
    activity = discord.Activity(type=discord.ActivityType.playing, name="Fastmice")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"Bot status set to '{activity.name}'")
    print("Attempting to sync all application commands...")
    try:
        synced = await bot.tree.sync()
        print(f"SUCCESS: Synced {len(synced)} slash commands.")
        print("--------------------------------------")
        print("Fastmice Bot is fully ready and online!")
    except Exception as e:
        print(f"!!!!!!!!!! ERROR DURING SYNC !!!!!!!!!!!\n{e}\n--------------------------------------")

@bot.event
async def on_member_join(member: discord.Member):
    await send_welcome_messages(member)

# --- SECURE on_message FUNCTION ---
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if not isinstance(message.author, discord.Member) or not message.author.guild_permissions.administrator:
        message_content_lower = message.content.lower()
        PROFANITY_LIST = ["badword1", "badword2", "كلمة سيئة"] 
        if any(word in message_content_lower for word in PROFANITY_LIST):
            try:
                await message.delete()
                warning_msg = await message.channel.send(f"{message.author.mention}, please avoid using inappropriate language.")
                await asyncio.sleep(5)
                await warning_msg.delete()
            except discord.Forbidden:
                print("Bot does not have permissions to delete messages.")
            except Exception as e:
                print(f"Error during profanity check: {e}")

# --- HELPER FUNCTION (WELCOME MESSAGE) ---
async def send_welcome_messages(member: discord.Member):
    guild = member.guild
    try:
        role = discord.utils.get(guild.roles, name=AUTO_ROLE_NAME)
        if role: await member.add_roles(role)
    except Exception as e:
        print(f"Failed to assign role: {e}")
    welcome_channel = discord.utils.get(guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if welcome_channel:
        embed = discord.Embed(title=f"🎉 Welcome to {guild.name}! 🎉", description=f"Hello {member.mention}, we're so happy to have you here!", color=discord.Color.blue())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="📺 Subscribe to our YouTube Channel!", value=f"Follow all our game updates and news [by clicking here]({YOUTUBE_CHANNEL_URL})!", inline=False)
        embed.set_footer(text="Have a great time in our community!")
        await welcome_channel.send(embed=embed)
    try:
        dm_embed = discord.Embed(title="Welcome to the Fastmice Community!", description=f"Hey {member.name}! Welcome! Use `/help` in the server to see available commands.", color=0xFFD700)
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        print(f"Could not send a DM to {member.name}.")

# --- SLASH COMMANDS (OWNER ONLY) ---

# --- NEW COMMAND ADDED HERE ---
@bot.tree.command(name="sendmsg", description="[OWNER ONLY] Sends a multi-line text message.")
@is_owner()
async def sendmsg(interaction: discord.Interaction, channel: discord.TextChannel):
    modal = TextMessageModal(target_channel=channel)
    await interaction.response.send_modal(modal)

@bot.tree.command(name="sendpic", description="[OWNER ONLY] Sends a single picture.")
@is_owner()
async def sendpic(interaction: discord.Interaction, channel: discord.TextChannel, attachment: discord.Attachment):
    await interaction.response.defer(ephemeral=True)
    file = await attachment.to_file()
    await channel.send(file=file)
    await interaction.followup.send(f"Picture sent to {channel.mention}.", ephemeral=True)

@bot.tree.command(name="sendvidgif", description="[OWNER ONLY] Sends a single video or GIF.")
@is_owner()
async def sendvidgif(interaction: discord.Interaction, channel: discord.TextChannel, attachment: discord.Attachment):
    await interaction.response.defer(ephemeral=True)
    file = await attachment.to_file()
    await channel.send(file=file)
    await interaction.followup.send(f"Video/GIF sent to {channel.mention}.", ephemeral=True)
    
@bot.tree.command(name="sendmsgpic", description="[OWNER ONLY] Sends a picture with a multi-line message.")
@is_owner()
async def sendmsgpic(interaction: discord.Interaction, channel: discord.TextChannel, attachment: discord.Attachment):
    modal = MessageWithPicModal(target_channel=channel, attachment=attachment)
    await interaction.response.send_modal(modal)

@bot.tree.command(name="sendvidgifmsg", description="[OWNER ONLY] Sends a video/gif with a multi-line message.")
@is_owner()
async def sendvidgifmsg(interaction: discord.Interaction, channel: discord.TextChannel, attachment: discord.Attachment):
    modal = MessageWithVidModal(target_channel=channel, attachment=attachment)
    await interaction.response.send_modal(modal)

@bot.tree.command(name="sendgallery", description="[OWNER ONLY] Sends up to 10 pictures in one message.")
@is_owner()
async def sendgallery(interaction: discord.Interaction, channel: discord.TextChannel,
    attachment1: discord.Attachment, attachment2: discord.Attachment=None, attachment3: discord.Attachment=None,
    attachment4: discord.Attachment=None, attachment5: discord.Attachment=None, attachment6: discord.Attachment=None,
    attachment7: discord.Attachment=None, attachment8: discord.Attachment=None, attachment9: discord.Attachment=None, attachment10: discord.Attachment=None):
    await interaction.response.defer(ephemeral=True)
    attachments = [att for att in [attachment1, attachment2, attachment3, attachment4, attachment5, attachment6, attachment7, attachment8, attachment9, attachment10] if att is not None]
    files_to_send = [await att.to_file() for att in attachments]
    await channel.send(files=files_to_send)
    await interaction.followup.send(f"Sent {len(files_to_send)} pictures to {channel.mention}.", ephemeral=True)

@bot.tree.command(name="kick", description="[OWNER ONLY] Kicks a member from the server.")
@is_owner()
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {member.mention}. Reason: {reason}", ephemeral=True)

@bot.tree.command(name="ban", description="[OWNER ONLY] Bans a member from the server.")
@is_owner()
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"Banned {member.mention}. Reason: {reason}", ephemeral=True)

@bot.tree.command(name="addrole", description="[OWNER ONLY] Gives a role to a member.")
@is_owner()
async def addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await interaction.response.send_message(f"Added `{role.name}` to {member.mention}.", ephemeral=True)

@bot.tree.command(name="deleterole", description="[OWNER ONLY] Removes a role from a member.")
@is_owner()
async def deleterole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if role not in member.roles:
        await interaction.response.send_message(f"{member.mention} does not have the `{role.name}` role.", ephemeral=True)
        return
    await member.remove_roles(role)
    await interaction.response.send_message(f"Removed `{role.name}` from {member.mention}.", ephemeral=True)

@bot.tree.command(name="testwelcome", description="[OWNER ONLY] Manually triggers the welcome message for a user.")
@is_owner()
async def testwelcome(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"Sending a test welcome to {member.mention}...", ephemeral=True)
    await send_welcome_messages(member)

@bot.tree.command(name="debug_id", description="[OWNER ONLY] Checks if your ID matches the owner's ID.")
@is_owner()
async def debug_id(interaction: discord.Interaction):
    your_id = str(interaction.user.id)
    stored_id = SERVER_OWNER_ID
    embed = discord.Embed(title="🕵️ ID Verification Check", color=discord.Color.gold())
    embed.add_field(name="Your User ID (from Discord)", value=f"`{your_id}`", inline=False)
    embed.add_field(name="Owner ID (stored in code)", value=f"`{stored_id}`", inline=False)
    if your_id == stored_id:
        embed.add_field(name="Result", value="✅ **MATCH!** The IDs are identical. Owner commands should work for you.", inline=False)
        embed.color = discord.Color.green()
    else:
        embed.add_field(name="Result", value="❌ **NO MATCH!** The IDs are different. This is why you are being blocked.", inline=False)
        embed.set_footer(text="ACTION: Copy your User ID from above and paste it EXACTLY into the SERVER_OWNER_ID variable in the code.")
        embed.color = discord.Color.red()
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- SLASH COMMANDS (PUBLIC) ---

@bot.tree.command(name="websites", description="Shows all official Fastmice websites and social links.")
async def websites(interaction: discord.Interaction):
    embed = discord.Embed(title="🔗 Fastmice Official Links", description="Here are all our official pages. Follow us everywhere!", color=0x1DA1F2)
    links_text = ("🌐 **Website 1:** [fastmice.free.nf](http://fastmice.free.nf/?i=1)\n"
                 "🌐 **Website 2:** [fastmicesite.rf.gd](http://fastmicesite.rf.gd/?i=1)\n"
                 "📘 **Facebook:** [Follow us on Facebook](https://www.facebook.com/profile.php?id=61576051520943)\n"
                 "🐦 **X (Twitter):** [@FastmiceEXE](https://x.com/FastmiceEXE)\n"
                 "🎵 **TikTok:** [@fastmice](https://www.tiktok.com/@fastmice)\n"
                 "💬 **Discord:** [Join our Server](https://discord.gg/sfR8bWK6sc)")
    embed.add_field(name="Our Pages", value=links_text, inline=False)
    embed.set_footer(text="Thanks for your support!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Shows a list of all available commands.")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Fastmice Bot Help", description="Here is a list of my commands:", color=discord.Color.orange())
    public_commands_list = ("`/help` - Shows this help message.\n"
                           "`/founder` - Shows the server founder's name.\n"
                           "`/roll` - Rolls a dice.\n"
                           "`/websites` - Shows all our official links.")
    embed.add_field(name="👋 Public Commands", value=public_commands_list, inline=False)
    if str(interaction.user.id) == SERVER_OWNER_ID:
        admin_commands_list = ("`/sendmsg` `/sendpic` `/sendvidgif` `/sendmsgpic` `/sendvidgifmsg`\n"
                              "`/sendgallery` `/kick` `/ban` `/addrole` `/deleterole`\n"
                              "`/testwelcome` `/debug_id`")
        embed.add_field(name="👑 Owner Commands (Visible to you only)", value=admin_commands_list, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="founder", description="Shows the name of the server founder.")
async def founder(interaction: discord.Interaction):
    await interaction.response.send_message(f"The founder of this awesome server is <@{SERVER_OWNER_ID}> ({SERVER_OWNER_USERNAME})! 👑")

@bot.tree.command(name="roll", description="Roll a dice!")
async def roll(interaction: discord.Interaction, sides: int = 6):
    if sides < 2:
        await interaction.response.send_message("A dice must have at least 2 sides!", ephemeral=True)
        return
    result = random.randint(1, sides)
    await interaction.response.send_message(f"{interaction.user.mention} rolled a {sides}-sided dice and got a **{result}**! 🎲")

# --- ERROR HANDLING SECTION ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CheckFailure):
        await interaction.response.send_message("You are not the owner of this bot and cannot use this command.", ephemeral=True)
    elif isinstance(error, discord.app_commands.CommandInvokeError) and isinstance(error.original, discord.Forbidden):
        await interaction.response.send_message("I don't have the necessary permissions to do that. Please check my role and channel permissions.", ephemeral=True)
    else:
        print(f"An unhandled error occurred in a slash command: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("An unexpected error occurred. Please try again later.", ephemeral=True)

# --- RUN THE BOT ---
if __name__ == "__main__":
    bot.run(BOT_TOKEN)