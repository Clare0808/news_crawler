import articles from "../data/news.json";

// Frontend fixtures only. Replace this adapter with API calls when the backend is ready.
export function getNews() {
  return articles;
}

export const companies = [
  {
    id: "tsmc",
    name: "台積電",
    code: "2330",
    initials: "台",
    sector: "晶圓代工",
    color: "forest",
    description: "追蹤先進製程、晶片管制與半導體供應鏈消息。",
  },
  {
    id: "nvidia",
    name: "輝達",
    code: "NVDA",
    initials: "N",
    sector: "AI 運算",
    color: "lime",
    description: "整理 AI 算力、資料中心與晶片出口相關報導。",
  },
  {
    id: "mediatek",
    name: "聯發科",
    code: "2454",
    initials: "聯",
    sector: "IC 設計",
    color: "sand",
    description: "關注晶片設計、ASIC 與運算平台發展。",
  },
  {
    id: "asus",
    name: "華碩",
    code: "2357",
    initials: "華",
    sector: "電腦與伺服器",
    color: "blue",
    description: "聚焦 AI 伺服器、機櫃出貨與產品布局。",
  },
  {
    id: "ase",
    name: "日月光",
    code: "3711",
    initials: "日",
    sector: "封裝測試",
    color: "purple",
    description: "觀察先進封裝、測試產能與供應鏈投資。",
  },
  {
    id: "winbond",
    name: "華邦電",
    code: "2344",
    initials: "邦",
    sector: "記憶體",
    color: "rose",
    description: "整理記憶體需求、AI 應用與產業動態。",
  },
];

export const categories = [
  "全部新聞",
  "半導體",
  "AI 科技",
  "金融市場",
  "國際政經",
  "產業動態",
];
export const sources = ["中央社", "工商時報", "經濟日報", "財訊"];
export const sentimentLabels = {
  positive: "正面",
  neutral: "中性",
  negative: "負面",
};

export function companyById(id) {
  return companies.find((company) => company.id === id);
}

export function shortDate(value, withTime = false) {
  const date = new Date(value);
  return new Intl.DateTimeFormat("zh-TW", {
    timeZone: "Asia/Taipei",
    month: "2-digit",
    day: "2-digit",
    ...(withTime ? { hour: "2-digit", minute: "2-digit", hour12: false } : {}),
  }).format(date);
}

export function exportNews(items) {
  const cell = (value) => {
    let text = String(value ?? "");
    if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`;
    return `"${text.replaceAll('"', '""')}"`;
  };
  const rows = [
    [
      "標題",
      "來源",
      "發布時間",
      "分類",
      "情緒（示範）",
      "關鍵詞（示範）",
      "原文連結",
    ],
    ...items.map((item) => [
      item.title,
      item.source,
      item.publishedAt,
      item.category,
      sentimentLabels[item.sentiment],
      item.keywords.join("、"),
      item.url,
    ]),
  ];
  const url = URL.createObjectURL(
    new Blob(
      ["\uFEFF" + rows.map((row) => row.map(cell).join(",")).join("\r\n")],
      { type: "text/csv;charset=utf-8;" }
    )
  );
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "FinSight-新聞整理-示範資料.csv";
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
