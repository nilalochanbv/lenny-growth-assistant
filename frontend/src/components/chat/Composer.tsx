import { useState, useRef, useEffect } from 'react';
import { ArrowUp, Loader2 } from 'lucide-react';
import type { ModelInfo } from '../../types';

interface ComposerProps {
  onSendMessage: (message: string, skill?: string) => void;
  isLoading: boolean;
  activeProvider?: string;
  selectedModel: string;
  availableModels: ModelInfo[];
  onSelectModel: (modelId: string, provider: 'local' | 'cloud') => void;
}

export const Composer: React.FC<ComposerProps> = ({
  onSendMessage,
  isLoading,
  selectedModel,
  availableModels,
  onSelectModel,
}) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [text]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (!text.trim() || isLoading) return;
    onSendMessage(text.trim());
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  return (
    <div className="composer-area">
      <div className="composer-box">
        <textarea
          ref={textareaRef}
          className="composer-textarea"
          placeholder="Ask a product or growth question grounded in Lenny's archive..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          rows={1}
        />

        <div className="composer-footer">
          <div className="composer-controls">
            <select
              className="model-select-compact"
              value={selectedModel}
              onChange={(e) => {
                const modelId = e.target.value;
                const m = availableModels.find(x => x.id === modelId);
                if (m) {
                  onSelectModel(m.id, m.provider);
                }
              }}
              disabled={isLoading}
            >
              {availableModels.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          </div>

          <button
            className="send-btn"
            onClick={handleSubmit}
            disabled={!text.trim() || isLoading}
            title="Send message (Enter)"
          >
            {isLoading ? <Loader2 size={16} className="animate-spin" /> : <ArrowUp size={16} />}
          </button>
        </div>
      </div>
    </div>
  );
};
