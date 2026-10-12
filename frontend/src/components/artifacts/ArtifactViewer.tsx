import React, { useState } from 'react';
import { X, Copy, Download, Check, Eye, Code2 } from 'lucide-react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import type { Artifact } from '../../types';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({ artifact, onClose }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const isHtml = artifact.format === 'html';

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const extension = isHtml ? 'html' : 'md';
    const mimeType = isHtml ? 'text/html' : 'text/markdown';
    const blob = new Blob([artifact.content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.toLowerCase().replace(/\s+/g, '_')}.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Safe markdown preview using marked + DOMPurify
  const getRenderedMarkdown = () => {
    const raw = marked.parse(artifact.content, { breaks: true, gfm: true }) as string;
    return DOMPurify.sanitize(raw);
  };

  // Isolated HTML sandbox:
  // Using iframe srcDoc with sandbox="allow-scripts" but NO "allow-same-origin"
  // This rigorously blocks access to parent cookies, local storage, and application DOM!
  const getSafeHtmlSrcDoc = () => {
    return `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${artifact.title}</title>
        <style>
          body {
            margin: 0;
            padding: 24px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #0b1120;
            color: #f8fafc;
            line-height: 1.6;
          }
          * { box-sizing: border-box; }
        </style>
      </head>
      <body>
        ${artifact.content}
      </body>
      </html>
    `;
  };

  return (
    <aside className="artifact-panel">
      <div className="artifact-panel-header">
        <div className="artifact-title-group">
          <span className={`artifact-tag ${isHtml ? 'html' : 'markdown'}`}>
            {artifact.format}
          </span>
          <div className="artifact-title" title={artifact.title}>
            {artifact.title}
          </div>
        </div>

        <div className="artifact-panel-actions">
          <div className="tab-toggle">
            <button 
              className={`tab-btn ${activeTab === 'preview' ? 'active' : ''}`}
              onClick={() => setActiveTab('preview')}
            >
              <Eye size={13} style={{ marginRight: '4px', verticalAlign: '-1px' }} />
              Preview
            </button>
            <button 
              className={`tab-btn ${activeTab === 'code' ? 'active' : ''}`}
              onClick={() => setActiveTab('code')}
            >
              <Code2 size={13} style={{ marginRight: '4px', verticalAlign: '-1px' }} />
              Source
            </button>
          </div>

          <button className="icon-action-btn" onClick={handleCopy} title="Copy code">
            {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
          </button>

          <button className="icon-action-btn" onClick={handleDownload} title="Download file">
            <Download size={14} />
          </button>

          <button className="icon-action-btn" onClick={onClose} title="Close panel">
            <X size={14} />
          </button>
        </div>
      </div>

      <div className="artifact-panel-content">
        {activeTab === 'preview' ? (
          isHtml ? (
            <div className="artifact-preview-container">
              <iframe
                title={artifact.title}
                className="artifact-iframe"
                sandbox="allow-scripts"
                srcDoc={getSafeHtmlSrcDoc()}
              />
            </div>
          ) : (
            <div 
              className="artifact-markdown-view"
              dangerouslySetInnerHTML={{ __html: getRenderedMarkdown() }}
            />
          )
        ) : (
          <div className="artifact-code-view">
            <code>{artifact.content}</code>
          </div>
        )}
      </div>
    </aside>
  );
};
