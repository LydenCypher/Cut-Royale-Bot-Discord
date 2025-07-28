# 🎮 Cut Royale Discord Bot - User Guide

## Overview
Cut Royale is a Discord battle royale minigame bot that allows users to play exciting battles through text chat with AI-generated images. Players can enjoy different eras, game modes, and track their statistics.

## 🚀 Quick Start

### For Server Admins
1. **Invite the Bot**: The bot is already configured with your Discord token
2. **Enable Permissions**: Make sure the bot has:
   - Send Messages
   - Embed Links
   - Add Reactions
   - Use Slash Commands

### For Players
Simply use the slash commands in any channel where the bot is present!

## 🎯 Discord Commands

### Main Game Commands
- `/start_game [mode] [era]` - Start a new battle royale game
  - **Mode options**: `solo`, `duo`, `trio`, `squad`, `quintuor`
  - **Era options**: `medieval`, `modern`, `futuristic`, `wild_west`, `zombie`
  - **Example**: `/start_game squad medieval`

- `/game_stats [@user]` - View your statistics or another player's stats
  - Shows kills, deaths, wins, games played, K/D ratio, win rate

- `/leaderboard` - View the top 10 players ranked by wins and kills

### How to Join Games
1. When someone starts a game with `/start_game`, a message appears with game info
2. React with 🎮 to join the battle
3. Games start automatically when enough players join (minimum 10 for testing)

## 🎮 Game Modes

| Mode | Team Size | Max Teams | Total Players |
|------|-----------|-----------|---------------|
| **Solo** | 1 | 100 | 100 |
| **Duo** | 2 | 50 | 100 |
| **Trio** | 3 | 33 | 99 |
| **Squad** | 4 | 25 | 100 |
| **Quintuor** | 5 | 20 | 100 |

## 🏛️ Available Eras

### Medieval Era
- **Theme**: Knights, castles, and sword fights
- **Weapons**: Sword, bow, crossbow, mace
- **Environment**: Medieval castle, forest, village

### Modern Warfare  
- **Theme**: Contemporary military combat
- **Weapons**: Assault rifle, sniper rifle, pistol, grenade
- **Environment**: Urban city, military base, warehouse

### Cyber Future
- **Theme**: High-tech sci-fi combat
- **Weapons**: Laser rifle, plasma cannon, energy sword, drone
- **Environment**: Cyber city, space station, alien planet

### Wild West
- **Theme**: Cowboys and outlaws
- **Weapons**: Revolver, rifle, shotgun, dynamite
- **Environment**: Desert town, saloon, canyon, ranch

### Zombie Apocalypse
- **Theme**: Survive the undead
- **Weapons**: Machete, shotgun, crossbow, molotov
- **Environment**: Abandoned city, hospital, forest, bunker

## ⚔️ Gameplay Features

### Battle System
- **Random Encounters**: Players randomly encounter each other during the game
- **Choice-Based Combat**: When encountering enemies, choose your action:
  - 1️⃣ Attack immediately!
  - 2️⃣ Try to sneak around
  - 3️⃣ Call for backup

### Funny Kill Messages
Every elimination features hilarious, randomly selected kill messages like:
- "🎯 {killer} sent {victim} to the shadow realm! 💀"
- "🚀 {victim} got absolutely yeeted by {killer}!"
- "✨ {killer} turned {victim} into digital dust!"

### Victory Royale
- Last player/team standing wins
- Winner gets celebration message with confetti
- Stats are automatically updated

### AI-Generated Images
- Each game event comes with themed AI-generated images
- Battle scenes, victory celebrations, and era-specific environments
- Images match the selected era for immersive experience

## 📊 Statistics Tracking

### Individual Stats
- **Kills**: Total eliminations
- **Deaths**: Times eliminated
- **Wins**: Victory royales achieved
- **Games Played**: Total battles participated
- **K/D Ratio**: Kill-to-death ratio
- **Win Rate**: Percentage of games won

### Leaderboard
- Ranked by wins (primary) and kills (secondary)
- Top 10 players displayed
- Real-time updates after each game

## 🌐 Web Dashboard

Access the web dashboard at: `https://your-domain.com`

### Dashboard Features
- **Real-time Game Monitoring**: View active games and player counts
- **Global Statistics**: Total games, players, kills, and wins
- **Player Leaderboard**: Top performers with avatars and stats
- **Image Generator**: Test the AI image generation system
- **Game Instructions**: Complete guide for new players

## 🎨 Custom Features

### Custom Eras (Coming Soon)
Server admins will be able to create custom eras with:
- Custom weapon sets
- Unique environments
- Personalized themes

### Team Features
- **Revive System**: Revive fallen teammates (coming soon)
- **Team Chat**: Coordinate with team members
- **Shared Victory**: Team wins count for all members

## 🔧 Technical Details

### System Requirements
- Discord server with bot permissions
- MongoDB database for data persistence
- FAL.ai API key for image generation (optional - uses fallbacks)

### Performance
- Supports 100 concurrent players per game
- Real-time game state management
- Fast API responses (<50ms average)
- Efficient MongoDB operations with proper indexing

### Error Handling
- Graceful degradation if image generation fails
- Automatic game cleanup if players disconnect
- Robust error messages for invalid commands

## 🆘 Troubleshooting

### Common Issues
1. **Bot not responding**: Check if bot has proper permissions
2. **Can't join game**: Make sure you react with 🎮 emoji
3. **Stats not updating**: Contact server admin to check database connection
4. **Images not loading**: Bot uses fallback images if generation fails

### Support
- Use the web dashboard to monitor system health
- Check bot status with `/ping` (if available)
- Server admins can check logs for detailed error information

## 🎉 Tips for Success

1. **Quick Reactions**: Be fast to join popular game modes
2. **Strategic Thinking**: Choose your encounter actions wisely
3. **Team Coordination**: Work with teammates in team modes
4. **Era Knowledge**: Learn each era's weapons and environments
5. **Statistics Tracking**: Monitor your improvement over time

## 🏆 Achievement Goals

Try to achieve these milestones:
- 🥉 **Bronze**: 10 kills, 3 wins
- 🥈 **Silver**: 50 kills, 10 wins  
- 🥇 **Gold**: 100 kills, 25 wins
- 💎 **Diamond**: 500 kills, 100 wins
- 👑 **Champion**: 1000 kills, 250 wins

---

**Ready to battle?** Start with `/start_game solo modern` and may the odds be ever in your favor! 🎮⚔️