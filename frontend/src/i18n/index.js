import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import en from './locales/en.json';
import hi from './locales/hi.json';
import kn from './locales/kn.json';
import ta from './locales/ta.json';
import te from './locales/te.json';
import mr from './locales/mr.json';
import bn from './locales/bn.json';
import gu from './locales/gu.json';
import ml from './locales/ml.json';
import or_ from './locales/or.json';
import pa from './locales/pa.json';
import as_ from './locales/as.json';
import ur from './locales/ur.json';
import sd from './locales/sd.json';
import ne from './locales/ne.json';
import sa from './locales/sa.json';
import kok from './locales/kok.json';
import mai from './locales/mai.json';
import doi from './locales/doi.json';
import mni from './locales/mni.json';
import sat from './locales/sat.json';
import bodo from './locales/bodo.json';
import ks from './locales/ks.json';

const savedLang = typeof window !== 'undefined' ? localStorage.getItem('pcai_language') || 'en' : 'en';

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    hi: { translation: hi },
    kn: { translation: kn },
    ta: { translation: ta },
    te: { translation: te },
    mr: { translation: mr },
    bn: { translation: bn },
    gu: { translation: gu },
    ml: { translation: ml },
    or: { translation: or_ },
    pa: { translation: pa },
    as: { translation: as_ },
    ur: { translation: ur },
    sd: { translation: sd },
    ne: { translation: ne },
    sa: { translation: sa },
    kok: { translation: kok },
    mai: { translation: mai },
    doi: { translation: doi },
    mni: { translation: mni },
    sat: { translation: sat },
    bodo: { translation: bodo },
    ks: { translation: ks },
  },
  lng: savedLang,
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

export const LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English', priority: 0 },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', priority: 1 },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', priority: 1 },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', priority: 1 },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', priority: 1 },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', priority: 1 },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', priority: 2 },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', priority: 2 },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', priority: 2 },
  { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ', priority: 2 },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', priority: 2 },
  { code: 'as', name: 'Assamese', nativeName: 'অসমীয়া', priority: 2 },
  { code: 'ur', name: 'Urdu', nativeName: 'اردو', priority: 2 },
  { code: 'sd', name: 'Sindhi', nativeName: 'سنڌي', priority: 3 },
  { code: 'ne', name: 'Nepali', nativeName: 'नेपाली', priority: 3 },
  { code: 'sa', name: 'Sanskrit', nativeName: 'संस्कृतम्', priority: 3 },
  { code: 'kok', name: 'Konkani', nativeName: 'कोंकणी', priority: 3 },
  { code: 'mai', name: 'Maithili', nativeName: 'मैथिली', priority: 3 },
  { code: 'doi', name: 'Dogri', nativeName: 'डोगरी', priority: 3 },
  { code: 'mni', name: 'Manipuri', nativeName: 'মৈতৈলোন্', priority: 3 },
  { code: 'sat', name: 'Santali', nativeName: 'ᱥᱟᱱᱛᱟᱲᱤ', priority: 3 },
  { code: 'bodo', name: 'Bodo', nativeName: 'बड़ो', priority: 3 },
  { code: 'ks', name: 'Kashmiri', nativeName: 'कॉशुर', priority: 3 },
];

export default i18n;
