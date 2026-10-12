import React from 'react';
import { X, ExternalLink, BookOpen, User, Calendar, Award } from 'lucide-react';
import type { Citation } from '../../types';

interface EvidenceModalProps {
  citation: Citation | null;
  onClose: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BookOpen size={16} color="#818cf8" />
            <h3 className="modal-title">Transcript Evidence Source</h3>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          <div className="evidence-card">
            <h4 className="evidence-title">{citation.doc_title}</h4>
            <div className="evidence-meta">
              {citation.guest && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <User size={12} /> {citation.guest}
                </span>
              )}
              {citation.date && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Calendar size={12} /> {citation.date}
                </span>
              )}
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#10b981' }}>
                <Award size={12} /> Score: {Math.round(citation.score * 100)}%
              </span>
            </div>

            <div className="evidence-text">
              {citation.excerpt}
            </div>

            <div style={{ marginTop: '8px' }}>
              <a 
                href={citation.doc_url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="evidence-link"
              >
                <span>Read Full Original Episode on Lenny's Newsletter</span>
                <ExternalLink size={12} />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
