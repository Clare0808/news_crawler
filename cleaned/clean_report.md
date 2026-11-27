# 清洗報告

由 `python clean.py` 產生，不要手動修改。

| 來源   |   原始筆數 |   內容無效剔除 |   同來源重複剔除 |   保留 |   內文被截斷 |   時間為紙本預設值 |   清掉雜訊的篇數 |
|:-----|-------:|---------:|----------:|-----:|--------:|-----------:|----------:|
| 中央社  |    497 |        1 |         0 |  496 |       0 |          0 |       489 |
| 工商時報 |   1910 |        0 |        16 | 1894 |    1831 |        830 |       217 |
| 經濟日報 |    677 |        0 |         0 |  677 |       0 |          0 |       677 |
| 財訊   |    800 |        3 |         0 |  797 |       0 |          0 |       731 |

合計保留 3864 篇。不同來源刊出同一篇稿的有 39 組、80 篇，保留並標在 `DupGroup` 欄位。

## 各規則命中篇數

| 規則                |   篇數 |
|:------------------|-----:|
| wealth_read_more  |  718 |
| edn_word_count    |  677 |
| cna_dateline      |  484 |
| cna_editor_tail   |  324 |
| cna_photo_caption |  293 |
| wealth_reprint    |  206 |
| wealth_orig_title |  134 |
| cna_date_code     |  131 |
| ctee_dateline     |  115 |
| wealth_disclaimer |   92 |
| ctee_moneydj_tail |   73 |
| wealth_statement  |   36 |
| ctee_moneydj_head |   29 |
| edn_photo_caption |   17 |
| edn_copyright     |   13 |
| wealth_no_reprint |    4 |
