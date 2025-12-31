import { derived, writable } from 'svelte/store';

export type Locale = 'en' | 'cs';

export const SUPPORTED_LOCALES: Locale[] = ['en', 'cs'];

export const locale = writable<Locale>('en');

type TranslationKey =
  | 'nav.tasks'
  | 'nav.projects'
  | 'nav.calendar'
  | 'task.priority.high'
  | 'task.priority.medium'
  | 'task.priority.low'
  | 'task.status.todo'
  | 'task.status.in_progress'
  | 'task.status.done'
  | 'project.create';

export const translations: Record<Locale, Record<TranslationKey, string>> = {
  en: {
    'nav.tasks': 'Tasks',
    'nav.projects': 'Projects',
    'nav.calendar': 'Calendar',
    'task.priority.high': 'High',
    'task.priority.medium': 'Medium',
    'task.priority.low': 'Low',
    'task.status.todo': 'To Do',
    'task.status.in_progress': 'In Progress',
    'task.status.done': 'Done',
    'project.create': 'Create Project'
  },
  cs: {
    'nav.tasks': 'Úkoly',
    'nav.projects': 'Projekty',
    'nav.calendar': 'Kalendář',
    'task.priority.high': 'Vysoká',
    'task.priority.medium': 'Střední',
    'task.priority.low': 'Nízká',
    'task.status.todo': 'K vyřízení',
    'task.status.in_progress': 'Probíhá',
    'task.status.done': 'Hotovo',
    'project.create': 'Vytvořit projekt'
  }
};

export const t = derived(locale, ($locale) => (key: string) => {
  return (translations[$locale] as Record<string, string>)?.[key] || key;
});

export function getLocaleName(loc: Locale): string {
  const names: Record<Locale, string> = {
    en: 'English',
    cs: 'Čeština'
  };
  return names[loc];
}
