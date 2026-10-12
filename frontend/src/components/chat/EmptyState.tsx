import React from 'react';
import { Sparkles, BookOpen, PenTool, LayoutTemplate, Layers } from 'lucide-react';

interface EmptyStateProps {
  onSelectPrompt: (prompt: string, skill?: string) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPrompt }) => {
  const starters = [
    {
      title: "Molly Graham's Legos Advice",
      desc: "How did giving away your Legos change with AI and rapid scaling?",
      prompt: "What did Molly Graham say about giving away your Legos in fast-growing tech companies and how AI changes this?",
      icon: <Layers size={16} color="#818cf8" />,
      skill: "knowledge_qa"
    },
    {
      title: "Core Retention Frameworks",
      desc: "How top PMs analyze retention curves and setup natural user loops.",
      prompt: "How do great product teams improve retention and build sustainable user habit loops?",
      icon: <BookOpen size={16} color="#38bdf8" />,
      skill: "knowledge_qa"
    },
    {
      title: "Ship 30 for 30 Essay on Scaling",
      desc: "A ~1,250-word editorial essay on leadership transitions & organizational friction.",
      prompt: "Write a 1,250-word Ship 30 for 30 essay on why product teams burn out during hypergrowth and how leaders solve it.",
      icon: <PenTool size={16} color="#f59e0b" />,
      skill: "ship30_writer"
    },
    {
      title: "Interactive Growth Audit Tool",
      desc: "Generate a standalone HTML/CSS deliverable for product scorecarding.",
      prompt: "Generate an interactive HTML/CSS Product-Market Fit and Retention Scorecard with an intuitive calculator.",
      icon: <LayoutTemplate size={16} color="#10b981" />,
      skill: "artifact_generator"
    }
  ];

  return (
    <div className="empty-state">
      <div className="empty-state-badge">
        <Sparkles size={13} />
        <span>Lenny's Podcast & Newsletter Knowledge Engine</span>
      </div>
      <h1 className="empty-state-title">The Lenny Growth Assistant</h1>
      <p className="empty-state-desc">
        Ask high-signal product management and startup growth questions grounded in 60+ verified transcripts. 
        Synthesize practitioner wisdom, inspect exact citations, and generate actionable deliverables.
      </p>

      <div className="starter-prompts">
        {starters.map((item, idx) => (
          <div 
            key={idx} 
            className="prompt-card"
            onClick={() => onSelectPrompt(item.prompt, item.skill)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {item.icon}
              <div className="prompt-card-title">{item.title}</div>
            </div>
            <div className="prompt-card-desc">{item.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
