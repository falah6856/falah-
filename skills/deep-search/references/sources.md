# كتالوج المصادر وعوامل البحث

## عوامل بحث Google (وتعمل أغلبها في Bing وBrave وWebSearch)
| العامل | مثال | الاستخدام |
|---|---|---|
| `"..."` | `"food delivery" "Saudi"` | عبارة حرفية |
| `site:` | `site:arxiv.org` · `site:github.com` · `site:.edu` · `site:.gov.sa` | حصر في موقع أو نطاق |
| `filetype:` | `filetype:pdf` · `filetype:xlsx` | تقارير ودراسات وبيانات |
| `intitle:` / `inurl:` | `intitle:"case study"` | العنوان أو الرابط |
| `-` | `-jobs -course` | استبعاد الضجيج |
| `OR` | `startup OR company` | بدائل |
| `before:` / `after:` | `after:2025-01-01` | نطاق زمني (Google) |
| `related:` (محدود) | — | مواقع شبيهة |

قوالب مفيدة:
- تقارير: `"<موضوع>" (report OR whitepaper OR survey) filetype:pdf`
- قوائم جاهزة: `"<موضوع>" (awesome OR "curated list") site:github.com`
- دراسات حالة: `"<موضوع>" intitle:"case study"`
- نقد: `"<موضوع>" (failure OR "post-mortem" OR criticism)`
- أرقام: `"<موضوع>" (statistics OR "market size" OR dataset)`

## خدمات Google المتخصصة
- **Google Scholar** (scholar.google.com): "Cited by" للتتبّع للأمام، "Related articles". بلا API رسمي.
- **Google Patents** (patents.google.com).
- **Google Dataset Search** (datasetsearch.research.google.com).
- **Google Trends**: لمقارنة الاهتمام عبر الزمن.

## أوراق علمية (APIs مفتوحة)
| المصدر | الحجم/الميزة | الرابط |
|---|---|---|
| OpenAlex | أكبر فهرس مفتوح (مئات الملايين من الأعمال)، استشهادات، مجاني | `api.openalex.org/works?search=` |
| Semantic Scholar | رسم استشهادات، "highly influential citations"، توصيات | `api.semanticscholar.org/graph/v1/paper/search` |
| arXiv | ما قبل النشر في الفيزياء والحاسب والرياضيات | `export.arxiv.org/api/query` |
| PubMed | الطب والأحياء | `eutils.ncbi.nlm.nih.gov` |
| Crossref | بيانات DOI لكل الناشرين | `api.crossref.org/works` |
| Unpaywall | نسخ مجانية قانونية من الأوراق المغلقة | `api.unpaywall.org` |

خوادم MCP جاهزة تجمعها (طرف ثالث، راجع الكود قبل الاعتماد): `academic-research-mcp` (9 مصادر)، `paper-search-mcp` (مع تنزيل PDF).

## الويب للوكلاء (خوادم MCP)
| الأداة | أقوى في |
|---|---|
| Exa | بحث دلالي بالمعنى؛ ناسب لاستعلامات HyDE |
| Brave Search | فهرس مستقل عن Google/Bing — مصدر "مستقل" لحساب الصيد وإعادة الصيد |
| Tavily | بحث + استخراج للوكلاء |
| Firecrawl | استخراج الصفحات الصعبة والزحف |
| Perplexity | إجابات مجمّعة بمصادر (لا تعدّها مصدرًا مستقلًا؛ هي تبحث في الويب نفسه) |

## مشاريع وشركات ومنتجات
- GitHub: `gh api -X GET search/repositories -f q='<موضوع> stars:>100' -f sort=stars`، ومستودعات `awesome-<موضوع>`.
- Y Combinator directory (ycombinator.com/companies)، Product Hunt، Crunchbase (مدفوع)، Hacker News (`hn.algolia.com`).
- قوائم التصنيف والجوائز في المجال، وتقارير الصناديق الاستثمارية.

## لماذا تعدد الطبقات مهم للقياس
تقدير الصيد وإعادة الصيد يحتاج طريقتين **مستقلتين قدر الإمكان**. محرك عام مقابل قاعدة أوراق، أو Google مقابل Brave، أفضل من صياغتين في المحرك نفسه.
