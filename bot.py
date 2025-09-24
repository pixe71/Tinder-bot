import discord
from discord.ext import commands
import json
import os
import random
from typing import Dict, List, Set

# Configuration du bot
TOKEN = 'MTQyMDE2MzQ1NzI2MDU4OTE0Ng.G7ZuHJ.9M_DJtfVkWor1509EzzN1K1MOnsYWNyNeGs4eQ'
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

class TinderBot:
    def __init__(self):
        self.profiles = {}  # {user_id: {"likes": set(), "dislikes": set(), "active": bool}}
        self.matches = {}   # {user_id: set(matched_users)}
        self.data_file = "tinder_data.json"
        self.load_data()
    
    def load_data(self):
        """Charge les données depuis le fichier JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    # Conversion des listes en sets pour les likes/dislikes
                    for user_id, profile in data.get('profiles', {}).items():
                        self.profiles[int(user_id)] = {
                            "likes": set(profile.get('likes', [])),
                            "dislikes": set(profile.get('dislikes', [])),
                            "active": profile.get('active', True)
                        }
                    # Conversion pour les matches
                    for user_id, matches in data.get('matches', {}).items():
                        self.matches[int(user_id)] = set(matches)
            except Exception as e:
                print(f"Erreur lors du chargement des données: {e}")
    
    def save_data(self):
        """Sauvegarde les données dans le fichier JSON"""
        try:
            data = {
                'profiles': {},
                'matches': {}
            }
            # Conversion des sets en listes pour la sérialisation JSON
            for user_id, profile in self.profiles.items():
                data['profiles'][str(user_id)] = {
                    "likes": list(profile['likes']),
                    "dislikes": list(profile['dislikes']),
                    "active": profile['active']
                }
            for user_id, matches in self.matches.items():
                data['matches'][str(user_id)] = list(matches)
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
    
    def get_profile(self, user_id: int) -> Dict:
        """Récupère ou crée un profil utilisateur"""
        if user_id not in self.profiles:
            self.profiles[user_id] = {
                "likes": set(),
                "dislikes": set(),
                "active": True
            }
        return self.profiles[user_id]
    
    def get_next_person(self, user_id: int, guild_members: List[discord.Member]) -> discord.Member:
        """Trouve la prochaine personne à swiper"""
        profile = self.get_profile(user_id)
        already_seen = profile['likes'].union(profile['dislikes'])
        
        # Filtre les membres éligibles
        eligible_members = []
        for member in guild_members:
            if (member.id != user_id and 
                member.id not in already_seen and 
                not member.bot and
                self.profiles.get(member.id, {}).get('active', True)):
                eligible_members.append(member)
        
        if not eligible_members:
            return None
        
        return random.choice(eligible_members)
    
    def swipe(self, user_id: int, target_id: int, like: bool) -> bool:
        """Effectue un swipe et retourne True s'il y a match"""
        profile = self.get_profile(user_id)
        
        if like:
            profile['likes'].add(target_id)
            # Vérifier s'il y a match (l'autre personne nous a aussi liké)
            target_profile = self.get_profile(target_id)
            if user_id in target_profile['likes']:
                # Match trouvé !
                if user_id not in self.matches:
                    self.matches[user_id] = set()
                if target_id not in self.matches:
                    self.matches[target_id] = set()
                
                self.matches[user_id].add(target_id)
                self.matches[target_id].add(user_id)
                self.save_data()
                return True
        else:
            profile['dislikes'].add(target_id)
        
        self.save_data()
        return False

# Instance globale du système Tinder
tinder_system = TinderBot()

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté !')
    print('Bot Tinder Discord prêt !')

class SwipeView(discord.ui.View):
    def __init__(self, user_id: int, target_member: discord.Member, guild):
        super().__init__(timeout=300)  # 5 minutes de timeout
        self.user_id = user_id
        self.target_member = target_member
        self.guild = guild
    
    @discord.ui.button(label='❤️', style=discord.ButtonStyle.success)
    async def like_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Ce n'est pas votre session de swipe !", ephemeral=True)
            return
        
        # Effectuer le swipe
        is_match = tinder_system.swipe(self.user_id, self.target_member.id, True)
        
        if is_match:
            # Annonce du match à tout le serveur
            embed = discord.Embed(
                title="🎉 NOUVEAU MATCH ! 🎉",
                description=f"{interaction.user.mention} et {self.target_member.mention} ont matché !",
                color=0xFF69B4
            )
            embed.add_field(name="💕", value="Vous pouvez maintenant discuter !", inline=False)
            
            # Envoie l'annonce dans le canal actuel avec @everyone
            await interaction.response.edit_message(
                content="@everyone",
                embed=embed,
                view=None
            )
        else:
            await interaction.response.edit_message(
                content="❤️ Vous avez liké cette personne !",
                embed=None,
                view=None
            )
        
        # Proposer automatiquement la prochaine personne
        await self.show_next_person(interaction)
    
    @discord.ui.button(label='❌', style=discord.ButtonStyle.danger)
    async def dislike_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Ce n'est pas votre session de swipe !", ephemeral=True)
            return
        
        # Effectuer le swipe (dislike)
        tinder_system.swipe(self.user_id, self.target_member.id, False)
        
        await interaction.response.edit_message(
            content="❌ Vous avez passé cette personne !",
            embed=None,
            view=None
        )
        
        # Proposer automatiquement la prochaine personne
        await self.show_next_person(interaction)
    
    async def show_next_person(self, interaction):
        """Affiche automatiquement la prochaine personne"""
        import asyncio
        await asyncio.sleep(2)  # Petite pause
        
        next_person = tinder_system.get_next_person(self.user_id, self.guild.members)
        if next_person:
            embed = discord.Embed(
                title="Personne suivante",
                description=f"**{next_person.display_name}**",
                color=0x00ff00
            )
            if next_person.avatar:
                embed.set_image(url=next_person.avatar.url)
            embed.add_field(name="Statut", value=str(next_person.status), inline=True)
            
            new_view = SwipeView(self.user_id, next_person, self.guild)
            await interaction.followup.send(embed=embed, view=new_view)
        else:
            await interaction.followup.send("Plus personne à swiper pour le moment ! 😅")

@bot.command(name='swipe')
async def swipe_command(ctx):
    """Commencer à swiper"""
    if ctx.author.bot:
        return
    
    # Trouve une personne à swiper
    next_person = tinder_system.get_next_person(ctx.author.id, ctx.guild.members)
    
    if not next_person:
        await ctx.send("Plus personne à swiper pour le moment ! 😅")
        return
    
    # Crée l'embed pour afficher la personne
    embed = discord.Embed(
        title="💕 Tinder Discord 💕",
        description=f"**{next_person.display_name}**",
        color=0xFF1493
    )
    
    if next_person.avatar:
        embed.set_image(url=next_person.avatar.url)
    
    embed.add_field(name="Statut", value=str(next_person.status), inline=True)
    embed.add_field(name="Depuis", value=next_person.joined_at.strftime("%d/%m/%Y") if next_person.joined_at else "Inconnu", inline=True)
    embed.set_footer(text="Cliquez sur ❤️ pour liker ou ❌ pour passer")
    
    # Crée la vue avec les boutons
    view = SwipeView(ctx.author.id, next_person, ctx.guild)
    await ctx.send(embed=embed, view=view)

@bot.command(name='matches')
async def matches_command(ctx):
    """Voir ses matches"""
    user_matches = tinder_system.matches.get(ctx.author.id, set())
    
    if not user_matches:
        await ctx.send("Vous n'avez pas encore de matches ! 💔")
        return
    
    embed = discord.Embed(
        title="💕 Vos Matches 💕",
        color=0xFF69B4
    )
    
    match_list = []
    for match_id in user_matches:
        member = ctx.guild.get_member(match_id)
        if member:
            match_list.append(f"• {member.display_name}")
    
    if match_list:
        embed.description = "\n".join(match_list)
    else:
        embed.description = "Aucun match actif trouvé"
    
    await ctx.send(embed=embed)

@bot.command(name='profile')
async def profile_command(ctx):
    """Voir ses statistiques"""
    profile = tinder_system.get_profile(ctx.author.id)
    matches = len(tinder_system.matches.get(ctx.author.id, set()))
    
    embed = discord.Embed(
        title=f"Profil de {ctx.author.display_name}",
        color=0x9932CC
    )
    
    embed.add_field(name="❤️ Likes donnés", value=len(profile['likes']), inline=True)
    embed.add_field(name="❌ Passes", value=len(profile['dislikes']), inline=True)
    embed.add_field(name="💕 Matches", value=matches, inline=True)
    embed.add_field(name="📊 Statut", value="🟢 Actif" if profile['active'] else "🔴 Inactif", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='toggle')
async def toggle_command(ctx):
    """Activer/désactiver son profil"""
    profile = tinder_system.get_profile(ctx.author.id)
    profile['active'] = not profile['active']
    tinder_system.save_data()
    
    status = "activé" if profile['active'] else "désactivé"
    await ctx.send(f"Votre profil a été {status} !")

@bot.command(name='reset')
async def reset_command(ctx):
    """Reset son profil (admin seulement)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Seuls les administrateurs peuvent utiliser cette commande !")
        return
    
    if ctx.author.id in tinder_system.profiles:
        del tinder_system.profiles[ctx.author.id]
    if ctx.author.id in tinder_system.matches:
        del tinder_system.matches[ctx.author.id]
    
    tinder_system.save_data()
    await ctx.send("Votre profil a été réinitialisé !")

@bot.command(name='help_tinder')
async def help_tinder_command(ctx):
    """Affiche l'aide"""
    embed = discord.Embed(
        title="🆘 Aide - Tinder Discord",
        description="Voici les commandes disponibles :",
        color=0x00BFFF
    )
    
    commands_list = [
        ("!swipe", "Commencer à swiper"),
        ("!matches", "Voir vos matches"),
        ("!profile", "Voir vos statistiques"),
        ("!toggle", "Activer/désactiver votre profil"),
        ("!reset", "Réinitialiser votre profil (admin)"),
        ("!help_tinder", "Afficher cette aide")
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    await ctx.send(embed=embed)

# Lancer le bot
if __name__ == "__main__":
    bot.run(TOKEN)
