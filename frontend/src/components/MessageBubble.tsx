import React from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot, Copy, Check } from 'lucide-react';
import './MessageBubble.css';

interface MessageBubbleProps {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    sources?: string[];
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ role, content, timestamp, sources }) => {
    const [copied, setCopied] = React.useState(false);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const formatTime = (date: Date) => {
        return new Intl.DateTimeFormat('vi-VN', {
            hour: '2-digit',
            minute: '2-digit',
        }).format(date);
    };

    const isUser = role === 'user';

    return (
        <div className={`message-wrapper ${isUser ? 'user-message' : 'assistant-message'} fade-in`}>
            <div className="message-container">
                {/* Avatar */}
                <div className={`avatar ${isUser ? 'avatar-user' : 'avatar-assistant'}`}>
                    {isUser ? <User size={20} /> : <Bot size={20} />}
                </div>

                {/* Message Content */}
                <div className="message-content">
                    <div className="message-header">
                        <span className="message-role">{isUser ? 'Bạn' : 'Trợ lý AI Luật'}</span>
                        <span className="message-time">{formatTime(timestamp)}</span>
                    </div>

                    <div className={`message-bubble ${isUser ? 'bubble-user' : 'bubble-assistant'}`}>
                        {isUser ? (
                            <p className="message-text">{content}</p>
                        ) : (
                            <div className="markdown-content">
                                <ReactMarkdown>{content}</ReactMarkdown>
                            </div>
                        )}

                        {/* Copy Button for Assistant Messages */}
                        {!isUser && (
                            <button
                                className="copy-button"
                                onClick={handleCopy}
                                aria-label="Sao chép"
                            >
                                {copied ? <Check size={16} /> : <Copy size={16} />}
                            </button>
                        )}
                    </div>

                    {/* Sources Display */}
                    {sources && sources.length > 0 && (
                        <div className="sources-container">
                            <p className="sources-label">📚 Nguồn tham khảo:</p>
                            <div className="sources-list">
                                {sources.map((source, idx) => (
                                    <span key={idx} className="source-tag">
                                        {source}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MessageBubble;
