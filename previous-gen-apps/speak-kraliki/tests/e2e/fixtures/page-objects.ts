import { Page, Locator } from '@playwright/test';

/**
 * Page Object for Landing Page
 * Speak by Kraliki landing page with login/register CTAs
 * Default locale is Czech (cs)
 */
export class LandingPage {
  readonly page: Page;
  readonly heroTitle: Locator;
  readonly heroSubtitle: Locator;
  readonly loginButton: Locator;
  readonly registerButton: Locator;
  readonly featureCards: Locator;
  readonly navLinks: Locator;
  readonly footer: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heroTitle = page.locator('h1');
    this.heroSubtitle = page.locator('.hero-subtitle, [data-testid="hero-subtitle"]');
    // Czech: "PRIHLASIT SE" / English: "SIGN IN"
    this.loginButton = page.getByRole('button', { name: /prihlasit|sign in|login/i });
    // Czech: "ZALOZIT UCET" / English: "CREATE ACCOUNT"
    this.registerButton = page.getByRole('button', { name: /zalozit|create|register/i });
    this.featureCards = page.locator('[data-testid="feature-card"], .feature-card');
    this.navLinks = page.locator('nav a, header a');
    this.footer = page.locator('footer');
  }

  async goto() {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  async clickLogin() {
    await this.loginButton.click();
    await this.page.waitForURL(/login/, { timeout: 15000 });
  }

  async clickRegister() {
    await this.registerButton.click();
    await this.page.waitForURL(/register/, { timeout: 15000 });
  }
}

/**
 * Page Object for Login Page
 * Handles authentication forms
 */
export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly registerLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel(/email/i);
    this.passwordInput = page.getByLabel(/password|heslo/i);
    this.submitButton = page.getByRole('button', { name: /login|sign in|prihlasit/i });
    this.errorMessage = page.locator('[data-testid="error-message"], .error-message, [role="alert"]');
    this.registerLink = page.getByRole('link', { name: /register|create|zalozit/i });
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

/**
 * Page Object for Register Page
 * Handles user registration
 */
export class RegisterPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly companyNameInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly loginLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel(/email/i);
    this.passwordInput = page.getByLabel(/^password|^heslo/i);
    this.confirmPasswordInput = page.getByLabel(/confirm|opakuj/i);
    this.companyNameInput = page.getByLabel(/company|firma|spolecnost/i);
    this.submitButton = page.getByRole('button', { name: /register|sign up|create|zalozit/i });
    this.errorMessage = page.locator('[data-testid="error-message"], .error-message, [role="alert"]');
    this.loginLink = page.getByRole('link', { name: /login|sign in|prihlasit/i });
  }

  async goto() {
    await this.page.goto('/register');
  }

  async register(email: string, password: string, companyName?: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    if (this.confirmPasswordInput) {
      await this.confirmPasswordInput.fill(password).catch(() => {});
    }
    if (companyName && this.companyNameInput) {
      await this.companyNameInput.fill(companyName).catch(() => {});
    }
    await this.submitButton.click();
  }
}

/**
 * Page Object for Dashboard
 * CEO/Manager dashboard for survey management
 */
export class DashboardPage {
  readonly page: Page;
  readonly surveysLink: Locator;
  readonly actionsLink: Locator;
  readonly employeesLink: Locator;
  readonly alertsLink: Locator;
  readonly analyticsLink: Locator;
  readonly createSurveyButton: Locator;
  readonly userMenu: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.surveysLink = page.getByRole('link', { name: /survey|pruzkum/i });
    this.actionsLink = page.getByRole('link', { name: /action|akce/i });
    this.employeesLink = page.getByRole('link', { name: /employee|zamestnanec/i });
    this.alertsLink = page.getByRole('link', { name: /alert|upozorneni/i });
    this.analyticsLink = page.getByRole('link', { name: /analytic|analyza/i });
    this.createSurveyButton = page.getByRole('button', { name: /create|vytvorit|new|novy/i });
    this.userMenu = page.locator('[data-testid="user-menu"], .user-menu');
    this.logoutButton = page.getByRole('button', { name: /logout|odhlasit/i });
  }

  async goto() {
    await this.page.goto('/dashboard');
  }

  async goToSurveys() {
    await this.page.goto('/dashboard/surveys');
  }

  async goToActions() {
    await this.page.goto('/dashboard/actions');
  }

  async goToEmployees() {
    await this.page.goto('/dashboard/employees');
  }

  async goToAlerts() {
    await this.page.goto('/dashboard/alerts');
  }

  async goToAnalytics() {
    await this.page.goto('/dashboard/analytics');
  }
}

/**
 * Page Object for Employee Voice Feedback
 * Magic link flow for anonymous employee feedback
 */
export class EmployeeVoicePage {
  readonly page: Page;
  readonly consentScreen: Locator;
  readonly startButton: Locator;
  readonly skipButton: Locator;
  readonly voiceRecorder: Locator;
  readonly textModeButton: Locator;
  readonly textInput: Locator;
  readonly submitButton: Locator;
  readonly thankYouMessage: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    // Czech: "ANONYMNI" / English: "anonymous"
    this.consentScreen = page.locator('[data-testid="consent-screen"], .consent-screen');
    // Czech: "POJDME NA TO" / English: "START"
    this.startButton = page.getByRole('button', { name: /pojdme|start|begin|rozumim|ok/i });
    // Czech: "Preskocit" / English: "Skip"
    this.skipButton = page.getByRole('button', { name: /preskocit|skip|nechci/i });
    this.voiceRecorder = page.locator('[data-testid="voice-recorder"], .voice-recorder');
    // Czech: "PREJIT NA TEXT" / English: "Switch to text"
    this.textModeButton = page.getByRole('button', { name: /prejit|text|write|psat/i });
    this.textInput = page.locator('textarea, [data-testid="feedback-input"]');
    this.submitButton = page.getByRole('button', { name: /submit|send|odeslat|poslat/i });
    this.thankYouMessage = page.locator('[data-testid="thank-you"], .thank-you');
    this.errorMessage = page.locator('[data-testid="error"], .error-message, [role="alert"]');
  }

  async gotoWithToken(token: string) {
    await this.page.goto(`/v/${token}`);
  }

  async startConversation() {
    await this.startButton.click();
  }

  async skipFeedback() {
    await this.skipButton.click();
  }

  async switchToTextMode() {
    await this.textModeButton.click();
  }

  async submitTextFeedback(text: string) {
    await this.textInput.fill(text);
    await this.submitButton.click();
  }
}

/**
 * Page Object for Survey Creation Modal
 */
export class SurveyCreationModal {
  readonly page: Page;
  readonly modal: Locator;
  readonly nameInput: Locator;
  readonly descriptionInput: Locator;
  readonly frequencySelect: Locator;
  readonly addQuestionButton: Locator;
  readonly questionInputs: Locator;
  readonly saveButton: Locator;
  readonly cancelButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.modal = page.locator('[data-testid="survey-modal"], .survey-modal, [role="dialog"]');
    this.nameInput = page.getByLabel(/name|nazev/i);
    this.descriptionInput = page.getByLabel(/description|popis/i);
    this.frequencySelect = page.getByLabel(/frequency|frekvence/i);
    this.addQuestionButton = page.getByRole('button', { name: /add question|pridat otazku/i });
    this.questionInputs = page.locator('[data-testid="question-input"], .question-input');
    this.saveButton = page.getByRole('button', { name: /save|create|ulozit|vytvorit/i });
    this.cancelButton = page.getByRole('button', { name: /cancel|zrusit/i });
  }

  async fillSurvey(name: string, description: string, frequency?: string) {
    await this.nameInput.fill(name);
    await this.descriptionInput.fill(description);
    if (frequency) {
      await this.frequencySelect.selectOption(frequency);
    }
  }

  async addQuestion(questionText: string) {
    await this.addQuestionButton.click();
    const lastQuestion = this.questionInputs.last();
    await lastQuestion.fill(questionText);
  }

  async save() {
    await this.saveButton.click();
  }

  async cancel() {
    await this.cancelButton.click();
  }
}
