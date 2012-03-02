i18n= {
  "be":
  {
  "OpenStreetMap Belarus": "OpenStreetMap Беларусь",
  "about": "пра праект",
  "Embed": "Убудова",
  "Embeddable map": "Экспарт карты для іншых сайтаў",
  "Crosshair": "Перакрыжаванне",
  "Marker": "Маркер",
  "Marker label": "Тэкст на маркеры",
  "Language": "Мова",
  "Copy this text into your page's HTML code": "Скапіруйце гэты тэкст у html-код вашай старонкі",
  "Map data © <a href='http://osm.org'>OpenStreetMap</a> contributors, CC-BY-SA; rendering by <a href='http://kosmosnimki.ru'>kosmosnimki.ru</a>": "Дадзеныя © Удзельнікі <a href='http://osm.org'>OpenStreetMap</a>, CC-BY-SA; візуальны стыль <a href='http://kosmosnimki.ru'>kosmosnimki.ru</a>",
  "Permalink": "Спасылка на гэтае месца",
  "Opening hours": "Калі працуюць",
  "atm": "банкамат",
  "ATM": "Ёсць банкамат",
  "bank": "банк",
  "pharmacy": "аптэка",
  "library": "бібліятэка",
  "university": "універсітэт",
  "cafe": "кафэ",
  "post office": "аддзяленне пошты",
  "restaurant": "рэстаран",
  "college": "каледж",
  "bar": "бар",
  "pub": "паб",
  "nightclub": "начны клуб",
  "hairdresser shop": "цырульня",
  "school": "школа",
  "kindergarten": "дзіцячы сад",
  "fuel": "запраўка",
  "boutique shop": "буцік",
  "photo shop": "фотакрама",
  "fast food": "перакус",
  "supermarket shop": "супермаркет",
  "bureau de change": "абмен валюты",
  "convenience shop": "крама",
  "cinema": "кінатэатр",
  "computer shop": "камп'ютэрная крама",
  "chemist shop": "бытавая хімія",
  "tourist shop": "крама для турыстаў",
  "telecommunication office": "тэлекамунікацыі",
  "company office": "офіс кампаніі",
  "books shop": "кнігарня",
  "optician shop": "оптыка",
  "pawnshop": "ламбард",
  "post box": "паштовая скрыня",
  "yes": "так",
  "no": "не",
  "Mo": "панядзелак",
  "Tu": "аўторак",
  "We": "серада",
  "Th": "чацвер",
  "Fr": "пятніца",
  "Sa": "субота",
  "Su": "нядзеля",
  "off (weekend)": "выхадны",
  "Download OpenStreetMap": "Сцягнуць OpenStreetMap",
  "download": "cцягнуць",
  "Project page": "Старонка праекта",
  "Offline world maps for all countries, including Belarus, based on the OpenStreetMap.":"Карты ўсіх краін свету, улiчвая Беларусь, якiм не патрэбны Iнтэрнэт.",
  "Put the whole World into your":"Выкарыстоўваюцца вельмі добра сціснутыя вектарныя дадзеныя, за кошт чаго ўвесь свет лёгка змяшчаецца ў",
  "iPhone, iPad or iPod":"iPhone, iPad або iPod",
  " due to greatly compressed vector map data":"",
  "Made in Belarus":"Зроблена ў Беларусі",
  "GpsMid is a free, fully offline, vector based map application for your mobile phone. It displays your current position on a zoomable map and can be used to search for and navigate to roads or points of interest of your liking. As all data is stored in a compact binary format on your phone you will incur no charges for extra data downloads.":"GpsMid - бясплатная вектарныя мапы для вашага мабільнага тэлефона з падтрымкай Java. Прысутнічае адлюстраванне вашага бягучага месцазнаходжання на мапе, пошук, навігацыя па дарогах краіны і патрэбныя вам пункты. Усе дадзеныя захоўваюцца ў кампактным двойкавым фармаце адразу на вашым тэлефоне, так што вам не прыйдзецца плаціць за інтэрнэт ці іншыя паслугі сувязі.",
  "Download Pre-Compiled Belarus": "Сцягнуць сабраныя мапы Беларусі",
  " floor":" паверх",
  "dormitory":"інтэрнат",
  "embassy":"амбасада",
  "kiosk shop":"кіёск",
  "toilets":"туалет",
  "car rental":"арэнда машын",
  "telephone":"тэлефон",
  "Other":"Іншы",
  "Route from here":"Пракласці маршрут адсюль",
  "Route to here":"Пракласці маршрут сюды",
  "Clear route":"Прыбраць маршрут",
  "Reverse route":"Адваротны маршрут",
  "Edit via ":"Правіць праз ",
  "Edit on OpenStreetMap.org":"Правіць на OpenStreetMap.org",
  "Route as bicycle":"Роварны маршрут",
  "Route as car":"Аўтамабільны маршрут",
  "Report a problem":"Паведаміць пра памылку тут",
  "Report a problem on map":"Паведамленне пра памылку на мапе",
  "Who are you?":"Хто вы?",
  "Describe what's wrong":"Што не так",
  "please zoom in":"калі ласка, павялічце мапу",
  "Send report":"Даслаць паведамленне",
  
  '':''
  //"shoes shop": "абуак",
  },
  "ru":
  {
    " w": "Скопируйте этот текст и вставьте в html-код вашей страницы:",
    "asssd": "Данные © Участники <a href='http://osm.org'>OpenStreetMap</a>, CC-BY-SA; визуальный стиль <a href='http://kosmonimki.ru'>kosmosnimki.ru</a>"
  }
  
}


function _(s) {
  if (typeof(s)=='undefined'){return s};
  if (typeof(i18n)!='undefined' && i18n[locale] && (s in i18n[locale])) {
    return i18n[locale][s];
  }
  if (typeof(i18n)!='undefined' && i18n[locale] && i18n[locale][s.substring(0, s.length-1)] && s.substring(s.length-1) == ":" ) {
    return i18n[locale][s.substring(0, s.length-1)]+":";
  }
  return s;
}


function refreshLocales(){
  $('s').html(function(a,b){return _(b)});
  $('a').html(function(a,b){return _(b)});
  $('label').html(function(a,b){return _(b)});
  $('button').html(function(a,b){return _(b)});
  $('a').attr("title", function(a,b){return _(b)})
}

refreshLocales();