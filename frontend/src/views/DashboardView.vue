<script setup>
import { computed } from "vue";
import NewsCard from "../components/NewsCard.vue";
import SentimentChart from "../components/SentimentChart.vue";
import { notify, useWorkspace } from "../composables/useWorkspace.js";
import {
  companies,
  exportNews,
  shortDate,
  sources,
} from "../services/newsService.js";
import AppIcon from "../components/AppIcon.vue";

const { articles, savedIds } = useWorkspace();
const latest = articles.slice(0, 3);
const firstDate = articles.at(-1)?.publishedAt;
const lastDate = articles[0]?.publishedAt;
const keywordCounts = computed(() => {
  const counts = new Map();
  articles.forEach((article) =>
    article.keywords.forEach((word) =>
      counts.set(word, (counts.get(word) || 0) + 1)
    )
  );
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5);
});
const companyCounts = companies.map((company) => ({
  ...company,
  count: articles.filter((article) => article.companyIds.includes(company.id))
    .length,
}));
function download() {
  exportNews(articles);
  notify(`已匯出 ${articles.length} 篇展示新聞`);
}
</script>

<template>
  <section class="overview-hero" aria-labelledby="overview-title">
    <h1 id="overview-title">財經新聞總覽</h1>
    <p v-if="firstDate && lastDate">
      新聞樣本 <time :datetime="firstDate">{{ firstDate.slice(0, 4) }}/{{ shortDate(firstDate) }}</time> —
      <time :datetime="lastDate">{{ shortDate(lastDate) }}</time>
    </p>
    <RouterLink to="/news" class="button primary">探索新聞</RouterLink>
  </section>

  <dl class="overview-stats" aria-label="展示資料總覽">
    <div>
      <dt>新聞樣本</dt>
      <dd>{{ articles.length }} <small>篇</small></dd>
    </div>
    <div>
      <dt>新聞來源</dt>
      <dd>{{ sources.length }} <small>家</small></dd>
    </div>
    <div>
      <dt>觀測公司</dt>
      <dd>{{ companies.length }} <small>家</small></dd>
    </div>
    <div>
      <dt>我的收藏</dt>
      <dd>{{ savedIds.length }} <small>篇</small></dd>
    </div>
  </dl>

  <section class="overview-section" aria-labelledby="latest-title">
    <div class="section-heading">
      <h2 id="latest-title">最新新聞</h2>
      <div class="section-actions">
        <button class="text-link" type="button" @click="download">
          <AppIcon name="download" :size="16" />匯出整理
        </button>
        <RouterLink to="/news" class="text-link">查看全部</RouterLink>
      </div>
    </div>
    <div class="article-grid">
      <NewsCard
        v-for="article in latest"
        :key="article.id"
        :article="article"
      />
    </div>
  </section>

  <div class="overview-analysis">
    <section class="panel">
      <div class="panel-heading">
        <h2>新聞情緒分布</h2>
        <span class="tiny-demo">示範</span>
      </div>
      <SentimentChart :articles="articles" />
    </section>
    <section class="panel topics-panel">
      <div class="panel-heading">
        <h2>熱門關鍵詞</h2>
        <RouterLink to="/insights" class="text-link">查看分析</RouterLink>
      </div>
      <RouterLink
        v-for="[word, count] in keywordCounts"
        :key="word"
        :to="{ path: '/news', query: { q: word } }"
        class="topic-row"
      >
        <strong>{{ word }}</strong>
        <span class="topic-meter" aria-hidden="true">
          <i :style="{ width: `${(count / keywordCounts[0][1]) * 100}%` }"></i>
        </span>
        <span class="topic-count">{{ count }} 篇</span>
      </RouterLink>
      <p class="panel-footnote">依展示關鍵詞標籤統計</p>
    </section>
  </div>

  <section class="overview-section" aria-labelledby="company-title">
    <div class="section-heading">
      <h2 id="company-title">公司觀測</h2>
      <RouterLink to="/companies" class="text-link">查看全部</RouterLink>
    </div>
    <div class="company-strip">
      <RouterLink
        v-for="company in companyCounts"
        :key="company.id"
        :to="{ path: '/companies', query: { company: company.id } }"
        class="company-mini"
      >
        <span
          class="company-avatar"
          :class="company.color"
          aria-hidden="true"
          >{{ company.initials }}</span
        >
        <span>
          <strong>{{ company.name }}</strong>
          <small>{{ company.code }} · {{ company.count }} 篇</small>
        </span>
      </RouterLink>
    </div>
  </section>
</template>
