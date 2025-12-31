/**
 * Speak by Kraliki - Internationalization (i18n)
 *
 * Phase 1: Czech (cs) and English (en) - COMPLETE
 * Phase 2: Polish (pl), Slovak (sk), Spanish (es) - After Launch
 */

import { derived, writable } from 'svelte/store';

export type Locale = 'cs' | 'en';

export const SUPPORTED_LOCALES: Locale[] = ['cs', 'en'];

// Default locale from browser or Czech
function getDefaultLocale(): Locale {
  if (typeof window !== 'undefined') {
    const browserLang = navigator.language.slice(0, 2);
    if (browserLang === 'en') return 'en';
  }
  return 'cs'; // Default to Czech for CEE market
}

export const locale = writable<Locale>(getDefaultLocale());

// Translation keys organized by section
type TranslationKey =
  // Common
  | 'common.loading'
  | 'common.save'
  | 'common.cancel'
  | 'common.delete'
  | 'common.edit'
  | 'common.create'
  | 'common.back'
  | 'common.next'
  | 'common.submit'
  | 'common.search'
  | 'common.filter'
  | 'common.all'
  | 'common.none'
  | 'common.yes'
  | 'common.no'
  | 'common.error'
  | 'common.success'
  // Nav
  | 'nav.dashboard'
  | 'nav.surveys'
  | 'nav.alerts'
  | 'nav.actions'
  | 'nav.employees'
  | 'nav.settings'
  | 'nav.logout'
  // Landing
  | 'landing.title'
  | 'landing.subtitle'
  | 'landing.description'
  | 'landing.login'
  | 'landing.register'
  | 'landing.feature1.title'
  | 'landing.feature1.desc'
  | 'landing.feature2.title'
  | 'landing.feature2.desc'
  | 'landing.feature3.title'
  | 'landing.feature3.desc'
  // Auth
  | 'auth.login'
  | 'auth.register'
  | 'auth.email'
  | 'auth.password'
  | 'auth.confirmPassword'
  | 'auth.firstName'
  | 'auth.lastName'
  | 'auth.companyName'
  | 'auth.forgotPassword'
  | 'auth.noAccount'
  | 'auth.hasAccount'
  | 'auth.invalidCredentials'
  | 'auth.loginDescription'
  | 'auth.registerDescription'
  | 'auth.loggingIn'
  | 'auth.creatingAccount'
  | 'auth.minPassword'
  // Dashboard
  | 'dashboard.title'
  | 'dashboard.newCampaign'
  | 'dashboard.sentiment'
  | 'dashboard.participation'
  | 'dashboard.activeAlerts'
  | 'dashboard.pendingActions'
  | 'dashboard.topics'
  | 'dashboard.noTopics'
  | 'dashboard.alerts'
  | 'dashboard.viewAll'
  | 'dashboard.noAlerts'
  | 'dashboard.actionLoop'
  | 'dashboard.manage'
  | 'dashboard.noActions'
  | 'dashboard.responses'
  // Sentiment
  | 'sentiment.positive'
  | 'sentiment.negative'
  | 'sentiment.neutral'
  // Status
  | 'status.new'
  | 'status.heard'
  | 'status.inProgress'
  | 'status.resolved'
  | 'status.draft'
  | 'status.scheduled'
  | 'status.active'
  | 'status.paused'
  | 'status.completed'
  // Surveys
  | 'surveys.title'
  | 'surveys.create'
  | 'surveys.name'
  | 'surveys.description'
  | 'surveys.frequency'
  | 'surveys.once'
  | 'surveys.weekly'
  | 'surveys.monthly'
  | 'surveys.quarterly'
  | 'surveys.questions'
  | 'surveys.addQuestion'
  | 'surveys.launch'
  | 'surveys.pause'
  | 'surveys.stats'
  | 'surveys.noSurveys'
  // Alerts
  | 'alerts.title'
  | 'alerts.unread'
  | 'alerts.markRead'
  | 'alerts.createAction'
  | 'alerts.severity.low'
  | 'alerts.severity.medium'
  | 'alerts.severity.high'
  | 'alerts.noAlerts'
  // Actions
  | 'actions.title'
  | 'actions.create'
  | 'actions.topic'
  | 'actions.priority'
  | 'actions.publicMessage'
  | 'actions.visibleToEmployees'
  | 'actions.markHeard'
  | 'actions.markInProgress'
  | 'actions.markResolved'
  | 'actions.noActions'
  // Employees
  | 'employees.title'
  | 'employees.add'
  | 'employees.import'
  | 'employees.firstName'
  | 'employees.lastName'
  | 'employees.email'
  | 'employees.department'
  | 'employees.jobTitle'
  | 'employees.active'
  | 'employees.optedOut'
  | 'employees.noEmployees'
  // Voice Interface
  | 'voice.title'
  | 'voice.consent.title'
  | 'voice.consent.intro'
  | 'voice.consent.anonymous'
  | 'voice.consent.managerNoSee'
  | 'voice.consent.aggregated'
  | 'voice.consent.reviewTranscript'
  | 'voice.consent.deleteData'
  | 'voice.consent.duration'
  | 'voice.consent.accept'
  | 'voice.consent.skip'
  | 'voice.mode.voice'
  | 'voice.mode.text'
  | 'voice.switchToText'
  | 'voice.end'
  | 'voice.thinking'
  | 'voice.speakNow'
  | 'voice.switchHint'
  | 'voice.send'
  | 'voice.placeholder'
  | 'voice.completed.title'
  | 'voice.completed.message'
  | 'voice.completed.viewTranscript'
  | 'voice.error'
  | 'voice.invalidLink'
  // Transcript
  | 'transcript.title'
  | 'transcript.redact'
  | 'transcript.redactSelected'
  | 'transcript.deleteAll'
  | 'transcript.confirmDelete'
  // Action Loop Widget
  | 'actionLoop.title'
  | 'actionLoop.weAreListening'
  | 'actionLoop.weAreWorking'
  | 'actionLoop.resolved'
  // Settings
  | 'settings.profile'
  | 'settings.company'
  | 'settings.preferences'
  | 'settings.language';

export const translations: Record<Locale, Record<TranslationKey, string>> = {
  cs: {
    // Common
    'common.loading': 'Nacitam...',
    'common.save': 'Ulozit',
    'common.cancel': 'Zrusit',
    'common.delete': 'Smazat',
    'common.edit': 'Upravit',
    'common.create': 'Vytvorit',
    'common.back': 'Zpet',
    'common.next': 'Dalsi',
    'common.submit': 'Odeslat',
    'common.search': 'Hledat',
    'common.filter': 'Filtr',
    'common.all': 'Vse',
    'common.none': 'Zadne',
    'common.yes': 'Ano',
    'common.no': 'Ne',
    'common.error': 'Chyba',
    'common.success': 'Uspech',
    // Nav
    'nav.dashboard': 'Dashboard',
    'nav.surveys': 'Kampane',
    'nav.alerts': 'Alerty',
    'nav.actions': 'Akce',
    'nav.employees': 'Zamestnanci',
    'nav.settings': 'Nastaveni',
    'nav.logout': 'Odhlasit',
    // Landing
    'landing.title': 'SPEAK BY KRALIKI',
    'landing.subtitle': 'AI Voice Employee Intelligence Platform',
    'landing.description': 'Zjistete, co si vasi zamestnanci opravdu mysli. Hlasove rozhovory. Anonymni zpetna vazba. Akcni vhledy.',
    'landing.login': 'Prihlasit se',
    'landing.register': 'Zalozit ucet',
    'landing.feature1.title': 'HLAS MISTO TEXTU',
    'landing.feature1.desc': 'Zamestnanci mluvi prirozene. AI nasloucha a pta se dal.',
    'landing.feature2.title': '100% ANONYMNI',
    'landing.feature2.desc': 'Zadny manazer nevidi jednotlive odpovedi. Pouze trendy.',
    'landing.feature3.title': 'AKCE & FEEDBACK',
    'landing.feature3.desc': 'Ukazte zamestnancum, ze naslouchate. Uzavirate smycku.',
    // Auth
    'auth.login': 'Prihlasit se',
    'auth.register': 'Registrovat',
    'auth.email': 'E-mail',
    'auth.password': 'Heslo',
    'auth.confirmPassword': 'Potvrdit heslo',
    'auth.firstName': 'Jmeno',
    'auth.lastName': 'Prijmeni',
    'auth.companyName': 'Nazev firmy',
    'auth.forgotPassword': 'Zapomenute heslo?',
    'auth.noAccount': 'Nemate ucet?',
    'auth.hasAccount': 'Mate ucet?',
    'auth.invalidCredentials': 'Neplatne prihlasovaci udaje',
    'auth.loginDescription': 'Pristup do dashboardu Speak by Kraliki',
    'auth.registerDescription': 'Zalozit ucet pro vasi firmu',
    'auth.loggingIn': 'Prihlasuji...',
    'auth.creatingAccount': 'Vytvarim ucet...',
    'auth.minPassword': 'Min. 8 znaku',
    // Dashboard
    'dashboard.title': 'Dashboard',
    'dashboard.newCampaign': 'Nova kampan',
    'dashboard.sentiment': 'Sentiment',
    'dashboard.participation': 'Participace',
    'dashboard.activeAlerts': 'Aktivni alerty',
    'dashboard.pendingActions': 'Cekajici akce',
    'dashboard.topics': 'Temata',
    'dashboard.noTopics': 'Zatim zadna temata',
    'dashboard.alerts': 'Alerty',
    'dashboard.viewAll': 'Vsechny',
    'dashboard.noAlerts': 'Zadne nove alerty',
    'dashboard.actionLoop': 'Akce (Action Loop)',
    'dashboard.manage': 'Spravovat',
    'dashboard.noActions': 'Zadne akce. Vytvorte akci z alertu pro uzavreni feedback smycky.',
    'dashboard.responses': 'odpovedi',
    // Sentiment
    'sentiment.positive': 'Pozitivni',
    'sentiment.negative': 'Negativni',
    'sentiment.neutral': 'Neutralni',
    // Status
    'status.new': 'Novy',
    'status.heard': 'Slysime',
    'status.inProgress': 'Resime',
    'status.resolved': 'Vyreseno',
    'status.draft': 'Koncept',
    'status.scheduled': 'Naplanovano',
    'status.active': 'Aktivni',
    'status.paused': 'Pozastaveno',
    'status.completed': 'Dokonceno',
    // Surveys
    'surveys.title': 'Kampane',
    'surveys.create': 'Nova kampan',
    'surveys.name': 'Nazev',
    'surveys.description': 'Popis',
    'surveys.frequency': 'Frekvence',
    'surveys.once': 'Jednorazove',
    'surveys.weekly': 'Tyden',
    'surveys.monthly': 'Mesic',
    'surveys.quarterly': 'Ctvrtletne',
    'surveys.questions': 'Otazky',
    'surveys.addQuestion': 'Pridat otazku',
    'surveys.launch': 'Spustit',
    'surveys.pause': 'Pozastavit',
    'surveys.stats': 'Statistiky',
    'surveys.noSurveys': 'Zatim zadne kampane',
    // Alerts
    'alerts.title': 'Alerty',
    'alerts.unread': 'Neprectene',
    'alerts.markRead': 'Oznacit jako prectene',
    'alerts.createAction': 'Vytvorit akci',
    'alerts.severity.low': 'Nizka',
    'alerts.severity.medium': 'Stredni',
    'alerts.severity.high': 'Vysoka',
    'alerts.noAlerts': 'Zadne alerty',
    // Actions
    'actions.title': 'Akce',
    'actions.create': 'Nova akce',
    'actions.topic': 'Tema',
    'actions.priority': 'Priorita',
    'actions.publicMessage': 'Verejna zprava',
    'actions.visibleToEmployees': 'Viditelne pro zamestnance',
    'actions.markHeard': 'Oznacit: Slysime',
    'actions.markInProgress': 'Oznacit: Resime',
    'actions.markResolved': 'Oznacit: Vyreseno',
    'actions.noActions': 'Zatim zadne akce',
    // Employees
    'employees.title': 'Zamestnanci',
    'employees.add': 'Pridat zamestnance',
    'employees.import': 'Importovat CSV',
    'employees.firstName': 'Jmeno',
    'employees.lastName': 'Prijmeni',
    'employees.email': 'E-mail',
    'employees.department': 'Oddeleni',
    'employees.jobTitle': 'Pozice',
    'employees.active': 'Aktivni',
    'employees.optedOut': 'Odhlaseni',
    'employees.noEmployees': 'Zatim zadni zamestnanci',
    // Voice Interface
    'voice.title': 'Speak by Kraliki - Check-in',
    'voice.consent.title': 'PULSE BY KRALIKI',
    'voice.consent.intro': 'Ahoj! Toto je tvuj mesicni prostor pro zpetnou vazbu.',
    'voice.consent.anonymous': 'Rozhovor je 100% ANONYMNI',
    'voice.consent.managerNoSee': 'Tvuj nadrizeny NEUVIDI co jsi rekl/a',
    'voice.consent.aggregated': 'Vedeni vidi pouze agregovane trendy',
    'voice.consent.reviewTranscript': 'Po rozhovoru si muzes precist a upravit prepis',
    'voice.consent.deleteData': 'Muzes kdykoliv pozadat o smazani svych dat',
    'voice.consent.duration': 'Rozhovor trva cca 5 minut.',
    'voice.consent.accept': 'Rozumim, pojdme na to',
    'voice.consent.skip': 'Nechci odpovidat: Preskocit tento mesic',
    'voice.mode.voice': 'Hlasovy rezim',
    'voice.mode.text': 'Textovy rezim',
    'voice.switchToText': 'Prejit na text',
    'voice.end': 'Ukoncit',
    'voice.thinking': 'Premyslim...',
    'voice.speakNow': 'Mluv do mikrofonu...',
    'voice.switchHint': 'Nebo prepni na textovy rezim vyse',
    'voice.send': 'Odeslat',
    'voice.placeholder': 'Napis svou odpoved...',
    'voice.completed.title': 'Dekujeme!',
    'voice.completed.message': 'Tvoje zpetna vazba byla zaznamenana. Vazime si tveho casu.',
    'voice.completed.viewTranscript': 'Zobrazit prepis',
    'voice.error': 'Chyba',
    'voice.invalidLink': 'Neplatny nebo vyprsely odkaz',
    // Transcript
    'transcript.title': 'Prepis rozhovoru',
    'transcript.redact': 'Upravit/Smazat',
    'transcript.redactSelected': 'Smazat vybrane',
    'transcript.deleteAll': 'Smazat vsechna data',
    'transcript.confirmDelete': 'Opravdu chcete smazat vsechna data?',
    // Action Loop Widget
    'actionLoop.title': 'Co delame s vasi zpetnou vazbou',
    'actionLoop.weAreListening': 'Slysime vas',
    'actionLoop.weAreWorking': 'Pracujeme na tom',
    'actionLoop.resolved': 'Vyreseno',
    // Settings
    'settings.profile': 'Profil',
    'settings.company': 'Firma',
    'settings.preferences': 'Preference',
    'settings.language': 'Jazyk',
  },
  en: {
    // Common
    'common.loading': 'Loading...',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.delete': 'Delete',
    'common.edit': 'Edit',
    'common.create': 'Create',
    'common.back': 'Back',
    'common.next': 'Next',
    'common.submit': 'Submit',
    'common.search': 'Search',
    'common.filter': 'Filter',
    'common.all': 'All',
    'common.none': 'None',
    'common.yes': 'Yes',
    'common.no': 'No',
    'common.error': 'Error',
    'common.success': 'Success',
    // Nav
    'nav.dashboard': 'Dashboard',
    'nav.surveys': 'Campaigns',
    'nav.alerts': 'Alerts',
    'nav.actions': 'Actions',
    'nav.employees': 'Employees',
    'nav.settings': 'Settings',
    'nav.logout': 'Logout',
    // Landing
    'landing.title': 'SPEAK BY KRALIKI',
    'landing.subtitle': 'AI Voice Employee Intelligence Platform',
    'landing.description': 'Discover what your employees really think. Voice conversations. Anonymous feedback. Actionable insights.',
    'landing.login': 'Sign In',
    'landing.register': 'Create Account',
    'landing.feature1.title': 'VOICE NOT TEXT',
    'landing.feature1.desc': 'Employees speak naturally. AI listens and follows up.',
    'landing.feature2.title': '100% ANONYMOUS',
    'landing.feature2.desc': 'No manager sees individual responses. Only trends.',
    'landing.feature3.title': 'ACTION & FEEDBACK',
    'landing.feature3.desc': 'Show employees you listen. Close the loop.',
    // Auth
    'auth.login': 'Sign In',
    'auth.register': 'Register',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.confirmPassword': 'Confirm Password',
    'auth.firstName': 'First Name',
    'auth.lastName': 'Last Name',
    'auth.companyName': 'Company Name',
    'auth.forgotPassword': 'Forgot password?',
    'auth.noAccount': "Don't have an account?",
    'auth.hasAccount': 'Already have an account?',
    'auth.invalidCredentials': 'Invalid credentials',
    'auth.loginDescription': 'Access your Speak by Kraliki dashboard',
    'auth.registerDescription': 'Create an account for your company',
    'auth.loggingIn': 'Signing in...',
    'auth.creatingAccount': 'Creating account...',
    'auth.minPassword': 'Min. 8 characters',
    // Dashboard
    'dashboard.title': 'Dashboard',
    'dashboard.newCampaign': 'New Campaign',
    'dashboard.sentiment': 'Sentiment',
    'dashboard.participation': 'Participation',
    'dashboard.activeAlerts': 'Active Alerts',
    'dashboard.pendingActions': 'Pending Actions',
    'dashboard.topics': 'Topics',
    'dashboard.noTopics': 'No topics yet',
    'dashboard.alerts': 'Alerts',
    'dashboard.viewAll': 'View All',
    'dashboard.noAlerts': 'No new alerts',
    'dashboard.actionLoop': 'Actions (Action Loop)',
    'dashboard.manage': 'Manage',
    'dashboard.noActions': 'No actions. Create an action from an alert to close the feedback loop.',
    'dashboard.responses': 'responses',
    // Sentiment
    'sentiment.positive': 'Positive',
    'sentiment.negative': 'Negative',
    'sentiment.neutral': 'Neutral',
    // Status
    'status.new': 'New',
    'status.heard': 'Heard',
    'status.inProgress': 'In Progress',
    'status.resolved': 'Resolved',
    'status.draft': 'Draft',
    'status.scheduled': 'Scheduled',
    'status.active': 'Active',
    'status.paused': 'Paused',
    'status.completed': 'Completed',
    // Surveys
    'surveys.title': 'Campaigns',
    'surveys.create': 'New Campaign',
    'surveys.name': 'Name',
    'surveys.description': 'Description',
    'surveys.frequency': 'Frequency',
    'surveys.once': 'Once',
    'surveys.weekly': 'Weekly',
    'surveys.monthly': 'Monthly',
    'surveys.quarterly': 'Quarterly',
    'surveys.questions': 'Questions',
    'surveys.addQuestion': 'Add Question',
    'surveys.launch': 'Launch',
    'surveys.pause': 'Pause',
    'surveys.stats': 'Statistics',
    'surveys.noSurveys': 'No campaigns yet',
    // Alerts
    'alerts.title': 'Alerts',
    'alerts.unread': 'Unread',
    'alerts.markRead': 'Mark as Read',
    'alerts.createAction': 'Create Action',
    'alerts.severity.low': 'Low',
    'alerts.severity.medium': 'Medium',
    'alerts.severity.high': 'High',
    'alerts.noAlerts': 'No alerts',
    // Actions
    'actions.title': 'Actions',
    'actions.create': 'New Action',
    'actions.topic': 'Topic',
    'actions.priority': 'Priority',
    'actions.publicMessage': 'Public Message',
    'actions.visibleToEmployees': 'Visible to Employees',
    'actions.markHeard': 'Mark: Heard',
    'actions.markInProgress': 'Mark: In Progress',
    'actions.markResolved': 'Mark: Resolved',
    'actions.noActions': 'No actions yet',
    // Employees
    'employees.title': 'Employees',
    'employees.add': 'Add Employee',
    'employees.import': 'Import CSV',
    'employees.firstName': 'First Name',
    'employees.lastName': 'Last Name',
    'employees.email': 'Email',
    'employees.department': 'Department',
    'employees.jobTitle': 'Job Title',
    'employees.active': 'Active',
    'employees.optedOut': 'Opted Out',
    'employees.noEmployees': 'No employees yet',
    // Voice Interface
    'voice.title': 'Speak by Kraliki - Check-in',
    'voice.consent.title': 'PULSE BY KRALIKI',
    'voice.consent.intro': 'Hi! This is your monthly feedback space.',
    'voice.consent.anonymous': 'This conversation is 100% ANONYMOUS',
    'voice.consent.managerNoSee': 'Your manager will NOT see what you said',
    'voice.consent.aggregated': 'Leadership only sees aggregated trends',
    'voice.consent.reviewTranscript': 'You can review and edit the transcript after',
    'voice.consent.deleteData': 'You can request data deletion anytime',
    'voice.consent.duration': 'The conversation takes about 5 minutes.',
    'voice.consent.accept': 'I understand, let\'s go',
    'voice.consent.skip': 'I don\'t want to respond: Skip this month',
    'voice.mode.voice': 'Voice Mode',
    'voice.mode.text': 'Text Mode',
    'voice.switchToText': 'Switch to Text',
    'voice.end': 'End',
    'voice.thinking': 'Thinking...',
    'voice.speakNow': 'Speak into the microphone...',
    'voice.switchHint': 'Or switch to text mode above',
    'voice.send': 'Send',
    'voice.placeholder': 'Type your response...',
    'voice.completed.title': 'Thank You!',
    'voice.completed.message': 'Your feedback has been recorded. We appreciate your time.',
    'voice.completed.viewTranscript': 'View Transcript',
    'voice.error': 'Error',
    'voice.invalidLink': 'Invalid or expired link',
    // Transcript
    'transcript.title': 'Conversation Transcript',
    'transcript.redact': 'Edit/Delete',
    'transcript.redactSelected': 'Delete Selected',
    'transcript.deleteAll': 'Delete All Data',
    'transcript.confirmDelete': 'Are you sure you want to delete all data?',
    // Action Loop Widget
    'actionLoop.title': 'What we\'re doing with your feedback',
    'actionLoop.weAreListening': 'We hear you',
    'actionLoop.weAreWorking': 'We\'re working on it',
    'actionLoop.resolved': 'Resolved',
    // Settings
    'settings.profile': 'Profile',
    'settings.company': 'Company',
    'settings.preferences': 'Preferences',
    'settings.language': 'Language',
  },
};

// Derived store for translation function
export const t = derived(locale, ($locale) => (key: string) => {
  return (translations[$locale] as Record<string, string>)?.[key] || key;
});

// Helper to get locale name
export function getLocaleName(loc: Locale): string {
  const names: Record<Locale, string> = {
    cs: 'Cestina',
    en: 'English',
  };
  return names[loc];
}

// Helper to set locale and persist
export function setLocale(loc: Locale): void {
  locale.set(loc);
  if (typeof window !== 'undefined') {
    localStorage.setItem('vop-locale', loc);
  }
}

// Initialize locale from storage
export function initLocale(): void {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('vop-locale') as Locale | null;
    if (stored && SUPPORTED_LOCALES.includes(stored)) {
      locale.set(stored);
    }
  }
}
