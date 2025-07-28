import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [activeGames, setActiveGames] = useState([]);
  const [players, setPlayers] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [imagePrompt, setImagePrompt] = useState("");
  const [generatedImage, setGeneratedImage] = useState(null);
  const [imageLoading, setImageLoading] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [gamesResponse, playersResponse] = await Promise.all([
        axios.get(`${API}/games`),
        axios.get(`${API}/players`)
      ]);
      
      setActiveGames(gamesResponse.data);
      setPlayers(playersResponse.data);
      
      // Calculate global stats
      const totalGames = gamesResponse.data.length;
      const totalPlayers = playersResponse.data.length;
      const totalKills = playersResponse.data.reduce((sum, player) => sum + (player.stats?.kills || 0), 0);
      const totalWins = playersResponse.data.reduce((sum, player) => sum + (player.stats?.wins || 0), 0);
      
      setStats({
        totalGames,
        totalPlayers,
        totalKills,
        totalWins
      });
      
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
      setLoading(false);
    }
  };

  const generateImage = async () => {
    if (!imagePrompt.trim()) return;
    
    setImageLoading(true);
    try {
      const response = await axios.post(`${API}/generate_image`, {
        prompt: imagePrompt,
        game_context: "modern"
      });
      
      if (response.data.success) {
        setGeneratedImage(response.data.image_url);
      }
    } catch (error) {
      console.error("Error generating image:", error);
      alert("Error generating image. Please try again.");
    } finally {
      setImageLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading Cut Royale Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <div className="bg-black bg-opacity-50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-white mb-2">⚔️ Cut Royale</h1>
          <p className="text-purple-300">Discord Battle Royale Bot Dashboard</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm font-medium">Active Games</p>
                <p className="text-3xl font-bold text-white">{stats.totalGames || 0}</p>
              </div>
              <div className="p-3 bg-purple-500 bg-opacity-30 rounded-lg">
                🎮
              </div>
            </div>
          </div>
          
          <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-300 text-sm font-medium">Total Players</p>
                <p className="text-3xl font-bold text-white">{stats.totalPlayers || 0}</p>
              </div>
              <div className="p-3 bg-blue-500 bg-opacity-30 rounded-lg">
                👥
              </div>
            </div>
          </div>
          
          <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-300 text-sm font-medium">Total Kills</p>
                <p className="text-3xl font-bold text-white">{stats.totalKills || 0}</p>
              </div>
              <div className="p-3 bg-red-500 bg-opacity-30 rounded-lg">
                🎯
              </div>
            </div>
          </div>
          
          <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-300 text-sm font-medium">Total Wins</p>
                <p className="text-3xl font-bold text-white">{stats.totalWins || 0}</p>
              </div>
              <div className="p-3 bg-yellow-500 bg-opacity-30 rounded-lg">
                👑
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Active Games */}
          <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
            <h2 className="text-2xl font-bold text-white mb-4">🎮 Active Games</h2>
            {activeGames.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">🎯</div>
                <p className="text-purple-300">No active games</p>
                <p className="text-sm text-purple-400 mt-2">Use <code>/start_game</code> in Discord to begin!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {activeGames.map((game) => (
                  <div key={game.id} className="bg-black bg-opacity-30 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="text-lg font-semibold text-white">{game.era} - {game.mode}</h3>
                        <p className="text-sm text-purple-300">Status: {game.status}</p>
                      </div>
                      <div className="text-right">
                        <span className="inline-block bg-purple-500 bg-opacity-50 text-white px-2 py-1 rounded text-sm">
                          {game.current_players}/{game.max_players}
                        </span>
                      </div>
                    </div>
                    <div className="flex justify-between text-sm text-purple-200">
                      <span>Players: {game.current_players}</span>
                      <span>Alive: {game.alive_players || game.current_players}</span>
                    </div>
                    {game.status === 'active' && (
                      <div className="mt-2 w-full bg-gray-600 rounded-full h-2">
                        <div 
                          className="bg-red-500 h-2 rounded-full transition-all duration-300"
                          style={{width: `${((game.current_players - (game.alive_players || game.current_players)) / game.current_players) * 100}%`}}
                        ></div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Image Generator */}
          <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
            <h2 className="text-2xl font-bold text-white mb-4">🎨 Image Generator</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-purple-300 mb-2">
                  Generate Battle Royale Images
                </label>
                <input
                  type="text"
                  value={imagePrompt}
                  onChange={(e) => setImagePrompt(e.target.value)}
                  placeholder="e.g., medieval battle scene, futuristic combat arena..."
                  className="w-full px-3 py-2 bg-black bg-opacity-30 border border-purple-500 border-opacity-30 rounded-lg text-white placeholder-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <button
                onClick={generateImage}
                disabled={imageLoading || !imagePrompt.trim()}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-600 text-white font-bold py-3 px-4 rounded-lg transition-all duration-300"
              >
                {imageLoading ? "Generating..." : "Generate Image"}
              </button>
              
              {generatedImage && (
                <div className="mt-4">
                  <img
                    src={generatedImage}
                    alt="Generated battle royale scene"
                    className="w-full rounded-lg shadow-lg"
                  />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Players Leaderboard */}
        <div className="mt-8 bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
          <h2 className="text-2xl font-bold text-white mb-4">🏆 Leaderboard</h2>
          {players.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">👤</div>
              <p className="text-purple-300">No players yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left border-b border-white border-opacity-20">
                    <th className="py-3 text-purple-300 font-medium">Rank</th>
                    <th className="py-3 text-purple-300 font-medium">Player</th>
                    <th className="py-3 text-purple-300 font-medium">Wins</th>
                    <th className="py-3 text-purple-300 font-medium">Kills</th>
                    <th className="py-3 text-purple-300 font-medium">Games</th>
                    <th className="py-3 text-purple-300 font-medium">K/D</th>
                  </tr>
                </thead>
                <tbody>
                  {players
                    .sort((a, b) => (b.stats?.wins || 0) - (a.stats?.wins || 0))
                    .slice(0, 10)
                    .map((player, index) => {
                      const kills = player.stats?.kills || 0;
                      const deaths = player.stats?.deaths || 0;
                      const kd = deaths > 0 ? (kills / deaths).toFixed(2) : kills.toFixed(2);
                      
                      return (
                        <tr key={player.id} className="border-b border-white border-opacity-10">
                          <td className="py-3 text-white font-bold">
                            {index === 0 && "🥇"}
                            {index === 1 && "🥈"}
                            {index === 2 && "🥉"}
                            {index > 2 && `#${index + 1}`}
                          </td>
                          <td className="py-3">
                            <div className="flex items-center space-x-3">
                              {player.avatar_url && (
                                <img
                                  src={player.avatar_url}
                                  alt={player.username}
                                  className="w-8 h-8 rounded-full"
                                />
                              )}
                              <span className="text-white font-medium">{player.username}</span>
                            </div>
                          </td>
                          <td className="py-3 text-yellow-300 font-bold">{player.stats?.wins || 0}</td>
                          <td className="py-3 text-red-300">{kills}</td>
                          <td className="py-3 text-blue-300">{player.stats?.games_played || 0}</td>
                          <td className="py-3 text-purple-300">{kd}</td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Game Instructions */}
        <div className="mt-8 bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
          <h2 className="text-2xl font-bold text-white mb-4">📚 How to Play</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-purple-300 mb-2">Discord Commands</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between items-center bg-black bg-opacity-30 rounded px-3 py-2">
                  <code className="text-purple-400">/start_game</code>
                  <span className="text-purple-200">Start a new battle</span>
                </div>
                <div className="flex justify-between items-center bg-black bg-opacity-30 rounded px-3 py-2">
                  <code className="text-purple-400">/game_stats</code>
                  <span className="text-purple-200">View your stats</span>
                </div>
                <div className="flex justify-between items-center bg-black bg-opacity-30 rounded px-3 py-2">
                  <code className="text-purple-400">/leaderboard</code>
                  <span className="text-purple-200">Top players</span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-purple-300 mb-2">Game Modes</h3>
              <div className="space-y-2 text-sm">
                <div className="bg-black bg-opacity-30 rounded px-3 py-2">
                  <span className="text-white font-medium">Solo:</span>
                  <span className="text-purple-200 ml-2">1v99 - Last one standing</span>
                </div>
                <div className="bg-black bg-opacity-30 rounded px-3 py-2">
                  <span className="text-white font-medium">Duo/Trio/Squad:</span>
                  <span className="text-purple-200 ml-2">Team up with friends</span>
                </div>
                <div className="bg-black bg-opacity-30 rounded px-3 py-2">
                  <span className="text-white font-medium">Quintuor:</span>
                  <span className="text-purple-200 ml-2">5-person teams</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 p-4 bg-gradient-to-r from-purple-500 from-opacity-20 to-blue-500 to-opacity-20 rounded-lg border border-purple-500 border-opacity-30">
            <p className="text-purple-200 text-sm">
              <strong>🎮 Join a game:</strong> React with 🎮 to any game announcement to join the battle! 
              Games start automatically when enough players join.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;