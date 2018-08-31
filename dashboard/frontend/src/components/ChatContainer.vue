<template>
<v-app>
  <v-list
    dense
    >
    <v-list-tile
      value="true"
      v-for="conv in conversations"
      :key="conv.id"
      >
      <v-list-tile-action>
        <v-icon v-html="conv.icon"></v-icon>
      </v-list-tile-action>
      <v-list-tile-content>
        <v-list-tile-title v-text="conv.title"></v-list-tile-title>
      </v-list-tile-content>
    </v-list-tile>
  </v-list>
</v-app>
</template>

<script>
export default {
  data() {
    return {
      conversations: [
        { icon: 'dashboard', title: 'first conversation' },
        { icon: 'dashboard', title: 'first conversation' },
        { icon: 'dashboard', title: 'first conversation' },
        { icon: 'dashboard', title: 'first conversation' },
        { icon: 'gavel', title: 'second conversation' },
        { icon: 'gavel', title: 'second conversation' },
        { icon: 'gavel', title: 'second conversation' },
        { icon: 'gavel', title: 'second conversation' },
      ],
    };
  },
};
</script>
