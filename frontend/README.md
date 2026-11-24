# FinSight 財經觀測前端

Vue 3、Vue Router 與 Vite 製作的期末專題前端，目前不需後端即可執行。

## 本機啟動

在此 `frontend` 目錄執行，使用 Node.js 22.18+ 或 24.12+；本次以 Node.js 26 驗證。

```powershell
npm ci
npm run dev
```

開啟 http://127.0.0.1:5173/ 。只監聽本機，未部署。

```powershell
npm run build
npm run preview
```

`build` 產物位於 `dist/`。正式靜態主機之後需設定 SPA fallback，讓 `/news` 等路徑回傳 `index.html`。

## 頁面與互動

- `/`：新聞總覽、樣本統計、情緒分布、熱門關鍵詞。
- `/news`：文字搜尋、主題／來源／情緒／日期篩選、排序與分頁。
- `/companies`：公司選擇與相關新聞。
- `/insights`：示範情緒與關鍵詞統計。
- `/saved`：收藏新聞；儲存於目前瀏覽器的 `localStorage`。
- 新聞詳情：重點整理、原始內文、NLP 分析示例及原文連結。
- 其他前端互動：深淺色模式、手機選單、CSV 匯出、空結果提示。

可用 `/` 快捷鍵聚焦上方搜尋欄，輸入後按 Enter。詳情視窗支援 Escape 關閉；閱讀分頁支援左右方向鍵、Home 與 End。

## 展示資料

`src/data/news.json` 含 24 篇取自上層 `result/*.csv` 的新聞樣本，四個來源各 6 篇，發布日期為 2026/11/17–11/21。

標題、連結與內文來自既有 CSV，未對新聞事實或目前網站可用性進行查證。展示版只做基本雜訊清除，沒有變更原始 CSV；財訊來源名稱在展示資料中修正為「財訊」。

公司關聯、分類、關鍵詞與情緒為前端展示配置，重點句為既有文字片段。所有圖表依這 24 篇樣本及其示範標籤計算，並非整批 3,884 篇資料的分析結果。未執行 NLP 模型、雲端 API、爬蟲或股價預測。

## 程式位置與後續銜接

| 路徑 | 用途 |
| --- | --- |
| `src/App.vue` | 頂部導覽與搜尋、手機選單、說明與詳情視窗 |
| `src/styles.css` | 配色、元件樣式、深淺主題與 RWD |
| `src/views/` | 各頁面版型與篩選呈現 |
| `src/components/` | 導覽、圖示、新聞卡片、詳情與圖表 |
| `src/services/newsService.js` | 展示資料入口、公司資料、日期格式與匯出 |
| `src/composables/useWorkspace.js` | 收藏、選取文章與提示訊息狀態 |
| `src/data/news.json` | 靜態展示樣本 |

目前 `getNews()` 同步回傳展示資料。後續接 API 時，優先修改 `newsService.js`，並將 `useWorkspace.js` 的文章改為非同步載入的 reactive 狀態，再補 loading 與 error 處理；不要把 API 請求散落在每張卡片。

主要文章格式：

```js
{
  id: 'stable-id',
  title: '新聞標題',
  source: '中央社',
  url: 'https://example.com/article',
  publishedAt: '2026-11-21T18:08:00+08:00',
  category: '金融市場',
  content: '既有內文',
  excerpt: '列表文字',
  contentType: 'article', // 截斷內容使用 excerpt
  companyIds: ['tsmc'],
  keywords: ['關鍵詞'],
  sentiment: 'neutral', // positive | neutral | negative
  summary: ['重點句'],
  analysisMode: 'demo'
}
```

原始欄位對應：`Header → title`、`Source → source`、`Url → url`、`CreateTime → publishedAt`、`Content → content`。正式接入前需確認發布時間語意與時區。

## 既有資料與爬蟲檢查

四支爬蟲均通過 Python AST 語法解析；未重跑外部爬取。現有 CSV 共 3,884 筆。中央社有 1 筆空正文，工商時報有 1,774 筆正文剛好 200 字，財訊含僅剩「延伸閱讀：」的無效內容。

四支爬蟲尚無 `main` guard，不能直接 import 當作一般共用模組。這次僅新增前端，原始爬蟲與資料保持原樣。

## 本次驗證

- `npm run build`。
- 瀏覽器驗證搜尋、來源與情緒組合篩選、日期篩選與清除、分頁、空狀態。
- 新聞詳情、閱讀分頁與鍵盤切換、截斷內容提示。
- 收藏新增／移除、重新整理後保留。
- 公司切換、分析頁、CSV 匯出與深色模式。
- 手機導覽與 375 CSS px 版面；主要頁面無整頁水平溢位。

介面以 `cloth-reuse` 的白底橫向導覽、鼠尾草綠配色、圓角卡片與膠囊分類按鈕為主要參考，搭配文字與操作用線條圖示。
