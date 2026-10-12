import { useState } from 'react';
import { Copy, Check, FileCode, BookOpen } from 'lucide-react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import type { Message, Citation, Artifact } from '../../types';

interface MessageItemProps {
  message: Message;
  onSelectCitation: (citation: Citation) => void;
  onOpenArtifact: (artifact: Artifact) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({
  message,
  onSelectCitation,
  onOpenArtifact,
}) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getCleanHtml = (markdownText: string) => {
    const rawHtml = marked.parse(markdownText, { breaks: true, gfm: true }) as string;
    return DOMPurify.sanitize(rawHtml, {
      ALLOWED_TAGS: [
        'p', 'br', 'strong', 'em', 'u', 's', 'code', 'pre', 'blockquote',
        'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
      ],
      ALLOWED_ATTR: ['class']
    });
  };

  const skillLabels: Record<string, string> = {
    knowledge_qa: 'Knowledge Q&A',
    ship30_writer: 'Ship 30 for 30 Essay',
    artifact_generator: 'Artifact Deliverable',
  };

  return (
    <div className="message-wrapper">
      <div className={`message-avatar ${isUser ? 'user' : 'assistant'}`}>
        {isUser ? 'U' : 'L'}
      </div>

      <div className="message-body">
        <div className="message-header">
          <span className="message-sender">{isUser ? 'You' : 'Lenny Growth Assistant'}</span>
          {message.skill && skillLabels[message.skill] && (
            <span className="message-skill-tag">{skillLabels[message.skill]}</span>
          )}
        </div>

        <div 
          className="message-content"
          dangerouslySetInnerHTML={{ __html: getCleanHtml(message.content) }}
        />

        {message.artifact && (
          <button 
            className="view-artifact-btn"
            onClick={() => onOpenArtifact(message.artifact!)}
          >
            <FileCode size={14} />
            <span>Open Artifact: {message.artifact.title}</span>
          </button>
        )}

        {message.citations && message.citations.length > 0 && (
          <div className="citations-container">
            <div className="citations-label">Verified Transcript Sources</div>
            <div className="citations-chips">
              {message.citations.map((c, idx) => (
                <button 
                  key={c.chunk_id || idx} 
                  className="citation-chip"
                  onClick={() => onSelectCitation(c)}
                  title={`Excerpt from: ${c.doc_title}`}
                >
                  <BookOpen size={12} style={{ opacity: 0.7 }} />
                  <span className="badge">[{idx + 1}]</span>
                  <span>{c.guest ? `${c.guest}` : c.doc_title.slice(0, 24) + '...'}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {!isUser && (
          <div className="message-actions">
            <button className="action-btn" onClick={handleCopy}>
              {copied ? <Check size={12} color="#10b981" /> : <Copy size={12} />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
