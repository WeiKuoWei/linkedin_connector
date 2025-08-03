import React from 'react';
import { Auth } from '@supabase/auth-ui-react';
import { ThemeSupa } from '@supabase/auth-ui-shared';
import { supabase } from '../services/supabase';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              LinkedIn AI Weak Ties Chatbot
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Reconnect with your LinkedIn network using AI-powered insights. 
              Upload your connections, describe your mission, and get personalized 
              suggestions for reaching out to the right people.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-start">
            
            {/* Features Section */}
            <div className="space-y-8">
              <h2 className="text-3xl font-semibold text-gray-900 mb-6">
                How It Works
              </h2>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                    1
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Upload Your LinkedIn Connections
                    </h3>
                    <p className="text-gray-600">
                      Export your LinkedIn connections as a CSV file and upload them securely. 
                      We'll enrich each profile with detailed information.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                    2
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Describe Your Mission
                    </h3>
                    <p className="text-gray-600">
                      Tell us what you're looking for - whether it's partnerships, 
                      job opportunities, investment, or expertise in a specific area.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                    3
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Get AI-Powered Suggestions
                    </h3>
                    <p className="text-gray-600">
                      Our AI analyzes your network and recommends the most relevant 
                      connections, along with personalized outreach messages.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                    4
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Send Personalized Messages
                    </h3>
                    <p className="text-gray-600">
                      Copy the AI-generated messages and reach out to your connections 
                      with confidence and context.
                    </p>
                  </div>
                </div>
              </div>

              {/* Key Features */}
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  ✨ Key Features
                </h3>
                <ul className="space-y-2 text-gray-600">
                  <li>🔒 <strong>Secure & Private:</strong> Your data is encrypted and isolated</li>
                  <li>🤖 <strong>AI-Powered:</strong> Smart matching and message generation</li>
                  <li>🎯 <strong>Semantic Search:</strong> Find relevant connections by context</li>
                  <li>📝 <strong>Custom Messages:</strong> Personalized outreach for each contact</li>
                </ul>
              </div>
            </div>

            {/* Login Section */}
            <div className="bg-white p-8 rounded-lg shadow-lg border">
              <div className="mb-6">
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  Sign In to Get Started
                </h2>
                <p className="text-gray-600">
                  Create an account or sign in to start analyzing your LinkedIn network.
                </p>
              </div>

              <Auth
                supabaseClient={supabase}
                appearance={{
                  theme: ThemeSupa,
                  variables: {
                    default: {
                      colors: {
                        brand: '#3b82f6',
                        brandAccent: '#2563eb',
                      },
                    },
                  },
                }}
                providers={['google', 'github']}
                redirectTo={window.location.origin}
                onlyThirdPartyProviders={false}
                magicLink={true}
                view="sign_in"
              />

              <div className="mt-6 text-xs text-gray-500 text-center">
                By signing in, you agree to our Terms of Service and Privacy Policy. 
                Your LinkedIn data is processed securely and never shared.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;