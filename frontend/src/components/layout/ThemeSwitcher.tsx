import React, { useState } from 'react';
import { Sparkles, Sun } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { THEME_OPTIONS } from '../../types/theme';

interface ThemeSwitcherProps {
  compact?: boolean;
}

export const ThemeSwitcher: React.FC<ThemeSwitcherProps> = ({ compact = false }) => {
  const { theme, setTheme, currentThemeOption, cycleTheme } = useTheme();
  const [hoveredThemeId, setHoveredThemeId] = useState<string | null>(null);

  const hoveredOption = hoveredThemeId 
    ? THEME_OPTIONS.find(t => t.id === hoveredThemeId) 
    : null;

  return (
    <div 
      className={`theme-toggle-bar ${compact ? 'compact' : ''}`} 
      role="region" 
      aria-label="Theme toggle"
    >
      {/* Tactile Hardware-Feel Quick Toggle Switch */}
      <button
        type="button"
        className="theme-quick-toggle"
        onClick={cycleTheme}
        title={`Click to toggle next atmosphere (Current: ${currentThemeOption.name})`}
        aria-label="Toggle next theme"
      >
        <span className="theme-toggle-switch-track" aria-hidden="true">
          <span 
            className={`theme-toggle-switch-thumb ${currentThemeOption.isLight ? 'light' : ''}`}
            style={{ background: currentThemeOption.gradient }}
          />
        </span>

        <span className="theme-quick-icon-wrap" aria-hidden="true">
          {currentThemeOption.isLight ? (
            <Sun size={12} className="theme-mode-icon sun" />
          ) : (
            <Sparkles size={12} className="theme-mode-icon sparkles" />
          )}
        </span>

        {!compact && (
          <span className="theme-quick-label">
            {currentThemeOption.name}
          </span>
        )}
      </button>

      {/* Subtle Divider */}
      <span className="theme-toggle-divider" aria-hidden="true" />

      {/* Segmented Switchable Rail */}
      <div 
        className="theme-segmented-rail" 
        role="radiogroup" 
        aria-label="Select gradient atmosphere"
      >
        {THEME_OPTIONS.map((t) => {
          const isActive = t.id === theme;
          return (
            <button
              key={t.id}
              type="button"
              role="radio"
              aria-checked={isActive}
              className={`theme-segmented-tab ${isActive ? 'active' : ''}`}
              onClick={() => setTheme(t.id)}
              onMouseEnter={() => setHoveredThemeId(t.id)}
              onMouseLeave={() => setHoveredThemeId(null)}
              title={`${t.name} — ${t.tagline}`}
              aria-label={`Switch theme to ${t.name}`}
            >
              <span
                className="theme-tab-swatch"
                style={{ background: t.gradient }}
              >
                {isActive && (
                  <span 
                    className="theme-tab-active-glow" 
                    style={{ background: t.gradient }} 
                  />
                )}
              </span>
            </button>
          );
        })}
      </div>

      {/* Bespoke Floating Micro-Tooltip */}
      {hoveredOption && (
        <div className="theme-toggle-tooltip" role="tooltip">
          <span className="theme-tooltip-name">{hoveredOption.name}</span>
          <span className="theme-tooltip-tagline">{hoveredOption.tagline}</span>
        </div>
      )}
    </div>
  );
};

export default ThemeSwitcher;
