<script setup>
import { computed } from "vue";
import AppIcon from "../components/AppIcon.vue";
import SentimentChart from "../components/SentimentChart.vue";
import { useWorkspace } from "../composables/useWorkspace.js";
import { sources, sentimentLabels } from "../services/newsService.js";
const { articles } = useWorkspace();
const sentiments = ["positive", "neutral", "negative"].map((key) => ({
  key,
  label: sentimentLabels[key],
  count: articles.filter((article) => article.sentiment === key).length,
}));
const gradient = computed(() => {
  const first = (sentiments[0].count / articles.length) * 100;
  const second = first + (sentiments[1].count / articles.length) * 100;
  return `conic-gradient(var(--positive) 0 ${first}%, var(--neutral-chart) ${first}% ${second}%, var(--negative-chart) ${second}% 100%)`;
});
const keywords = computed(() => {
  const counts = new Map();
  articles.forEach((article) =>
    article.keywords.forEach((word) =>
      counts.set(word, (counts.get(word) || 0) + 1)
    )
  );
  return [...counts.entries()].sort((a, b) => b[1] - a[1]);
});
</script>

<template>
  <div class="page-heading">
    <h1>NLP 分析</h1>
    <p>展示樣本的情緒、關鍵詞與來源分布</p>
  </div>
  <div class="insights-grid">
    <section class="panel">
      <div class="panel-heading">
        <h2>各日新聞情緒</h2>
        <span class="panel-subtitle">11/17–11/21</span>
      </div>
      <SentimentChart :articles="articles" />
    </section>
    <section class="panel">
      <div class="panel-heading">
        <h2>整體情緒</h2>
        <span class="panel-subtitle">{{ articles.length }} 篇樣本</span>
      </div>
      <div class="donut-layout">
        <div
          class="sentiment-donut"
          :style="{ background: gradient }"
          role="img"
          :aria-label="
            sentiments
              .map((item) => `${item.label} ${item.count} 篇`)
              .join('，')
          "
        >
          <div>
            <strong>{{ articles.length }}</strong
            ><span>新聞樣本</span>
          </div>
        </div>
        <div class="sentiment-totals">
          <div v-for="item in sentiments" :key="item.key">
            <span class="sentiment-label"
              ><i :class="`${item.key}-dot`"></i>{{ item.label }}</span
            ><strong>{{ item.count }}<small> 篇</small></strong
            ><span
              >{{ Math.round((item.count / articles.length) * 100) }}%</span
            >
          </div>
        </div>
      </div>
    </section>
    <section class="panel">
      <div class="panel-heading">
        <h2>關鍵詞統計</h2>
        <span class="panel-subtitle">點選查看相關新聞</span>
      </div>
      <div class="keyword-cloud">
        <RouterLink
          v-for="[word, count] in keywords"
          :key="word"
          :to="{ path: '/news', query: { q: word } }"
          ><AppIcon name="tag" :size="15" />{{ word
          }}<span>{{ count }}</span></RouterLink
        >
      </div>
      <p class="panel-footnote">依展示標籤統計，未連接關鍵詞擷取模型。</p>
    </section>
    <section class="panel">
      <div class="panel-heading">
        <h2>新聞來源</h2>
        <span class="panel-subtitle">展示樣本</span>
      </div>
      <div class="source-list">
        <div v-for="source in sources" :key="source" class="source-row">
          <span>{{ source }}</span
          ><span class="source-bar"
            ><i
              :style="{
                width: `${
                  (articles.filter((article) => article.source === source)
                    .length /
                    articles.length) *
                  100
                }%`,
              }"
            ></i></span
          ><strong
            >{{ articles.filter((article) => article.source === source).length
            }}<small> 篇</small></strong
          >
        </div>
      </div>
    </section>
  </div>
  <p class="below-note">文字情緒不等同於股價方向；目前未提供行情預測。</p>
</template>
