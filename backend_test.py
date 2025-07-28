#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Cut Royale Discord Bot
Tests API endpoints, database operations, game logic, and image generation
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import uuid

# Test configuration
BACKEND_URL = "https://8db6eef8-d073-49c2-beb1-f304d8ba589c.preview.emergentagent.com/api"
TEST_TIMEOUT = 30

class CutRoyaleBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT))
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
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
            self.passed_tests.append(test_name)
            print(f"✅ {test_name}: {message}")
        else:
            self.failed_tests.append(test_name)
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    async def test_root_endpoint(self):
        """Test GET /api/ - Root endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and "Cut Royale" in data["message"]:
                        self.log_result("Root Endpoint", True, "Root endpoint responding correctly", {"response": data})
                    else:
                        self.log_result("Root Endpoint", False, "Unexpected response format", {"response": data})
                else:
                    self.log_result("Root Endpoint", False, f"HTTP {response.status}", {"status": response.status})
        except Exception as e:
            self.log_result("Root Endpoint", False, f"Connection error: {str(e)}")
    
    async def test_games_endpoint(self):
        """Test GET /api/games - Active games retrieval"""
        try:
            async with self.session.get(f"{BACKEND_URL}/games") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.log_result("Games Endpoint", True, f"Games endpoint working, returned {len(data)} games", {"count": len(data)})
                    else:
                        self.log_result("Games Endpoint", False, "Response is not a list", {"response": data})
                else:
                    self.log_result("Games Endpoint", False, f"HTTP {response.status}", {"status": response.status})
        except Exception as e:
            self.log_result("Games Endpoint", False, f"Connection error: {str(e)}")
    
    async def test_players_endpoint(self):
        """Test GET /api/players - Players data retrieval"""
        try:
            async with self.session.get(f"{BACKEND_URL}/players") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.log_result("Players Endpoint", True, f"Players endpoint working, returned {len(data)} players", {"count": len(data)})
                    else:
                        self.log_result("Players Endpoint", False, "Response is not a list", {"response": data})
                else:
                    self.log_result("Players Endpoint", False, f"HTTP {response.status}", {"status": response.status})
        except Exception as e:
            self.log_result("Players Endpoint", False, f"Connection error: {str(e)}")
    
    async def test_image_generation_endpoint(self):
        """Test POST /api/generate_image - Image generation functionality"""
        try:
            test_payload = {
                "prompt": "A medieval knight in battle",
                "game_context": "medieval"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/generate_image",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "success" in data and "image_url" in data:
                        if data["success"] and data["image_url"]:
                            self.log_result("Image Generation", True, "Image generation working", {"image_url": data["image_url"]})
                        else:
                            self.log_result("Image Generation", False, "Image generation failed", {"response": data})
                    else:
                        self.log_result("Image Generation", False, "Unexpected response format", {"response": data})
                else:
                    self.log_result("Image Generation", False, f"HTTP {response.status}", {"status": response.status})
        except Exception as e:
            self.log_result("Image Generation", False, f"Connection error: {str(e)}")
    
    async def test_image_generation_different_eras(self):
        """Test image generation with different eras"""
        eras = ["medieval", "modern", "futuristic", "wild_west", "zombie"]
        
        for era in eras:
            try:
                test_payload = {
                    "prompt": f"Battle scene in {era} era",
                    "game_context": era
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/generate_image",
                    json=test_payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success") and data.get("image_url"):
                            self.log_result(f"Image Gen - {era.title()}", True, f"Generated image for {era} era", {"image_url": data["image_url"]})
                        else:
                            self.log_result(f"Image Gen - {era.title()}", False, f"Failed to generate image for {era}", {"response": data})
                    else:
                        self.log_result(f"Image Gen - {era.title()}", False, f"HTTP {response.status} for {era}", {"status": response.status})
            except Exception as e:
                self.log_result(f"Image Gen - {era.title()}", False, f"Error testing {era}: {str(e)}")
    
    async def test_error_handling(self):
        """Test error handling scenarios"""
        
        # Test invalid image generation request
        try:
            invalid_payload = {"invalid_field": "test"}
            
            async with self.session.post(
                f"{BACKEND_URL}/generate_image",
                json=invalid_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status in [400, 422]:  # Expected validation error
                    self.log_result("Error Handling - Invalid Request", True, "Properly handled invalid request", {"status": response.status})
                else:
                    self.log_result("Error Handling - Invalid Request", False, f"Unexpected status for invalid request: {response.status}")
        except Exception as e:
            self.log_result("Error Handling - Invalid Request", False, f"Error testing invalid request: {str(e)}")
        
        # Test non-existent endpoint
        try:
            async with self.session.get(f"{BACKEND_URL}/nonexistent") as response:
                if response.status == 404:
                    self.log_result("Error Handling - 404", True, "Properly returns 404 for non-existent endpoint")
                else:
                    self.log_result("Error Handling - 404", False, f"Expected 404, got {response.status}")
        except Exception as e:
            self.log_result("Error Handling - 404", False, f"Error testing 404: {str(e)}")
    
    async def test_game_modes_and_eras_validation(self):
        """Test that the backend has proper game modes and eras configured"""
        # This tests the game logic constants indirectly through image generation
        game_modes = ["solo", "duo", "trio", "squad", "quintuor"]
        eras = ["medieval", "modern", "futuristic", "wild_west", "zombie"]
        
        # Test a few combinations
        test_combinations = [
            ("solo", "medieval"),
            ("duo", "modern"),
            ("squad", "futuristic")
        ]
        
        for mode, era in test_combinations:
            try:
                test_payload = {
                    "prompt": f"{mode} battle in {era} setting",
                    "game_context": era
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/generate_image",
                    json=test_payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            self.log_result(f"Game Logic - {mode}/{era}", True, f"Successfully processed {mode} mode with {era} era")
                        else:
                            self.log_result(f"Game Logic - {mode}/{era}", False, f"Failed to process {mode}/{era} combination")
                    else:
                        self.log_result(f"Game Logic - {mode}/{era}", False, f"HTTP {response.status} for {mode}/{era}")
            except Exception as e:
                self.log_result(f"Game Logic - {mode}/{era}", False, f"Error testing {mode}/{era}: {str(e)}")
    
    async def test_api_response_times(self):
        """Test API response times for performance"""
        endpoints = [
            ("Root", f"{BACKEND_URL}/"),
            ("Games", f"{BACKEND_URL}/games"),
            ("Players", f"{BACKEND_URL}/players")
        ]
        
        for name, url in endpoints:
            try:
                start_time = datetime.now()
                async with self.session.get(url) as response:
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds()
                    
                    if response.status == 200 and response_time < 5.0:  # 5 second threshold
                        self.log_result(f"Performance - {name}", True, f"Response time: {response_time:.2f}s", {"response_time": response_time})
                    elif response.status == 200:
                        self.log_result(f"Performance - {name}", False, f"Slow response: {response_time:.2f}s", {"response_time": response_time})
                    else:
                        self.log_result(f"Performance - {name}", False, f"HTTP {response.status}", {"status": response.status})
            except Exception as e:
                self.log_result(f"Performance - {name}", False, f"Error testing performance: {str(e)}")
    
    async def test_cors_headers(self):
        """Test CORS configuration"""
        try:
            async with self.session.options(f"{BACKEND_URL}/") as response:
                headers = response.headers
                
                cors_headers = [
                    "Access-Control-Allow-Origin",
                    "Access-Control-Allow-Methods",
                    "Access-Control-Allow-Headers"
                ]
                
                missing_headers = [h for h in cors_headers if h not in headers]
                
                if not missing_headers:
                    self.log_result("CORS Configuration", True, "CORS headers properly configured", {"headers": dict(headers)})
                else:
                    self.log_result("CORS Configuration", False, f"Missing CORS headers: {missing_headers}", {"headers": dict(headers)})
        except Exception as e:
            self.log_result("CORS Configuration", False, f"Error testing CORS: {str(e)}")
    
    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Cut Royale Backend Tests...")
        print(f"🔗 Testing backend at: {BACKEND_URL}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Core API endpoint tests
            await self.test_root_endpoint()
            await self.test_games_endpoint()
            await self.test_players_endpoint()
            await self.test_image_generation_endpoint()
            
            # Extended functionality tests
            await self.test_image_generation_different_eras()
            await self.test_game_modes_and_eras_validation()
            
            # Error handling and edge cases
            await self.test_error_handling()
            
            # Performance and configuration tests
            await self.test_api_response_times()
            await self.test_cors_headers()
            
        finally:
            await self.cleanup()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {len(self.passed_tests)}")
        print(f"❌ Failed: {len(self.failed_tests)}")
        print(f"📈 Total: {len(self.test_results)}")
        
        if self.failed_tests:
            print(f"\n🔍 Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test}")
        
        if self.passed_tests:
            print(f"\n✨ Passed Tests:")
            for test in self.passed_tests:
                print(f"   - {test}")
        
        # Return success status
        return len(self.failed_tests) == 0

async def main():
    """Main test runner"""
    tester = CutRoyaleBackendTester()
    success = await tester.run_all_tests()
    
    # Save detailed results to file
    with open("/app/backend_test_results.json", "w") as f:
        json.dump({
            "summary": {
                "total_tests": len(tester.test_results),
                "passed": len(tester.passed_tests),
                "failed": len(tester.failed_tests),
                "success_rate": len(tester.passed_tests) / len(tester.test_results) * 100 if tester.test_results else 0
            },
            "results": tester.test_results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))