import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Moon, Sun, Sparkles } from 'lucide-react';
import MessageBubble from './MessageBubble';
import { chatAPI } from '../services/api';
import type { Message } from '../services/api';
import './ChatInterface.css';

const ChatInterface: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [theme, setTheme] = useState<'dark' | 'light'>('dark');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);

    // Auto-scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Theme toggle
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    };

    // Welcome message
    useEffect(() => {
        const welcomeMessage: Message = {
            id: 'welcome',
            role: 'assistant',
            content: '👋 **Xin chào!** Tôi là Trợ lý AI về Luật Công nghệ Thông tin.\n\nTôi có thể giúp bạn tra cứu thông tin từ các văn bản pháp luật như:\n- Luật An ninh mạng\n- Luật An toàn thông tin mạng\n- Luật Chuyển giao công nghệ\n- Luật Công nghệ thông tin\n- Luật Khoa học công nghệ\n- Luật Trí tuệ nhân tạo\n\nBạn có câu hỏi gì không?',
            timestamp: new Date(),
        };
        setMessages([welcomeMessage]);
    }, []);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input.trim(),
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await chatAPI.sendMessage(input.trim());

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: response.answer,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: '❌ Xin lỗi, đã có lỗi xảy ra khi kết nối với server. Vui lòng thử lại sau.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
            inputRef.current?.focus();
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="chat-container">
            {/* Header */}
            <header className="chat-header glass">
                <div className="header-content">
                    <div className="header-left">
                        <div className="logo">
                            <Sparkles className="logo-icon" />
                        </div>
                        <div className="header-text">
                            <h1 className="header-title gradient-text">Trợ lý AI Luật</h1>
                            <p className="header-subtitle">Tư vấn pháp luật công nghệ thông tin</p>
                        </div>
                    </div>
                    <button
                        className="theme-toggle"
                        onClick={toggleTheme}
                        aria-label="Chuyển đổi chủ đề"
                    >
                        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                    </button>
                </div>
            </header>

            {/* Messages Area */}
            <main className="messages-area">
                <div className="messages-container">
                    {messages.map(message => (
                        <MessageBubble
                            key={message.id}
                            role={message.role}
                            content={message.content}
                            timestamp={message.timestamp}
                            sources={message.sources}
                        />
                    ))}

                    {/* Loading Indicator */}
                    {isLoading && (
                        <div className="loading-indicator fade-in">
                            <div className="avatar avatar-assistant">
                                <Bot size={20} />
                            </div>
                            <div className="typing-dots">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </main>

            {/* Input Area */}
            <footer className="input-area">
                <div className="input-container glass">
                    <textarea
                        ref={inputRef}
                        className="message-input"
                        placeholder="Nhập câu hỏi về luật công nghệ thông tin..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        rows={1}
                        disabled={isLoading}
                    />
                    <button
                        className="send-button"
                        onClick={handleSend}
                        disabled={!input.trim() || isLoading}
                        aria-label="Gửi tin nhắn"
                    >
                        {isLoading ? (
                            <Loader2 size={20} className="loading-spin" />
                        ) : (
                            <Send size={20} />
                        )}
                    </button>
                </div>
                <p className="input-hint">
                    Nhấn <kbd>Enter</kbd> để gửi, <kbd>Shift + Enter</kbd> để xuống dòng
                </p>
            </footer>
        </div>
    );
};

// Bot icon component
const Bot: React.FC<{ size: number }> = ({ size }) => (
    <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <rect x="3" y="11" width="18" height="10" rx="2" />
        <circle cx="12" cy="5" r="2" />
        <path d="M12 7v4" />
        <line x1="8" y1="16" x2="8" y2="16" />
        <line x1="16" y1="16" x2="16" y2="16" />
    </svg>
);

export default ChatInterface;
