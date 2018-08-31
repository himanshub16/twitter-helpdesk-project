<template>
  <div>

  <router-view :key="$route.ticketId" />

  <!-- placing toolbar below router-view to avoid nav-drawer from showing above toolbar -->
  <v-toolbar
    app
    fixed
    clipped-left
    clipped-right
    >
    <router-link :to="{ name: 'dashboard', params: { screenName: screenName } }">
      <v-toolbar-title class="black--text no-decoration">
        {{ screenName }}
      </v-toolbar-title>
    </router-link>

    <v-spacer></v-spacer>
    <v-menu :nudge-width="100">
      <v-toolbar-title slot="activator">
        <span>{{ username }}</span>
        <v-icon>arrow_drop_down</v-icon>
      </v-toolbar-title>

      <v-list>
        <v-list-tile>
          <v-list-tile-title>Log out</v-list-tile-title>
        </v-list-tile>
      </v-list>
    </v-menu>
  </v-toolbar>


  </div>
</template>


<script>
export default {
  data() {
    return {
      displayName: 'Ola Supports',
      username: 'himanshub16',
    };
  },

  computed: {
    screenName: function() {
      return this.$route.params.screenName
    },
  },
};
</script>

<style scoped>
  a {
  text-decoration: none;
  }
</style>
