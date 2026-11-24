<script setup>
import { computed, ref } from "vue";
import { shortDate } from "../services/newsService.js";
const props = defineProps({ articles: { type: Array, required: true } });
const selected = ref(null);
const days = computed(() => {
  const dates = [
    ...new Set(
      props.articles.map((article) => article.publishedAt.slice(0, 10))
    ),
  ].sort();
  return dates.map((date) => {
    const items = props.articles.filter((article) =>
      article.publishedAt.startsWith(date)
    );
    return {
      date,
      positive: items.filter((article) => article.sentiment === "positive")
        .length,
      neutral: items.filter((article) => article.sentiment === "neutral")
        .length,
      negative: items.filter((article) => article.sentiment === "negative")
        .length,
      total: items.length,
    };
  });
});
const max = computed(() => Math.max(...days.value.map((day) => day.total), 1));
</script>

<template>
  <div class="sentiment-chart">
    <div class="chart-grid" aria-label="各日展示新聞與情緒筆數">
      <div class="chart-guidelines" aria-hidden="true">
        <span></span><span></span><span></span>
      </div>
      <button
        v-for="day in days"
        :key="day.date"
        class="chart-column"
        :class="{ 'is-selected': selected === day.date }"
        type="button"
        :aria-label="`${day.date}，${day.total} 篇，正面 ${day.positive}，中性 ${day.neutral}，負面 ${day.negative}`"
        :aria-pressed="selected === day.date"
        @click="selected = selected === day.date ? null : day.date"
      >
        <span class="chart-count">{{ day.total }}</span
        ><span
          class="chart-bar"
          :style="{ height: `${(day.total / max) * 100}%` }"
          ><span class="chart-negative" :style="{ flex: day.negative }"></span
          ><span class="chart-neutral" :style="{ flex: day.neutral }"></span
          ><span
            class="chart-positive"
            :style="{ flex: day.positive }"
          ></span></span
        ><span class="chart-date">{{
          shortDate(day.date + "T12:00:00+08:00")
        }}</span>
      </button>
    </div>
    <div class="chart-legend">
      <span><i class="positive-dot"></i>正面</span
      ><span><i class="neutral-dot"></i>中性</span
      ><span><i class="negative-dot"></i>負面</span><small>單位：篇</small>
    </div>
    <p v-if="selected" class="chart-selected-note" role="status">
      {{ selected }}：正面
      {{ days.find((day) => day.date === selected)?.positive }} 篇、中性
      {{ days.find((day) => day.date === selected)?.neutral }} 篇、負面
      {{ days.find((day) => day.date === selected)?.negative }} 篇
    </p>
  </div>
</template>
