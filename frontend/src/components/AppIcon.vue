<script setup>
defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 20 },
});

const paths = {
  grid: ["M3 3h7v7H3z", "M14 3h7v7h-7z", "M3 14h7v7H3z", "M14 14h7v7h-7z"],
  news: [
    "M4 4h13v16H4z",
    "M17 8h3v10a2 2 0 0 1-2 2",
    "M7 8h7",
    "M7 12h7",
    "M7 16h4",
  ],
  building: [
    "M5 21V5l7-2v18",
    "M12 8h7v13",
    "M3 21h18",
    "M8 7v1",
    "M8 11v1",
    "M8 15v1",
    "M15 11h1",
    "M15 15h1",
  ],
  chart: ["M4 3v17h17", "M8 15v-4", "M13 15V7", "M18 15V5"],
  bookmark: ["M6 4h12v17l-6-4-6 4z"],
  search: ["M21 21l-5-5", "M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0"],
  chevron: ["m9 5 7 7-7 7"],
  down: ["m6 9 6 6 6-6"],
  close: ["m6 6 12 12", "M6 18 18 6"],
  calendar: [
    "M5 5h14a1 1 0 0 1 1 1v14H4V6a1 1 0 0 1 1-1z",
    "M8 3v4",
    "M16 3v4",
    "M4 10h16",
    "M8 14h2",
    "M14 14h2",
  ],
  download: ["M12 3v12", "m7 10 5 5 5-5", "M4 16v5h16v-5"],
  globe: [
    "M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0",
    "M3 12h18",
    "M12 3a17 17 0 0 1 0 18 17 17 0 0 1 0-18",
  ],
  clock: ["M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0", "M12 7v5l3 2"],
  trend: ["m3 17 6-6 4 4 8-10", "M15 5h6v6"],
  spark: ["m12 3 2.4 6.6L21 12l-6.6 2.4L12 21l-2.4-6.6L3 12l6.6-2.4z"],
  filter: ["M4 6h16", "M7 12h10", "M10 18h4"],
  external: ["M14 3h7v7", "M21 3 11 13", "M10 4H4v16h16v-6"],
  help: [
    "M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0",
    "M9.1 9a3 3 0 1 1 5.2 2c-1.3.9-2.3 1.2-2.3 3",
    "M12 17h.01",
  ],
  moon: ["M20.5 13.1A8.8 8.8 0 0 1 10.9 3.5 9 9 0 1 0 20.5 13.1z"],
  sun: [
    "M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0",
    "M12 2v2",
    "M12 20v2",
    "M2 12h2",
    "M20 12h2",
    "m5 5 1.5 1.5",
    "M17.5 17.5 19 19",
    "M5 19l1.5-1.5",
    "M17.5 6.5 19 5",
  ],
  menu: ["M4 6h16", "M4 12h16", "M4 18h16"],
  check: ["m5 12 4 4L19 6"],
  layers: ["m12 3 10 6-10 6L2 9z", "m2 14 10 6 10-6"],
  text: ["M4 5h16", "M4 10h16", "M4 15h10", "M4 20h7"],
  tag: ["M3 3h8l10 10-8 8L3 11z", "M7 7h.01"],
  reset: ["M3 10a9 9 0 1 1 2 8", "M3 4v6h6"],
};
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.65"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path v-for="(d, index) in paths[name] || paths.news" :key="index" :d="d" />
  </svg>
</template>
