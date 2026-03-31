import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Sun, Moon, Monitor, Globe, Bell, BellOff, Check } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useTranslation } from 'react-i18next';
import { LANGUAGES } from '../i18n';

const Settings = () => {
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme();
  const { t, i18n } = useTranslation();
  const [notifications, setNotifications] = useState(true);
  const [showAllLangs, setShowAllLangs] = useState(false);

  const themes = [
    { key: 'dark', icon: Moon, label: t('settings.dark_mode'), desc: t('settings.dark_desc') },
    { key: 'light', icon: Sun, label: t('settings.light_mode'), desc: t('settings.light_desc') },
    { key: 'system', icon: Monitor, label: t('settings.system_mode'), desc: t('settings.system_desc') },
  ];

  const handleLangChange = (code) => {
    i18n.changeLanguage(code);
    localStorage.setItem('pcai_language', code);
  };

  const priorityLangs = LANGUAGES.filter(l => l.priority <= 1);
  const otherLangs = LANGUAGES.filter(l => l.priority > 1);
  const displayLangs = showAllLangs ? LANGUAGES : priorityLangs;

  return (
    <div className="min-h-screen bg-background">
      <div className="glass-header sticky top-0 z-50 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="p-2 rounded-lg hover:bg-secondary transition-colors" data-testid="settings-back-btn">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-xl font-semibold font-sans">{t('settings.title')}</h1>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-6 space-y-8">
        {/* Appearance */}
        <section className="glass-card" data-testid="settings-appearance">
          <h2 className="text-lg font-semibold mb-4 font-sans flex items-center gap-2">
            <Sun className="w-5 h-5 text-primary" />
            {t('settings.appearance')}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {themes.map(({ key, icon: Icon, label, desc }) => (
              <button
                key={key}
                onClick={() => setTheme(key)}
                data-testid={`theme-${key}-btn`}
                className={`relative p-4 rounded-lg border text-left transition-all ${
                  theme === key
                    ? 'border-primary bg-primary/10 ring-2 ring-primary/30'
                    : 'border-border hover:border-primary/40'
                }`}
              >
                {theme === key && <Check className="absolute top-2 right-2 w-4 h-4 text-primary" />}
                <Icon className="w-6 h-6 mb-2 text-primary" />
                <p className="font-medium text-sm">{label}</p>
                <p className="text-xs text-muted-foreground mt-1">{desc}</p>
              </button>
            ))}
          </div>
        </section>

        {/* Language */}
        <section className="glass-card" data-testid="settings-language">
          <h2 className="text-lg font-semibold mb-4 font-sans flex items-center gap-2">
            <Globe className="w-5 h-5 text-primary" />
            {t('settings.language')}
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            {displayLangs.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLangChange(lang.code)}
                data-testid={`lang-${lang.code}-btn`}
                className={`p-3 rounded-lg border text-left transition-all ${
                  i18n.language === lang.code
                    ? 'border-primary bg-primary/10 ring-1 ring-primary/30'
                    : 'border-border hover:border-primary/40'
                }`}
              >
                <p className="font-medium text-sm">{lang.nativeName}</p>
                <p className="text-xs text-muted-foreground">{lang.name}</p>
              </button>
            ))}
          </div>
          {!showAllLangs && otherLangs.length > 0 && (
            <button
              onClick={() => setShowAllLangs(true)}
              data-testid="show-all-langs-btn"
              className="mt-3 text-sm text-primary hover:underline"
            >
              + {otherLangs.length} more languages
            </button>
          )}
        </section>

        {/* Notifications */}
        <section className="glass-card" data-testid="settings-notifications">
          <h2 className="text-lg font-semibold mb-4 font-sans flex items-center gap-2">
            <Bell className="w-5 h-5 text-primary" />
            {t('settings.notifications')}
          </h2>
          <div className="flex items-center justify-between p-3 rounded-lg border border-border">
            <div>
              <p className="font-medium text-sm">Record Alert Notifications</p>
              <p className="text-xs text-muted-foreground">Get notified when government record updates are detected</p>
            </div>
            <button
              onClick={() => setNotifications(!notifications)}
              data-testid="notifications-toggle-btn"
              className={`p-2 rounded-lg transition-colors ${notifications ? 'bg-primary/20 text-primary' : 'bg-secondary text-muted-foreground'}`}
            >
              {notifications ? <Bell className="w-5 h-5" /> : <BellOff className="w-5 h-5" />}
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Settings;
