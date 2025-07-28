from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import random
import asyncio
import discord
from discord.ext import commands
import fal_client
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = False  # Don't need message content for slash commands
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Game Models
class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    discord_id: str
    username: str
    avatar_url: Optional[str] = None
    stats: Dict[str, int] = Field(default_factory=lambda: {
        "kills": 0,
        "deaths": 0,
        "wins": 0,
        "games_played": 0,
        "damage_dealt": 0
    })
    current_game_id: Optional[str] = None
    is_alive: bool = True
    team_id: Optional[str] = None
    position: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0})

class Team(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    players: List[str] = Field(default_factory=list)  # Player IDs
    alive_count: int = 0
    kills: int = 0

class Game(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel_id: str
    guild_id: str
    mode: str  # "solo", "duo", "trio", "squad", "quintuor"
    era: str
    status: str = "waiting"  # "waiting", "starting", "active", "finished"
    players: List[str] = Field(default_factory=list)  # Player IDs
    teams: List[str] = Field(default_factory=list)  # Team IDs
    max_players: int = 100
    current_players: int = 0
    alive_players: int = 0
    zone_radius: int = 100
    zone_center: Dict[str, int] = Field(default_factory=lambda: {"x": 50, "y": 50})
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    winner: Optional[str] = None  # Player ID or Team ID
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GameAction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    game_id: str
    player_id: str
    action_type: str  # "kill", "revive", "move", "loot"
    target_player_id: Optional[str] = None
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ImageGenRequest(BaseModel):
    prompt: str
    game_context: Optional[str] = None

# Eras and game modes
ERAS = {
    "medieval": {
        "name": "Medieval Era",
        "description": "Knights, castles, and sword fights",
        "weapons": ["sword", "bow", "crossbow", "mace"],
        "environment": "medieval castle, forest, village"
    },
    "modern": {
        "name": "Modern Warfare",
        "description": "Contemporary military combat",
        "weapons": ["assault rifle", "sniper rifle", "pistol", "grenade"],
        "environment": "urban city, military base, warehouse"
    },
    "futuristic": {
        "name": "Cyber Future",
        "description": "High-tech sci-fi combat",
        "weapons": ["laser rifle", "plasma cannon", "energy sword", "drone"],
        "environment": "cyber city, space station, alien planet"
    },
    "wild_west": {
        "name": "Wild West",
        "description": "Cowboys and outlaws",
        "weapons": ["revolver", "rifle", "shotgun", "dynamite"],
        "environment": "desert town, saloon, canyon, ranch"
    },
    "zombie": {
        "name": "Zombie Apocalypse",
        "description": "Survive the undead",
        "weapons": ["machete", "shotgun", "crossbow", "molotov"],
        "environment": "abandoned city, hospital, forest, bunker"
    }
}

GAME_MODES = {
    "solo": {"name": "Solo", "team_size": 1, "max_teams": 100},
    "duo": {"name": "Duos", "team_size": 2, "max_teams": 50},
    "trio": {"name": "Trios", "team_size": 3, "max_teams": 33},
    "squad": {"name": "Squads", "team_size": 4, "max_teams": 25},
    "quintuor": {"name": "Quintuor", "team_size": 5, "max_teams": 20}
}

# Funny kill messages
KILL_MESSAGES = [
    "{killer} sent {victim} to the shadow realm! 💀",
    "{victim} got absolutely yeeted by {killer}! 🚀",
    "{killer} turned {victim} into digital dust! ✨",
    "{victim} just got served by {killer}! 🍽️",
    "{killer} made {victim} rage quit life! 😤",
    "{victim} got deleted by {killer}! 🗑️",
    "{killer} sent {victim} back to the lobby permanently! 🏠",
    "{victim} got absolutely rekt by {killer}! 💥",
    "{killer} showed {victim} the exit door! 🚪",
    "{victim} got eliminated with style by {killer}! 💫",
    "{killer} made {victim} disappear like magic! 🎩✨",
    "{victim} got schooled by {killer}! 📚",
    "{killer} sent {victim} to meet their maker! ⚰️",
    "{victim} got obliterated by {killer}! 💣",
    "{killer} made {victim} take a permanent nap! 😴"
]

# Discord Bot Events
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.tree.sync()

@bot.tree.command(name="start_game", description="Start a new Cut Royale game")
async def start_game(interaction: discord.Interaction, mode: str = "solo", era: str = "modern"):
    try:
        if mode not in GAME_MODES:
            await interaction.response.send_message("❌ Invalid game mode! Available modes: " + ", ".join(GAME_MODES.keys()))
            return
        
        if era not in ERAS:
            await interaction.response.send_message("❌ Invalid era! Available eras: " + ", ".join(ERAS.keys()))
            return

        # Create new game
        game = Game(
            channel_id=str(interaction.channel.id),
            guild_id=str(interaction.guild.id),
            mode=mode,
            era=era,
            max_players=GAME_MODES[mode]["max_teams"] * GAME_MODES[mode]["team_size"]
        )
        
        await db.games.insert_one(game.dict())
        
        embed = discord.Embed(
            title="🎮 Cut Royale - Game Starting!",
            description=f"**Mode:** {GAME_MODES[mode]['name']}\n**Era:** {ERAS[era]['name']}\n**Players:** 0/{game.max_players}",
            color=0x00ff00
        )
        embed.add_field(name="How to Join", value="React with 🎮 to join the battle!", inline=False)
        embed.set_footer(text=f"Game ID: {game.id}")
        
        message = await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("🎮")
        
        # Store message ID for reactions
        await db.games.update_one({"id": game.id}, {"$set": {"message_id": str(message.id)}})
        
    except Exception as e:
        logger.error(f"Error starting game: {e}")
        await interaction.response.send_message("❌ Error starting game!")

@bot.tree.command(name="game_stats", description="View your game statistics")
async def game_stats(interaction: discord.Interaction, user: discord.Member = None):
    target_user = user or interaction.user
    
    player_data = await db.players.find_one({"discord_id": str(target_user.id)})
    if not player_data:
        await interaction.response.send_message("❌ Player not found in database!")
        return
    
    stats = player_data.get("stats", {})
    embed = discord.Embed(
        title=f"📊 {target_user.display_name}'s Stats",
        color=0x00ff00
    )
    embed.add_field(name="🎯 Kills", value=stats.get("kills", 0), inline=True)
    embed.add_field(name="💀 Deaths", value=stats.get("deaths", 0), inline=True)
    embed.add_field(name="🏆 Wins", value=stats.get("wins", 0), inline=True)
    embed.add_field(name="🎮 Games", value=stats.get("games_played", 0), inline=True)
    
    kd_ratio = stats.get("kills", 0) / max(stats.get("deaths", 1), 1)
    embed.add_field(name="📈 K/D Ratio", value=f"{kd_ratio:.2f}", inline=True)
    
    win_rate = (stats.get("wins", 0) / max(stats.get("games_played", 1), 1)) * 100
    embed.add_field(name="🎯 Win Rate", value=f"{win_rate:.1f}%", inline=True)
    
    embed.set_thumbnail(url=target_user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="View the top players")
async def leaderboard(interaction: discord.Interaction):
    players = await db.players.find().to_list(100)
    
    # Sort by wins, then by kills
    sorted_players = sorted(players, key=lambda x: (x.get("stats", {}).get("wins", 0), x.get("stats", {}).get("kills", 0)), reverse=True)
    
    embed = discord.Embed(
        title="🏆 Cut Royale Leaderboard",
        color=0xffd700
    )
    
    for i, player in enumerate(sorted_players[:10], 1):
        stats = player.get("stats", {})
        embed.add_field(
            name=f"{i}. {player['username']}",
            value=f"🏆 {stats.get('wins', 0)} wins | 🎯 {stats.get('kills', 0)} kills",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    
    if str(reaction.emoji) == "🎮":
        # Player wants to join game
        game_data = await db.games.find_one({"message_id": str(reaction.message.id)})
        if not game_data or game_data["status"] != "waiting":
            return
        
        # Check if player already in game
        player_data = await db.players.find_one({"discord_id": str(user.id)})
        if not player_data:
            # Create new player
            player = Player(
                discord_id=str(user.id),
                username=user.display_name,
                avatar_url=str(user.display_avatar.url) if user.display_avatar else None
            )
            await db.players.insert_one(player.dict())
            player_data = player.dict()
        
        # Add player to game
        if player_data["id"] not in game_data["players"]:
            await db.games.update_one(
                {"id": game_data["id"]}, 
                {
                    "$push": {"players": player_data["id"]},
                    "$inc": {"current_players": 1}
                }
            )
            
            # Update game display
            updated_game = await db.games.find_one({"id": game_data["id"]})
            embed = discord.Embed(
                title="🎮 Cut Royale - Game Starting!",
                description=f"**Mode:** {GAME_MODES[updated_game['mode']]['name']}\n**Era:** {ERAS[updated_game['era']]['name']}\n**Players:** {updated_game['current_players']}/{updated_game['max_players']}",
                color=0x00ff00
            )
            embed.add_field(name="How to Join", value="React with 🎮 to join the battle!", inline=False)
            embed.set_footer(text=f"Game ID: {updated_game['id']}")
            
            await reaction.message.edit(embed=embed)
            
            # Start game if enough players
            if updated_game["current_players"] >= 10:  # Start with minimum players for testing
                await start_battle_royale(updated_game["id"])

async def start_battle_royale(game_id: str):
    """Start the actual battle royale game"""
    game_data = await db.games.find_one({"id": game_id})
    if not game_data:
        return
    
    # Update game status
    await db.games.update_one(
        {"id": game_id}, 
        {
            "$set": {
                "status": "active",
                "start_time": datetime.utcnow(),
                "alive_players": game_data["current_players"]
            }
        }
    )
    
    channel = bot.get_channel(int(game_data["channel_id"]))
    
    # Generate game start image
    era_info = ERAS[game_data["era"]]
    prompt = f"Battle royale game starting, {era_info['environment']}, {game_data['current_players']} players, aerial view, game style, high quality"
    
    try:
        image_url = await generate_game_image(prompt, game_data["era"])
        
        embed = discord.Embed(
            title="⚔️ BATTLE ROYALE STARTED!",
            description=f"🎮 **{game_data['current_players']} players** have entered the battlefield!\n🏛️ **Era:** {era_info['name']}\n⏰ **Zone starts shrinking in 60 seconds!**",
            color=0xff6600
        )
        
        if image_url:
            embed.set_image(url=image_url)
        
        await channel.send(embed=embed)
        
        # Start game loop
        asyncio.create_task(game_loop(game_id))
        
    except Exception as e:
        logger.error(f"Error starting battle: {e}")
        embed = discord.Embed(
            title="⚔️ BATTLE ROYALE STARTED!",
            description=f"🎮 **{game_data['current_players']} players** have entered the battlefield!\n🏛️ **Era:** {era_info['name']}",
            color=0xff6600
        )
        await channel.send(embed=embed)

async def game_loop(game_id: str):
    """Main game loop handling player interactions and events"""
    game_data = await db.games.find_one({"id": game_id})
    if not game_data:
        return
    
    channel = bot.get_channel(int(game_data["channel_id"]))
    
    while True:
        # Check if game should end
        game_data = await db.games.find_one({"id": game_id})
        if game_data["alive_players"] <= 1 or game_data["status"] != "active":
            await end_game(game_id)
            break
        
        # Simulate random encounters
        alive_players = await db.players.find({"current_game_id": game_id, "is_alive": True}).to_list(100)
        
        if len(alive_players) >= 2:
            # Random encounter between two players
            player1, player2 = random.sample(alive_players, 2)
            await simulate_encounter(game_id, player1, player2, channel)
        
        await asyncio.sleep(random.randint(10, 30))  # Random interval between events

async def simulate_encounter(game_id: str, player1: dict, player2: dict, channel):
    """Simulate a player encounter with choices"""
    game_data = await db.games.find_one({"id": game_id})
    era_info = ERAS[game_data["era"]]
    
    # Generate encounter image
    prompt = f"Two players fighting in {era_info['environment']}, {era_info['name']} era, battle scene, game art style"
    image_url = await generate_game_image(prompt, game_data["era"])
    
    embed = discord.Embed(
        title="⚔️ ENCOUNTER!",
        description=f"**{player1['username']}** spots **{player2['username']}** in the distance!",
        color=0xff0000
    )
    
    if image_url:
        embed.set_image(url=image_url)
    
    embed.add_field(
        name=f"{player1['username']}, what do you do?",
        value="1️⃣ Attack immediately!\n2️⃣ Try to sneak around\n3️⃣ Call for backup",
        inline=False
    )
    
    message = await channel.send(embed=embed)
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")
    
    # Wait for player response (simplified for demo)
    await asyncio.sleep(10)
    
    # Random outcome for now
    if random.random() < 0.6:
        # Player 1 wins
        winner, loser = player1, player2
    else:
        # Player 2 wins
        winner, loser = player2, player1
    
    await handle_kill(game_id, winner, loser, channel)

async def handle_kill(game_id: str, winner: dict, loser: dict, channel):
    """Handle a player kill"""
    # Update player stats
    await db.players.update_one(
        {"id": winner["id"]},
        {"$inc": {"stats.kills": 1}}
    )
    
    await db.players.update_one(
        {"id": loser["id"]},
        {
            "$inc": {"stats.deaths": 1},
            "$set": {"is_alive": False, "current_game_id": None}
        }
    )
    
    # Update game alive count
    await db.games.update_one(
        {"id": game_id},
        {"$inc": {"alive_players": -1}}
    )
    
    # Send funny kill message
    kill_msg = random.choice(KILL_MESSAGES).format(
        killer=winner["username"],
        victim=loser["username"]
    )
    
    # Generate kill image
    game_data = await db.games.find_one({"id": game_id})
    era_info = ERAS[game_data["era"]]
    prompt = f"Victory moment, {era_info['environment']}, {era_info['name']} era, celebration, eliminated player, game art"
    image_url = await generate_game_image(prompt, game_data["era"])
    
    embed = discord.Embed(
        title="💀 ELIMINATION!",
        description=kill_msg,
        color=0x8b0000
    )
    
    if image_url:
        embed.set_image(url=image_url)
    
    embed.add_field(name="Players Remaining", value=f"{game_data['alive_players'] - 1}", inline=True)
    
    await channel.send(embed=embed)
    
    # Record action
    action = GameAction(
        game_id=game_id,
        player_id=winner["id"],
        action_type="kill",
        target_player_id=loser["id"],
        description=kill_msg
    )
    await db.game_actions.insert_one(action.dict())

async def end_game(game_id: str):
    """End the game and declare winner"""
    game_data = await db.games.find_one({"id": game_id})
    if not game_data:
        return
    
    channel = bot.get_channel(int(game_data["channel_id"]))
    
    # Find winner
    winner_data = await db.players.find_one({"current_game_id": game_id, "is_alive": True})
    
    if winner_data:
        # Update winner stats
        await db.players.update_one(
            {"id": winner_data["id"]},
            {"$inc": {"stats.wins": 1, "stats.games_played": 1}}
        )
        
        # Update game
        await db.games.update_one(
            {"id": game_id},
            {
                "$set": {
                    "status": "finished",
                    "end_time": datetime.utcnow(),
                    "winner": winner_data["id"]
                }
            }
        )
        
        # Generate victory image
        era_info = ERAS[game_data["era"]]
        prompt = f"Victory royale, champion celebration, {era_info['environment']}, {era_info['name']} era, winner, confetti, trophy"
        image_url = await generate_game_image(prompt, game_data["era"])
        
        embed = discord.Embed(
            title="👑 VICTORY ROYALE!",
            description=f"**{winner_data['username']}** is the last one standing!\n\n🎉 **WINNER WINNER!**",
            color=0xffd700
        )
        
        if image_url:
            embed.set_image(url=image_url)
        
        embed.add_field(name="Final Stats", value=f"🎮 Players: {game_data['current_players']}\n⏱️ Duration: {datetime.utcnow() - game_data['start_time']}", inline=False)
        
        await channel.send(embed=embed)
    
    # Clean up players
    await db.players.update_many(
        {"current_game_id": game_id},
        {"$set": {"current_game_id": None, "is_alive": True}}
    )

async def generate_game_image(prompt: str, era: str) -> Optional[str]:
    """Generate game images using FAL.ai"""
    try:
        # Set FAL_KEY environment variable
        os.environ["FAL_KEY"] = os.environ.get('FAL_KEY', '')
        
        enhanced_prompt = f"{prompt}, {era} theme, game art style, high quality, detailed"
        
        handler = await fal_client.submit_async(
            "fal-ai/flux/dev",
            arguments={"prompt": enhanced_prompt}
        )
        
        result = await handler.get()
        
        if result.get("images") and len(result["images"]) > 0:
            return result["images"][0]["url"]
        
        return None
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return None

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Cut Royale Discord Bot API"}

@api_router.get("/games", response_model=List[dict])
async def get_active_games():
    games = await db.games.find({"status": {"$in": ["waiting", "active"]}}).to_list(100)
    return games

@api_router.get("/players", response_model=List[dict])
async def get_players():
    players = await db.players.find().to_list(100)
    return players

@api_router.post("/generate_image")
async def generate_image_endpoint(request: ImageGenRequest):
    try:
        image_url = await generate_game_image(request.prompt, request.game_context or "modern")
        return {"success": True, "image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Start Discord bot in background
async def start_bot():
    try:
        await bot.start(os.environ.get('DISCORD_BOT_TOKEN'))
    except Exception as e:
        logger.error(f"Error starting Discord bot: {e}")

# Background task to start bot
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    await bot.close()