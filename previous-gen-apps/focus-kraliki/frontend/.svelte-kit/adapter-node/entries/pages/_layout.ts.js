import { d as derived, w as writable } from "../../chunks/index.js";
const locale = writable("en");
const translations = {
  en: {
    "nav.tasks": "Tasks",
    "nav.projects": "Projects",
    "nav.calendar": "Calendar",
    "task.priority.high": "High",
    "task.priority.medium": "Medium",
    "task.priority.low": "Low",
    "task.status.todo": "To Do",
    "task.status.in_progress": "In Progress",
    "task.status.done": "Done",
    "project.create": "Create Project"
  },
  cs: {
    "nav.tasks": "Úkoly",
    "nav.projects": "Projekty",
    "nav.calendar": "Kalendář",
    "task.priority.high": "Vysoká",
    "task.priority.medium": "Střední",
    "task.priority.low": "Nízká",
    "task.status.todo": "K vyřízení",
    "task.status.in_progress": "Probíhá",
    "task.status.done": "Hotovo",
    "project.create": "Vytvořit projekt"
  }
};
derived(locale, ($locale) => (key) => {
  return translations[$locale]?.[key] || key;
});
const load = async () => {
};
export {
  load
};
