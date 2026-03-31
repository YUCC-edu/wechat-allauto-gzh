/// <reference types="vite/client" />
import yaml from 'js-yaml';
import { ThemeConfig } from './WeChatHTMLConverter';

const themeFiles = import.meta.glob('../themes/**/*.yaml', { query: '?raw', import: 'default', eager: true });

export interface ThemeInfo {
  id: string;
  category: string;
  name: string;
  config: ThemeConfig;
}

export function loadAllThemes(): ThemeInfo[] {
  const themes: ThemeInfo[] = [];

  for (const [path, content] of Object.entries(themeFiles)) {
    if (path.includes('_template.yaml')) continue;

    const match = path.match(/\.\.\/themes\/([^/]+)\/([^/]+)\.yaml$/);
    if (!match) continue;

    const [, category, name] = match;
    const id = `${category}/${name}`;

    try {
      const parsed = yaml.load(content as string) as any;
      
      // Convert YAML format to internal format
      const config: ThemeConfig = {
        name: parsed.name || '未命名主题',
        description: parsed.description || '',
        keywords: parsed.keywords || [],
        category,
        ...parsed.styles,
        colors: parsed.colors,
      };

      themes.push({
        id,
        category,
        name: parsed.name || name,
        config,
      });
    } catch (e) {
      console.error(`Failed to load theme ${id}:`, e);
    }
  }

  return themes.sort((a, b) => a.id.localeCompare(b.id));
}
