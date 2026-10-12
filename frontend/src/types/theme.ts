export type ThemeId = 'obsidian' | 'cosmic' | 'emerald' | 'sunset' | 'amber' | 'ocean' | 'pearl';

export interface ThemeOption {
  id: ThemeId;
  name: string;
  tagline: string;
  gradient: string;
  previewColors: [string, string, string];
  isLight?: boolean;
}

export const THEME_OPTIONS: ThemeOption[] = [
  {
    id: 'obsidian',
    name: 'Obsidian Luxe',
    tagline: 'Carbon noir with brushed champagne gold & warm amber',
    gradient: 'linear-gradient(135deg, #b45309 0%, #eab308 45%, #fde047 80%, #fef9c3 100%)',
    previewColors: ['#b45309', '#eab308', '#fde047'],
  },
  {
    id: 'cosmic',
    name: 'Cosmic Aurora',
    tagline: 'Deep indigo velvet with violet aurora & subtle cyan',
    gradient: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #06b6d4 100%)',
    previewColors: ['#4f46e5', '#7c3aed', '#06b6d4'],
  },
  {
    id: 'emerald',
    name: 'Emerald Matrix',
    tagline: 'Obsidian black with alpine mint & deep teal accents',
    gradient: 'linear-gradient(135deg, #059669 0%, #10b981 50%, #14b8a6 100%)',
    previewColors: ['#059669', '#10b981', '#14b8a6'],
  },
  {
    id: 'sunset',
    name: 'Sunset Nebula',
    tagline: 'Velvet plum with warm rose & apricot embers',
    gradient: 'linear-gradient(135deg, #e11d48 0%, #ec4899 50%, #f97316 100%)',
    previewColors: ['#e11d48', '#ec4899', '#f97316'],
  },
  {
    id: 'amber',
    name: 'Solar Flare',
    tagline: 'Espresso bronze with molten honey & copper glow',
    gradient: 'linear-gradient(135deg, #d97706 0%, #ea580c 50%, #ef4444 100%)',
    previewColors: ['#d97706', '#ea580c', '#ef4444'],
  },
  {
    id: 'ocean',
    name: 'Oceanic Abyss',
    tagline: 'Midnight navy with arctic azure & cobalt light',
    gradient: 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 50%, #38bdf8 100%)',
    previewColors: ['#0284c7', '#0ea5e9', '#38bdf8'],
  },
  {
    id: 'pearl',
    name: 'Alabaster Frost',
    tagline: 'Frosted studio crystal with crisp lilac & silver (Light)',
    gradient: 'linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #38bdf8 100%)',
    previewColors: ['#6366f1', '#a855f7', '#38bdf8'],
    isLight: true,
  },
];
