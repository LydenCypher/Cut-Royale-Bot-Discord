#!/usr/bin/env python3
"""
Database Testing for Cut Royale Discord Bot
Tests MongoDB connection and database operations
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid
import json

# Database configuration
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "cut_royale_db"

class DatabaseTester:
    def __init__(self):
        self.client = None
        self.db = None
        self.test_results = []
        
    async def setup(self):
        """Setup database connection"""
        try:
            self.client = AsyncIOMotorClient(MONGO_URL)
            self.db = self.client[DB_NAME]
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup database connection"""
        if self.client:
            self.client.close()
    
    def log_result(self, test_name: str, success: bool, message: str, details: dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if success:
            print(f"✅ {test_name}: {message}")
        else:
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    async def test_database_connection(self):
        """Test MongoDB connection"""
        try:
            # Test connection by listing collections
            collections = await self.db.list_collection_names()
            self.log_result("Database Connection", True, f"Connected successfully, found {len(collections)} collections", {"collections": collections})
        except Exception as e:
            self.log_result("Database Connection", False, f"Connection failed: {str(e)}")
    
    async def test_player_operations(self):
        """Test player CRUD operations"""
        try:
            # Create test player
            test_player = {
                "id": str(uuid.uuid4()),
                "discord_id": "123456789",
                "username": "TestPlayer",
                "avatar_url": "https://example.com/avatar.png",
                "stats": {
                    "kills": 5,
                    "deaths": 2,
                    "wins": 1,
                    "games_played": 3,
                    "damage_dealt": 1500
                },
                "current_game_id": None,
                "is_alive": True,
                "team_id": None,
                "position": {"x": 50, "y": 50}
            }
            
            # Insert player
            result = await self.db.players.insert_one(test_player)
            if result.inserted_id:
                self.log_result("Player Insert", True, "Player inserted successfully", {"player_id": test_player["id"]})
            else:
                self.log_result("Player Insert", False, "Failed to insert player")
                return
            
            # Find player
            found_player = await self.db.players.find_one({"id": test_player["id"]})
            if found_player and found_player["username"] == "TestPlayer":
                self.log_result("Player Find", True, "Player found successfully", {"username": found_player["username"]})
            else:
                self.log_result("Player Find", False, "Player not found or incorrect data")
            
            # Update player stats
            update_result = await self.db.players.update_one(
                {"id": test_player["id"]},
                {"$inc": {"stats.kills": 1}}
            )
            if update_result.modified_count > 0:
                self.log_result("Player Update", True, "Player stats updated successfully")
            else:
                self.log_result("Player Update", False, "Failed to update player stats")
            
            # Verify update
            updated_player = await self.db.players.find_one({"id": test_player["id"]})
            if updated_player and updated_player["stats"]["kills"] == 6:
                self.log_result("Player Update Verification", True, "Player update verified", {"new_kills": updated_player["stats"]["kills"]})
            else:
                self.log_result("Player Update Verification", False, "Player update not verified")
            
            # Delete test player
            delete_result = await self.db.players.delete_one({"id": test_player["id"]})
            if delete_result.deleted_count > 0:
                self.log_result("Player Delete", True, "Player deleted successfully")
            else:
                self.log_result("Player Delete", False, "Failed to delete player")
                
        except Exception as e:
            self.log_result("Player Operations", False, f"Error in player operations: {str(e)}")
    
    async def test_game_operations(self):
        """Test game CRUD operations"""
        try:
            # Create test game
            test_game = {
                "id": str(uuid.uuid4()),
                "channel_id": "987654321",
                "guild_id": "123456789",
                "mode": "solo",
                "era": "medieval",
                "status": "waiting",
                "players": [],
                "teams": [],
                "max_players": 100,
                "current_players": 0,
                "alive_players": 0,
                "zone_radius": 100,
                "zone_center": {"x": 50, "y": 50},
                "start_time": None,
                "end_time": None,
                "winner": None,
                "created_at": datetime.utcnow()
            }
            
            # Insert game
            result = await self.db.games.insert_one(test_game)
            if result.inserted_id:
                self.log_result("Game Insert", True, "Game inserted successfully", {"game_id": test_game["id"]})
            else:
                self.log_result("Game Insert", False, "Failed to insert game")
                return
            
            # Find active games
            active_games = await self.db.games.find({"status": {"$in": ["waiting", "active"]}}).to_list(100)
            if any(game["id"] == test_game["id"] for game in active_games):
                self.log_result("Game Query", True, f"Found {len(active_games)} active games including test game")
            else:
                self.log_result("Game Query", False, "Test game not found in active games")
            
            # Update game status
            update_result = await self.db.games.update_one(
                {"id": test_game["id"]},
                {"$set": {"status": "active", "start_time": datetime.utcnow()}}
            )
            if update_result.modified_count > 0:
                self.log_result("Game Update", True, "Game status updated successfully")
            else:
                self.log_result("Game Update", False, "Failed to update game status")
            
            # Delete test game
            delete_result = await self.db.games.delete_one({"id": test_game["id"]})
            if delete_result.deleted_count > 0:
                self.log_result("Game Delete", True, "Game deleted successfully")
            else:
                self.log_result("Game Delete", False, "Failed to delete game")
                
        except Exception as e:
            self.log_result("Game Operations", False, f"Error in game operations: {str(e)}")
    
    async def test_game_actions_operations(self):
        """Test game actions logging"""
        try:
            # Create test game action
            test_action = {
                "id": str(uuid.uuid4()),
                "game_id": str(uuid.uuid4()),
                "player_id": str(uuid.uuid4()),
                "action_type": "kill",
                "target_player_id": str(uuid.uuid4()),
                "description": "TestPlayer eliminated TargetPlayer with a sword!",
                "timestamp": datetime.utcnow()
            }
            
            # Insert action
            result = await self.db.game_actions.insert_one(test_action)
            if result.inserted_id:
                self.log_result("Game Action Insert", True, "Game action logged successfully", {"action_id": test_action["id"]})
            else:
                self.log_result("Game Action Insert", False, "Failed to log game action")
                return
            
            # Query actions for game
            game_actions = await self.db.game_actions.find({"game_id": test_action["game_id"]}).to_list(100)
            if len(game_actions) > 0:
                self.log_result("Game Action Query", True, f"Found {len(game_actions)} actions for game")
            else:
                self.log_result("Game Action Query", False, "No actions found for game")
            
            # Delete test action
            delete_result = await self.db.game_actions.delete_one({"id": test_action["id"]})
            if delete_result.deleted_count > 0:
                self.log_result("Game Action Delete", True, "Game action deleted successfully")
            else:
                self.log_result("Game Action Delete", False, "Failed to delete game action")
                
        except Exception as e:
            self.log_result("Game Action Operations", False, f"Error in game action operations: {str(e)}")
    
    async def test_database_indexes(self):
        """Test database indexes for performance"""
        try:
            # Check indexes on players collection
            player_indexes = await self.db.players.list_indexes().to_list(100)
            self.log_result("Player Indexes", True, f"Found {len(player_indexes)} indexes on players collection", {"indexes": [idx["name"] for idx in player_indexes]})
            
            # Check indexes on games collection
            game_indexes = await self.db.games.list_indexes().to_list(100)
            self.log_result("Game Indexes", True, f"Found {len(game_indexes)} indexes on games collection", {"indexes": [idx["name"] for idx in game_indexes]})
            
        except Exception as e:
            self.log_result("Database Indexes", False, f"Error checking indexes: {str(e)}")
    
    async def run_all_tests(self):
        """Run all database tests"""
        print("🗄️ Starting Cut Royale Database Tests...")
        print(f"🔗 Testing database at: {MONGO_URL}")
        print("=" * 60)
        
        if not await self.setup():
            return False
        
        try:
            await self.test_database_connection()
            await self.test_player_operations()
            await self.test_game_operations()
            await self.test_game_actions_operations()
            await self.test_database_indexes()
            
        finally:
            await self.cleanup()
        
        # Print summary
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print("\n" + "=" * 60)
        print("📊 DATABASE TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {len(passed_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"📈 Total: {len(self.test_results)}")
        
        if failed_tests:
            print(f"\n🔍 Failed Tests:")
            for test in failed_tests:
                print(f"   - {test['test']}")
        
        return len(failed_tests) == 0

async def main():
    """Main test runner"""
    tester = DatabaseTester()
    success = await tester.run_all_tests()
    
    # Save detailed results to file
    with open("/app/database_test_results.json", "w") as f:
        json.dump({
            "summary": {
                "total_tests": len(tester.test_results),
                "passed": len([r for r in tester.test_results if r["success"]]),
                "failed": len([r for r in tester.test_results if not r["success"]]),
                "success_rate": len([r for r in tester.test_results if r["success"]]) / len(tester.test_results) * 100 if tester.test_results else 0
            },
            "results": tester.test_results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/database_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))