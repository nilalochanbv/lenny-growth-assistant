import React, { createContext, useContext, useEffect, useState, useMemo } from 'react';
import type { ThemeId, ThemeOption } from '../types/theme';
import { THEME_OPTIONS } from '../types/theme';

interface ThemeContextType {
  theme: ThemeId;
  setTheme: (theme: ThemeId) => void;
  currentThemeOption: ThemeOption;
  cycleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const STORAGE_KEY = 'lenny_active_theme';

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<ThemeId>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY) as ThemeId | null;
      if (stored && THEME_OPTIONS.some(t => t.id === stored)) {
        return stored;
      }
    } catch {
      // Ignore localStorage read errors
    }
    return 'obsidian';
  });

  const setTheme = (newTheme: ThemeId) => {
    setThemeState(newTheme);
    try {
      localStorage.setItem(STORAGE_KEY, newTheme);
    } catch {
      // Ignore localStorage write errors
    }
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const currentThemeOption = useMemo(() => {
    return THEME_OPTIONS.find(t => t.id === theme) || THEME_OPTIONS[0];
  }, [theme]);

  const cycleTheme = () => {
    const currentIndex = THEME_OPTIONS.findIndex(t => t.id === theme);
    const nextIndex = (currentIndex + 1) % THEME_OPTIONS.length;
    setTheme(THEME_OPTIONS[nextIndex].id);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, currentThemeOption, cycleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
