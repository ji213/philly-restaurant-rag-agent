import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Search, Loader2, MapPin, Utensils, Star, ExternalLink } from 'lucide-react';

export default function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          postal_code: null, // Global semantic search as requested
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
      setError('Could not connect to the recommendation backend. Make sure your FastAPI server is running!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-orange-500 selection:text-white">
      {/* Header */}
      <header className="w-full py-6 px-8 border-b border-slate-800/60 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-orange-600 p-2 rounded-xl text-white font-bold">
            <Utensils className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">Philly Restaurant Agent</h1>
            <p className="text-xs text-slate-400">AI-powered food recommendations across Philadelphia</p>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-12 flex flex-col items-center">
        {!result && !loading && (
          <div className="text-center my-auto space-y-4 max-w-lg">
            <h2 className="text-4xl font-extrabold tracking-tight text-white">
              Where should we eat in Philly?
            </h2>
            <p className="text-slate-400 text-sm">
              Ask for anything—cozy date night spots, authentic cheesesteaks, late-night bites, or specific cuisines.
            </p>
          </div>
        )}

        {/* Search Input Bar */}
        <div className={`w-full transition-all duration-300 ${result || loading ? 'mb-8' : 'my-auto'}`}>
          <form onSubmit={handleSearch} className="relative flex items-center shadow-2xl rounded-2xl">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Best romantic Italian restaurants in Center City..."
              className="w-full bg-slate-900 border border-slate-700/80 rounded-2xl py-4 pl-5 pr-14 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm md:text-base shadow-inner"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="absolute right-3 bg-orange-600 hover:bg-orange-500 disabled:bg-slate-800 disabled:text-slate-600 text-white p-2.5 rounded-xl transition-colors flex items-center justify-center"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="w-full bg-red-950/50 border border-red-800/60 text-red-300 p-4 rounded-xl text-center text-sm mb-6">
            {error}
          </div>
        )}

        {/* Loading State Animation */}
        {loading && (
          <div className="flex flex-col items-center justify-center space-y-3 py-16">
            <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
            <p className="text-sm text-slate-400 animate-pulse">Searching reviews and crafting your dining guide...</p>
          </div>
        )}

        {/* Results View */}
        {result && !loading && (
          <div className="w-full space-y-10 animate-fade-in">
            {/* AI Recommendation Synthesis */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 md:p-8 shadow-xl">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-orange-400 mb-4">AI Recommendation</h3>
              <div className="prose prose-invert max-w-none text-slate-300 text-sm md:text-base leading-relaxed space-y-4">
                <ReactMarkdown>{result.recommendation}</ReactMarkdown>
              </div>
            </div>

            {/* Restaurant Cards Grid */}
            {result.restaurants && result.restaurants.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">Matching Spots</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {result.restaurants.map((restaurant, index) => (
                    <div 
                      key={index}
                      className="bg-slate-900/50 border border-slate-800/80 hover:border-slate-700 rounded-2xl p-5 flex flex-col justify-between transition-all"
                    >
                      <div>
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-bold text-base text-white">{restaurant.name || 'Restaurant'}</h4>
                          {restaurant.rating && (
                            <span className="flex items-center space-x-1 bg-amber-500/10 text-amber-400 text-xs px-2 py-1 rounded-lg border border-amber-500/20">
                              <Star className="w-3.5 h-3.5 fill-amber-400" />
                              <span>{restaurant.rating}</span>
                            </span>
                          )}
                        </div>
                        {restaurant.address && (
                          <p className="flex items-center text-xs text-slate-400 mb-3">
                            <MapPin className="w-3.5 h-3.5 mr-1 text-slate-500 flex-shrink-0" />
                            {restaurant.address}
                          </p>
                        )}
                        {restaurant.categories && (
                          <div className="flex flex-wrap gap-1.5 mb-4">
                            {restaurant.categories.map((cat, catIdx) => (
                              <span key={catIdx} className="bg-slate-800 text-slate-300 text-[10px] px-2 py-0.5 rounded-md">
                                {cat}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full py-4 text-center text-xs text-slate-600 border-t border-slate-900">
        Philly Restaurant RAG Agent • Powered by FastAPI, Pinecone & OpenAI
      </footer>
    </div>
  );
}