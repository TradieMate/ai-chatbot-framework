# React Widget Integration Guide

This guide shows how to integrate the AI Chatbot Framework with your React application using the REST API.

## 1. Install Required Dependencies

```bash
npm install axios uuid
```

## 2. Create Chatbot Hook

Create a custom React hook for chatbot functionality:

```typescript
// hooks/useChatbot.ts
import { useState, useCallback } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

interface ChatMessage {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
}

interface ChatbotResponse {
  text: string;
  context?: any;
}

export const useChatbot = (apiBaseUrl: string = 'http://localhost:8080') => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [threadId] = useState(() => uuidv4());
  const [context, setContext] = useState({});

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: uuidv4(),
      text,
      isBot: false,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post<ChatbotResponse>(
        `${apiBaseUrl}/bots/channels/rest/webbook`,
        {
          thread_id: threadId,
          text,
          context,
        }
      );

      // Add bot response
      const botMessage: ChatMessage = {
        id: uuidv4(),
        text: response.data.text,
        isBot: true,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
      
      // Update context if provided
      if (response.data.context) {
        setContext(response.data.context);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: uuidv4(),
        text: 'Sorry, I encountered an error. Please try again.',
        isBot: true,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [apiBaseUrl, threadId, context]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setContext({});
  }, []);

  return {
    messages,
    sendMessage,
    clearChat,
    isLoading,
    threadId,
  };
};
```

## 3. Create Chatbot Widget Component

```typescript
// components/ChatbotWidget.tsx
import React, { useState, useRef, useEffect } from 'react';
import { useChatbot } from '../hooks/useChatbot';

interface ChatbotWidgetProps {
  apiBaseUrl?: string;
  title?: string;
  placeholder?: string;
  className?: string;
}

export const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({
  apiBaseUrl = 'http://localhost:8080',
  title = 'AI Assistant',
  placeholder = 'Type your message...',
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { messages, sendMessage, clearChat, isLoading } = useChatbot(apiBaseUrl);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      await sendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className={`fixed bottom-4 right-4 z-50 ${className}`}>
      {/* Chat Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-colors"
          aria-label="Open chat"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="bg-white rounded-lg shadow-xl w-80 h-96 flex flex-col">
          {/* Header */}
          <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
            <h3 className="font-semibold">{title}</h3>
            <div className="flex gap-2">
              <button
                onClick={clearChat}
                className="text-blue-200 hover:text-white transition-colors"
                aria-label="Clear chat"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-blue-200 hover:text-white transition-colors"
                aria-label="Close chat"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && (
              <div className="text-gray-500 text-center text-sm">
                Start a conversation with the AI assistant!
              </div>
            )}
            
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}
              >
                <div
                  className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                    message.isBot
                      ? 'bg-gray-200 text-gray-800'
                      : 'bg-blue-600 text-white'
                  }`}
                >
                  {message.text}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 text-gray-800 px-3 py-2 rounded-lg text-sm">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="p-4 border-t">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={placeholder}
                disabled={isLoading}
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2 text-sm transition-colors"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
```

## 4. Usage in Your React App

```typescript
// App.tsx
import React from 'react';
import { ChatbotWidget } from './components/ChatbotWidget';

function App() {
  return (
    <div className="App">
      {/* Your existing app content */}
      <h1>My React App</h1>
      
      {/* Chatbot Widget */}
      <ChatbotWidget
        apiBaseUrl="http://localhost:8080"
        title="Customer Support"
        placeholder="How can I help you today?"
      />
    </div>
  );
}

export default App;
```

## 5. Environment Configuration

Create a `.env` file in your React app:

```env
REACT_APP_CHATBOT_API_URL=http://localhost:8080
```

Then use it in your component:

```typescript
<ChatbotWidget
  apiBaseUrl={process.env.REACT_APP_CHATBOT_API_URL}
/>
```

## 6. CORS Configuration

Make sure your chatbot backend allows CORS requests from your React app domain. The framework already includes CORS middleware that allows all origins, but for production, you should restrict it to your specific domain.

## 7. Production Considerations

1. **API URL**: Update the API URL to your production chatbot server
2. **Authentication**: Add authentication if needed
3. **Error Handling**: Implement proper error handling and retry logic
4. **Styling**: Customize the widget styling to match your app's design
5. **Analytics**: Add analytics tracking for chat interactions
6. **Rate Limiting**: Implement rate limiting on the client side

## 8. Advanced Features

You can extend the widget with additional features:

- File upload support
- Rich message types (buttons, cards, etc.)
- Typing indicators
- Message timestamps
- User authentication
- Chat history persistence
- Offline support